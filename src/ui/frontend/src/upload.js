import qs from 'query-string'
import $ from 'jquery'

import conf from './conf'
import {File} from './util'

export default async function upload(path, file, callbacks) {
  const onHashProgress = callbacks.onHashProgress || (() => null);

  file = new File(file);
  const md5 = await file.calcMD5(onHashProgress);

  if (file.size <= conf.chunk_size) {
    await _upload(path, file.file, {
      md5: md5,
      size: file.size,
    });
  } else {
    for (let offset = 0; offset < file.size; offset += conf.chunk_size) {
      const blob = file.file.slice(offset, offset + conf.chunk_size, file.type);
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
  return;
  return new Promise(resolve => {
    $.ajax({
      method: 'PUT',
      url: conf.api_origin + path + '?' + qs.stringify(args),
      contentType: file.type,
      data: file,
      processData: false,
      success: () => {
        resolve(null);
      }
    });
  });
}
