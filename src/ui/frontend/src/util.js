import qs from 'query-string';

import conf from './conf';

export async function fetchDir(path, depth) {
  //await new Promise((resolve) => setTimeout(resolve, 200));
  const args = qs.stringify({
    depth: depth || 1,
  });
  const res = await fetch(conf.api_origin + path + '?' + args);
  const data = await res.json();
  return data;
}

export async function fetchJSON(method, path, data) {
  let url = conf.api_origin + path;
  if (method === 'GET') {
    url += '?' + qs.stringify(data);
  }
  const res = await fetch(url);
  return await res.json();
}
