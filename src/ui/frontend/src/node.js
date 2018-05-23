import { fetchDir } from './util';

export default async function getRootDir(path) {
  const meta = await fetchDir(path);
  const node = new Node(meta);
  return node;
}

class Node {
  constructor(meta, parent) {
    this.meta = meta;
    this.parent = parent || null;
  }

  getDescendant = async (path) => {
    if (!path) return;
    if (!this.children) this.loadChildren();
  }

  loadChildren = () => {
    if (this.children) return;
    const meta = this.meta;
    this.dirs = meta.dirs.map((dir) => new Node(dir, this));
    this.files = meta.files.map((file) => new Node(file, this));
    this.children = this.dirs.concat(this.files);
    this.loaded = true;
  }
}

async function getDescendant(node, path) {
  if (!path) return;
  return await _getDescendant(node, path.split('/'));
}

async function _getDescendant(node, names) {
  if (names.length === 0 || node.meta.name !== names[0]) return;
  if (!node.children) await node.loadChildren();
  names = names.splice(1);
  let ret = node;
  if (names.length > 0) {
    for (let child of node.children) {
      ret = await _getDescendant(child, names) || ret;
    }
  }
  return ret;
}
