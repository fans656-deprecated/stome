import qs from 'query-string'

import conf from './conf'

const parts = conf.origin.split(':');
if (parts.length > 2) parts.pop();
parts.push('' + conf.api_port);
const api_origin = parts.join(':');

async function post(path, args, data) {
  return await request('POST', path, args, data);
}

async function request(method, path, args, data) {
  let url = api_origin + path;

  const params = {};
  // extract params from path
  if (url.indexOf('?') !== -1) {
    const parts = url.split('?');
    Object.assign(params, qs.parse(parts.pop()));
    url = parts.join('?');
  }
  Object.assign(params, args);
  const query = qs.stringify(params);
  if (query) url += '?' + query;

  const headers = new Headers();
  headers.append('Content-Type', 'application/json');

  const options = {
    method: method,
    headers: headers,
    body: data ? JSON.stringify(data) : '',
  };

  const res = await fetch(url, options);
  return await res.json();
}

const api = {
  post: post,
};

export default api;
