import * as qiniu from 'qiniu-js'

import api from '../api'


export default async function qiniuUpload(config) {
  await new QiniuUpload(config).start();
}

class QiniuUpload {
  constructor(config) {
    this.node = config.node;
    this.content = this.node.meta.contents.find(c => c.type === 'qiniu');
    this.storage_id = this.content.storage_id;
    this.md5 = config.md5;
    this.file = config.file;
  }

  start = async () => {
    const {chunks} = await this.getUploadConfig();
    this.node.startUpload();
    let loaded = 0;
    const onNewLoaded = (newLoaded) => {
      loaded += newLoaded;
      this.node.onUploadProgress(loaded, this.file.size);
    };
    for (let chunk of chunks) {
      chunk.loaded = 0;
      chunk.blob = await this.getEncryptedBlob(chunk);
      chunk.token = await this.getUploadToken(chunk);
      await this.doUpload(chunk, onNewLoaded);
    }
    this.finishUpload();
  }

  getUploadConfig = async () => {
    return await api.contentQuery(this, {
      'op': 'prepare-upload',
      'size': this.file.size,
    });
  }

  getEncryptedBlob = async (chunk) => {
    const blob = this.file.slice(chunk.offset, chunk.offset + chunk.size);
    const reader = new FileReader();
    const data = await new Promise((resolve) => {
      reader.onload = () => {
        resolve(reader.result);
      }
      reader.readAsArrayBuffer(blob);
    });
    const a = new Uint8Array(data);
    for (let i = 0; i < a.length; ++i) {
      a[i] = ~a[i];
    }
    return new Blob([a], {
      size: a.length,
      type: 'application/octet-stream',
    });
  }

  getUploadToken = async (chunk) => {
    const {token} = await api.contentQuery(this, {
      'op': 'get-upload-token',
      'path': chunk.path,
    });
    return token;
  }

  doUpload = async (chunk, onNewLoaded) => {
    await new Promise(resolve => {
      const observable = qiniu.upload(
        chunk.blob, chunk.path, chunk.token, {}, {}
      );
      observable.subscribe({
        next: ({total}) => {
          // qiniu upload chunk total is larger than actual blob size
          const loaded = (chunk.size * total.percent / 100).toFixed(0);
          const diff = loaded - chunk.loaded;
          chunk.loaded = total.loaded;
          onNewLoaded(diff);
        },
        error: (err) => {
          console.log('error', {
            'chunk': chunk,
            'err': err,
          });
          resolve(err);
        },
        complete: (res) => {
          resolve(res);
        },
      });
    });
  }

  finishUpload = async () => {
    await api.put('/?content', null, {
      'md5': this.md5,
      'storage_id': this.storage_id,
      'status': 'done',
    });
    await this.node.finishUpload();
  }
}
