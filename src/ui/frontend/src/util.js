import qs from 'query-string'
import md5 from 'js-md5'

import conf from './conf'
import {MB} from './constant'

export class File {
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
      onProgress(this.offset, this.size);
      if (!data) break;
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

export async function fetchDir(path) {
  const params = qs.stringify({depth: 1});
  const res = await fetch(conf.api_origin + path + '?' + params);
  const data = await res.json();
  return data;
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
  let name = ''
  if (!path.endsWith('/')) {
    const parts = path.split('/');
    name = parts.pop();
    path = joinPaths(...parts);
  }
  return [path, name];
}
