import { fetchDir } from './util';

export default async function getTree(path) {
  const tree = new Tree();
  const meta = await fetchDir(path);
  const root = new Node(meta, null, tree);
  tree.root = root;
  return tree;
}

class Node {
  constructor(meta, parent, tree) {
    this.meta = meta;
    this.parent = parent;
    this.tree = tree;
  }

  hasSubDirs = () => {
    return this.dirs && this.dirs.length > 0;
  }

  isCurrentDir = () => {
    return this === this.tree.currentDir;
  }

  isCurrentItem = () => {
    return this === this.tree.currentItem;
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
      this.dirs = await this._loadSubdirs(meta.dirs);
      this.files = meta.files.map(meta => new Node(meta, this, this.tree));
      this.children = this.dirs.concat(this.files);
    }
  }

  update = async (recursive) => {
    this.meta = await fetchDir(this.meta.path);
    if (recursive && this.children) {
      for (let child of this.children) {
        await child.update(recursive)
      }
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

  _loadSubdirs = async (metas) => {
    return await Promise.all(
      metas.map(async (meta) => {
        meta = await fetchDir(meta.path);
        return await new Node(meta, this, this.tree);
      })
    );
  }
}

class Tree {
  constructor() {
    this.root = null;
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
