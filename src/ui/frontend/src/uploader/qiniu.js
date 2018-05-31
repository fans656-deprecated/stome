//import qiniu from 'qiniu-js'
import { getJSON } from '../util'


export default async function qiniuUpload(meta) {
  const res = await getJSON('/?storage=qiniu&op=get-upload-token');
  console.log(res);
  console.log(meta);
}
