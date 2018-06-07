const api_origin = 'https://ub:6001';

const url2config = {};

self.addEventListener('install', (ev) => {
  self.skipWaiting();
});

self.addEventListener('message', (ev) => {
  const msg = ev.data;
  const op = msg.op;
  if (op === 'add-download-config') {
    const meta = msg.meta;
    const urlAndConfig = getClientDownloadConfig(meta, msg.origin);
    if (urlAndConfig) {
      const {url, config} = urlAndConfig;
      url2config[url] = config;
    }
  }
  ev.ports[0].postMessage(true);
});

self.addEventListener('fetch', async (ev) => {
  const request = ev.request;
  if (maybeFileDownload(request)) {
    let url = decodeURI(request.url);
    ev.respondWith(new Promise(async (resolve) => {
      let res = null;
      if (url in url2config) {
        const {meta, content} = url2config[url];
        res = getResponse(meta, content);
      } else {
        const path = getNodePath(url);
        try {
          res = await getResponseByPath(path);
        } catch (e) {
          res = fetch(url, {
            headers: {'X-Pass-Through-Service-Worker': true}
          });
        }
      }
      resolve(res);
    }));
  }
});

function maybeFileDownload(request) {
  if (request.headers.hasOwnProperty('X-Pass-Through-Service-Worker')) {
    return false;
  }
  if (request.method !== 'GET') return false;
  const url = request.url;
  if (url.indexOf('?') !== -1) return false;
  const path = getNodePath(url);
  if (path.startsWith('/static/')) return false;
  return true;
}

function getClientDownloadConfig(meta, origin) {
  const content = meta.contents.find(
    c => c.type === 'qiniu' && c.status === 'done'
  );
  if (content) {
    return {
      url: origin + meta.path,
      config: {meta: meta, content, content},
    };
  }
}

async function getResponseByPath(path) {
  const meta = await getNodeMeta(path);
  const content = await getQiniuContent(meta);
  return getResponse(meta, content);
}

function getResponse(meta, content) {
  return new Response(getStream(content), {
    headers: {
      'Content-Type': meta.mimetype,
      'Content-Length': meta.size,
    }
  });
}

function getNodePath(url) {
  return '/' + url.split('/').slice(3).join('/').split('?')[0];
}

async function getNodeMeta(path) {
  const res = await fetch(api_origin + path + '?op=meta');
  return await res.json();
}

async function getQiniuContent(meta) {
  return meta.contents.find(c => c.type === 'qiniu');
}

function getStream(content) {
  const stream = new ReadableStream({
    start: async (controller) => {
      for (let chunk of content.chunks) {
        const url = await getDownloadUrl(content, chunk);
        await enqueueChunkData(controller, url);
      }
      controller.close();
    }
  });
  return stream;
}

async function getDownloadUrl(content, chunk) {
  const headers = makeFetchHeaders();
  const res = await fetch(
    api_origin + '/?op=content-query', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({
        op: 'get-download-url',
        md5: content.md5,
        storage_id: content.storage_id,
        path: chunk.path,
      })
    }
  );
  return (await res.json()).url;
}

async function enqueueChunkData(controller, url) {
  const res = await fetch(url);
  const reader = res.body.getReader();
  while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    invertBytes(value);
    controller.enqueue(value);
  }
}

function makeFetchHeaders() {
  const headers = new Headers();
  headers.append('Content-Type', 'application/json');
  return headers;
}

function invertBytes(bytes) {
  for (let i = 0; i < bytes.length; ++i) {
    bytes[i] = ~bytes[i];
  }
}
