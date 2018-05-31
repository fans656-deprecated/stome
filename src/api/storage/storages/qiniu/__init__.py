import store


template = {
    'type': 'qiniu',
    'name': 'qiniu',
    'domain': 'p7a4nj2zt.bkt.clouddn.com',
    'bucket': 'eno.zone',
    'access-key': 'g_O72_____your-access-key____q4hYSz',
    'secret-key': 'zvn5N_____your-secret-key____dKla51',
}


class StorageInstanceQiniu(store.instance.Instance):

    def init(self):
        self.update_meta({
            'foo': 'bar',
        })

Instance = StorageInstanceQiniu
