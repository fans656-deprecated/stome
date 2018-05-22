import conf from './conf';

export async function fetchDir(path) {
  const res = await fetch(conf.api_origin + path);
  const data = await res.json();
  return data;
}
