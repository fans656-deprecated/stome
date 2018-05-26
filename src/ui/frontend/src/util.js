import qs from 'query-string';

import conf from './conf';

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
