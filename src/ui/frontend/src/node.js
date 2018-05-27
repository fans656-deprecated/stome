import { fetchDir, fetchJSON } from './util';

/**
 * Make a tree rooted at given path, e.g.
 *
 *   getTree('/')
 *   getTree('/home/fans656')
 *
 * @param {string} path - The path of tree's root node
 */
export default async function getTree(path) {
  const root = new Node(await fetchDir(path));
  const tree = new Tree(root);
  return tree;
}

class Node {
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
    this.loaded = !meta.listable;
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
  update = async () => {
    this.meta = await fetchDir(this.meta.path);
    if (!this.loaded) {
      this._load();
    } else {
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
    if (!path) return;
    return this._findByPathNames(path.split('/'), callback);
  }

  _findByPathNames = async (names, callback) => {
    const pathEndReached = names.length === 0;
    const notOnPath = this.meta.name !== names[0];

    if (pathEndReached) return null;
    if (notOnPath) return null;

    if (!this.loaded) await this._load();
    const last = names.length === 1;
    if (callback) await callback(this, last);

    names = names.splice(1);

    let ret = this;
    for (let child of this.dirs) {
      ret = await child._findByPathNames(names, callback) || ret;
    }
    return ret;
  }

  _load = async () => {
    if (this.loaded) return;
    this.dirs = await this._makeDirNodes();
    this.files = this._makeFileNodes();
    this.children = this.dirs.concat(this.files);
    this.loaded = true;
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
  constructor(root) {
    this.root = root;
    this.currentDir = null;
    this.currentItem = null;
    root.tree = this;
  }

  /**
   * Set tree's current directory by path
   * Uncollapse directories along from root
   */
  setCurrentPath = async (path) => {
    const node = await this.root.findByPath(path, async (node, last) => {
      await node.toggle(true);
    });
    this.setCurrentDir(node);
    return node;
  }

  /**
   * Set tree's current directory by node
   */
  setCurrentDir = (node) => {
    this.currentDir = node;
  }

  findByPath = async (path) => {
    return await this.root.findByPath(path);
  }
}
