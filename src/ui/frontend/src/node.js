import { fetchDir } from './util';

export default async function getTree(path) {
  const tree = new Tree(await getRootByPath(path));
  Node.tree = tree;
  return tree;
}

async function getRootByPath(path) {
  const meta = await fetchDir(path);
  const node = new Node(meta);
  return node;
}

class Node {
  constructor(meta, parent) {
    this.meta = meta;
    this.parent = parent || null;
  }

  hasSubDirs = () => {
    return this.dirs && this.dirs.length > 0;
  }

  isCurrentDir = () => {
    return this === Node.tree.currentDir;
  }

  isCurrentItem = () => {
    return this === Node.tree.currentItem;
  }

  toggle = async (toggled) => {
    this.toggled = toggled == null ? !this.toggled : toggled;
    for (let dir of this.dirs) await dir.loadChildren();
  }

  findByPath = async (path, callback) => {
    if (!path) return;
    return this._findByPathNames(path.split('/'), callback);
  }

  loadChildren = async () => {
    const meta = this.meta;
    if (meta.listable && !this.children) {
      this.dirs = await this._loadChildren(meta.dirs);
      this.files = await this._loadChildren(meta.files);
      this.children = this.dirs.concat(this.files);
    }
  }

  _findByPathNames = async (names, callback) => {
    if (names.length === 0) return null;
    if (this.meta.name !== names[0]) return null;
    if (!this.children) await this.loadChildren();
    if (callback) await callback(this);
    let ret = this;
    names = names.splice(1);
    if (this.dirs) {
      for (let child of this.dirs) {
        ret = await child._findByPathNames(names, callback) || ret;
      }
    }
    return ret;
  }

  _loadChildren = async (metas) => {
    return await Promise.all(
      metas.map(async (meta) => {
        meta = await fetchDir(meta.path);
        return await new Node(meta, this);
      })
    );
  }
}

class Tree {
  constructor(root) {
    this.root = root;
    this.currentDir = null;
    this.currentItem = null;
  }

  setCurrentPath = async (path) => {
    const currentDir = await this.root.findByPath(path, async (node) => {
      for (let dir of node.dirs) await dir.loadChildren();
      node.toggled = true;
    });
    this.setCurrentDir(currentDir);
  }

  setCurrentDir = (node) => {
    this.currentDir = node;
  }
}
