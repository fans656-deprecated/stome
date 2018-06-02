import _ from 'lodash';

import {
  headRes, fetchDir, fetchMeta, fetchTransfer, fetchJSON
} from './util';
import watch from './watch'

/**
 * Make a tree rooted at given path, e.g.
 *
 *   getTree('/')
 *   getTree('/home/fans656')
 *
 * @param {string} path - The path of tree's root node
 */
export async function getTree(path, ui) {
  const root = new Node(await fetchDir(path));
  const tree = new Tree(root, ui);
  return tree;
}
export default getTree;

export class Node {
  /**
   * @param {object} meta - Meta info got by e.g. GET http://res.eno.zone/home
   * @param {Node} parent - This node's parent node, nullable for root
   * @param {Tree} tree - This node's tree, not null
   */
  constructor(meta, parent, tree) {
    this.meta = meta;
    this.parent = parent;
    this.tree = tree;
    this.children = [];
    this.loaded = false;
  }

  /**
   * Return whether this node has sub-directories
   */
  hasSubDirs = () => {
    return this.dirs && this.dirs.length > 0;
  }

  /**
   * Return whether this node is tree's current dir
   */
  isCurrentDir = () => {
    return this === this.tree.currentDir;
  }

  /**
   * Return whether this node is tree's current (selected) item
   */
  isCurrentItem = () => {
    return this === this.tree.currentItem;
  }

  addFileChild = (node) => {
    if (!this.loaded) this._load();
    this.files.push(node);
  }

  findChildByName = (name) => {
    return this.children.find(f => f.meta.name === name);
  }

  /**
   * Collapse this node if `toggled` === false else uncollapse
   * @param {Boolean} toggled - false for collapse, true for uncollapse
   */
  toggle = async (toggled) => {
    if (!this.loaded) this._load();
    for (let dir of this.dirs) await dir._load();
    this.toggled = toggled == null ? !this.toggled : toggled;
  }

  /**
   * Update node's info and descendants' structure.
   */
  update = async (recursive) => {
    if (this.meta.listable) {
      this.meta = await fetchDir(this.meta.path);
      if (this.loaded) {
        await this._updateStructure();
      } else {
        await this._load();
      }
      if (recursive) {
        this.children.forEach(c => c.update(recursive));
      }
    } else {
      this.meta = await fetchMeta(this.meta.path);
    }
    this.tree.ui.update();
  }

  updateParent = async () => {
    const parent = this.parent;
    if (parent) {
      await parent.update();
      await parent.updateParent();
    }
  }

  /*
   * Delete this node (and its children if this is a dir)
   */
  delete = async () => {
    if (this.listable) {
      for (let child of this.children) {
        await child.delete();
      }
    }
    await fetchJSON('DELETE', this.meta.path);
    await this.updateParent();
  }

  /**
   * Find node by path, starting from root.
   * Call `callback` at every match node with the node as argument.
   * @param {Function} callback - 
   */
  findByPath = async (path, callback) => {
    if (!path) return null;
    const lastFoundNode = await this._findByPathNames(path.split('/'), callback);
    if (lastFoundNode && lastFoundNode.meta.path === path) {
      return lastFoundNode;
    } else {
      return null;
    }
  }

  onHashProgress = (offset, size) => {
    const percent = offset / size * 100;
    this.transfer.hashProgress = percent;
    const done = offset === size;
    if (done) {
      //console.log(this);
      //watch(this._watchUntilNodeCreatedOnRemote);
    }
    this.tree.ui.update();
  }

  _watchUntilNodeCreatedOnRemote = async () => {
    const meta = this.meta;
    const res = await headRes(meta.path);
    if (res.status === 200) {
      this.transfer.status = 'uploading';
      this.transfer.progress = 0;
      await this.update();
      watch(this._watchUntilNodeUploaded);
      return true;
    }
  }

  _watchUntilNodeUploaded = async () => {
    const meta = await fetchTransfer(this.meta.path);
    const unreceived = _.sum(meta.unreceived.map(([b, e]) => e - b));
    const total = meta.size;
    if (unreceived === 0) {
      delete this.transfer;
      await this.update();
      return true;
    }
    this.transfer.progress = (total - unreceived) / total * 100;
    await this.update();
  }

  _findByPathNames = async (names, callback) => {
    if (this.meta.name !== names[0]) return null;  // this node is not on path

    if (!this.loaded) await this._load();

    const isLast = names.length === 1;
    if (callback) await callback(this, isLast);
    if (isLast) return this;  // found last

    if (this.meta.listable) {
      names = names.splice(1);
      for (let child of this.children) {
        const node = await child._findByPathNames(names, callback);
        if (node) return node;
      }
    }
    return null;
  }

  _load = async () => {
    if (this.loaded) return;
    if (this.meta.listable) {
      this.dirs = await this._makeDirNodes();
      this.files = this._makeFileNodes();
      this.children = this.dirs.concat(this.files);
    }
    this.loaded = true;
  }

  _updateStructure = async () => {
    const pathToChild = {};
    this.children.forEach(child => pathToChild[child.meta.path] = child);
    this.dirs = await Promise.all(
      this.meta.dirs.map(meta => (
        pathToChild[meta.path] || this._makeDirNode(meta)
      ))
    );
    this.files = this.meta.files.map(meta => (
      pathToChild[meta.path] || this._makeFileNode(meta)
    ));
    this.children = this.dirs.concat(this.files);
  }

  _makeDirNodes = async () => {
    return await Promise.all(this.meta.dirs.map(this._makeDirNode));
  }

  _makeDirNode = async (meta) => {
    return new Node(await fetchDir(meta.path), this, this.tree)
  }

  _makeFileNodes = () => {
    return this.meta.files.map(this._makeFileNode);
  }

  _makeFileNode = (meta) => {
    return new Node(meta, this, this.tree);
  }
}

class Tree {
  constructor(root, ui) {
    this.root = root;
    this.ui = ui;
    this.currentDir = null;
    this.currentItem = null;
    root.tree = this;
  }

  /**
   * Set tree's current directory by path
   * Uncollapse directories along from root
   */
  setCurrentPath = async (path) => {
    let lastFoundNode = null;
    await this.root.findByPath(path, async (node) => {
      lastFoundNode = node;
      await node.toggle(true);
    });
    this.setCurrentDir(lastFoundNode);
    return lastFoundNode;
  }

  /**
   * Set tree's current directory by node
   */
  setCurrentDir = (node) => {
    this.currentDir = node;
  }

  setCurrentItem = (node) => {
    this.currentItem = node;
  }

  findByPath = async (path) => {
    if (path === '/') return this.root;
    return await this.root.findByPath(path);
  }
}
