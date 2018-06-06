import qs from 'qs'

import conf from '../conf'
import { Hasher } from '../util'

export default async function upload(path, file, callbacks) {
  const onHashProgress = callbacks.onHashProgress || (() => null);

  const hasher = new Hasher(file);
  const md5 = await hasher.calcMD5(onHashProgress);

  if (file.size <= conf.chunk_size) {
    _upload(path, file, {
      md5: md5,
      size: file.size,
    });
  } else {
    for (let offset = 0; offset < file.size; offset += conf.chunk_size) {
      const blob = file.slice(offset, offset + conf.chunk_size, file.type);
      _upload(path, blob, {
        md5: md5,
        size: file.size,
        'chunk-offset': offset,
        'chunk-md5': await new File(blob).calcMD5(),
      });
    }
  }
}

async function _upload(path, file, args) {
  const headers = new Headers();
  headers.append('Content-Type', file.type);
  await fetch(conf.api_origin + path + '?' + qs.stringify(args), {
    method: 'PUT',
    headers: headers,
    body: file,
  });
}
