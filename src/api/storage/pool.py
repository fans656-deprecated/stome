import multiprocessing


def get():
    return Pool()


class Pool(object):

    def __init__(self):
        pass

    def run(self, key, target, *args, **kwargs):
        p = multiprocessing.Process(target=target, args=args, kwargs=kwargs)
        p.daemon = True
        p.start()
