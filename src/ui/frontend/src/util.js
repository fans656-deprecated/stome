import conf from './conf';

export async function getListDirectoryResults(path) {
  const res = await fetch(conf.api_origin + path);
  const data = await res.json();
  return data;
  /*
  console.log(data);
  if (path === '/') {
    return {
      dirs: [
        {
          name: 'home',
          path: '/home',
          type: 'dir',
        },
        {
          name: 'public',
          path: '/public',
          type: 'dir',
        },
      ],
      files: [
        {
          name: '.conf',
          path: '/public/.conf',
          type: 'file',
        }
      ],
    };
  } else if (path === '/home') {
    return {
      dirs: [
        {
          name: 'fans656',
          path: '/home/fans656',
          type: 'dir',
        },
        {
          name: 'tyn',
          path: '/home/tyn',
          type: 'dir',
        },
      ],
      files: [],
    };
  } else if (path === '/public') {
    return {
      dirs: [],
      files: [
        {
          name: 'girl.jpg',
          path: '/public/girl.jpg',
          type: 'file',
        }
      ],
    };
  } else {
    return {
      dirs: [],
      files: [],
    };
  }
  */
}
