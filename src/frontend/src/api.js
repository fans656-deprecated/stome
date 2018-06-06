import qs from 'qs'

import conf from './conf'

const parts = conf.origin.split(':');
if (parts.length > 2) parts.pop();
parts.push('' + conf.api_port);
const api_origin = parts.join(':');

const api = {
  ls: async (path) => {
    try {
      const res = await fetch(conf.api_origin + path + '?op=ls');
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
  },

  get: async (path, args) => {
    return await api.request('GET', path, args);
  },

  put: async (path, args, data) => {
    return await api.request('PUT', path, args, data);
  },

  post: async (path, args, data) => {
    return await api.request('POST', path, args, data);
  },

  delete_: async (path) => {
    return await api.request('DELETE', path);
  },

  contentQuery: async (content, data) => {
    data = Object.assign(data, {
      md5: content.md5,
      storage_id: content.storage_id,
    });
    return await api.request('POST', '/?op=content-query', null, data);
  },

  request: async (method, path, args, data) => {
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
    };
    if (data) {
      options.body = JSON.stringify(data);
    }

    const res = await fetch(url, options);
    return await res.json();
  },
};

export default api;
