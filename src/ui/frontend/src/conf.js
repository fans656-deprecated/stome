const origin = window.location.origin;
const parts = origin.split(':');
if (parts.length > 2) {
  parts.pop();
}
const api_origin = parts.join(':') + ':6001';

const conf = {
  api_origin: api_origin,
}

export default conf;
