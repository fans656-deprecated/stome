import {MB} from './constant'

const origin = window.location.origin;
const api_port = 6001;
const parts = origin.split(':');
if (parts.length > 2) parts.pop();
parts.push('' + api_port);
const api_origin = parts.join(':');

const conf = {
  origin: origin,
  api_origin: api_origin,
  chunk_size: 1 * MB,
  api_port: api_port,
}

export default conf;
