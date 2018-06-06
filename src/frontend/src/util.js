import qs from 'qs'
import md5 from 'js-md5'
import $ from 'jquery'

import conf from './conf'
import {MB} from './constant'

export async function calcMD5(file, onProgress) {
  onProgress = onProgress || (() => null);
  return await (new Hasher(file)).calcMD5(onProgress);
}

export class Hasher {
  constructor(file) {
    this.file = file;
    this.offset = 0;
    this.size = file.size;
    this.type = file.type;
  }

  read = async (size) => {
    return new Promise(resolve => {
      if (this.offset >= this.size) {
        resolve(null);
        return;
      }
      const fr = new FileReader();
      fr.onload = () => {
        this.offset += fr.result.byteLength;
        resolve(fr.result);
      }
      const start = this.offset;
      let blob = null;
      if (size) {
        blob = this.file.slice(start, start + size);
      } else {
        blob = this.file.slice(start);
      }
      fr.readAsArrayBuffer(blob);
    });
  }

  calcMD5 = async (onProgress) => {
    onProgress = onProgress || (() => null);
    const m = md5.create();
    onProgress(this.offset, this.size);
    while (true) {
      const data = await this.read(4 * MB);
      if (!data) break;
      onProgress(this.offset, this.size);
      m.update(data);
    }
    return m.hex();
  }
}

export async function headRes(path) {
  return await fetch(conf.api_origin + path, {
    method: 'HEAD',
  });
}

export async function fetchRes(path) {
  return await fetch(conf.api_origin + path);
}

export async function fetchMeta(path) {
  const res = await fetch(conf.api_origin + path + '?meta');
  return await res.json();
}

export async function fetchDir(path) {
  const params = qs.stringify({depth: 1});
  try {
    const res = await fetch(conf.api_origin + path + '?' + params);
    const data = await res.json();
    return data;
  } catch (e) {
    if (e instanceof TypeError) {
      console.log(`Fetch path ${path} failed`);
    } else {
      console.log(e);
    }
    throw new Error('exit');
  }
}

export async function fetchTransfer(path) {
  const res = await fetch(conf.api_origin + path + '?transfer');
  return await res.json();
}

export async function getJSON(path) {
  const res = await fetch(conf.api_origin + path);
  return await res.json();
}

export async function fetchJSON(method, path, data) {
  let url = conf.api_origin + path;
  const headers = new Headers();
  headers.append('Content-Type', 'application/json');
  const options = {
    method: method,
    headers: headers,
  };
  if (method === 'GET' || method === 'DELETE') {
    url += '?' + qs.stringify(data);
  } else {
    options.body = JSON.stringify(data);
  }
  const res = await fetch(url, options);
  return await res.json();
}

export function joinPaths(...paths) {
  let res = '';
  for (let path of paths) {
    if (!path) continue;
    if (path.startsWith('/')) {
      res = path;
    } else {
      const sep = (res.endsWith('/') || path.startsWith('/')) ? '' : '/';
      res += sep + path;
    }
  }
  return res;
}

export function splitBaseName(path) {
  let name = '';
  if (!path.endsWith('/')) {
    const parts = path.split('/');
    name = parts.pop();
    path = joinPaths(...parts);
  }
  return [path, name];
}

export function newName(existedNames) {
  const basename = 'noname';
  if (existedNames.indexOf(basename) === -1) {
    return basename;
  } else {
    for (let i = 2; ; ++i) {
      const name = basename + '' + i;
      if (existedNames.indexOf(name) === -1) {
        return name;
      }
    }
  }
}

export function openTab(path) {
  const a = $('<a>');
  a.attr('href', conf.origin + path);
  a.attr('target', '_blank');
  a.attr('rel', 'noopener noreferer');
  a.attr('style', 'display: none');
  $('body').append(a);
  a[0].click();
  a.remove();
}
