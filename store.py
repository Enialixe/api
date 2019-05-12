import redis
import datetime
from functools import wraps
import time
import json
import logging
def retry(delay=3, backoff=2, throw_exception=True):
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = args[0].trys, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except Exception:
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            if throw_exception:
                return f(*args, **kwargs)
            else:
                try:
                    return f(*args, **kwargs)
                except Exception as E:
                    logging.exception(E)

        return f_retry
    return deco_retry

class Store(object):
    def __init__(self, host, port, local_port, timeout, keepalive, trys):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket_keepalive = keepalive
        self.trys = trys
        self.local_port = local_port
        self.database = redis.StrictRedis(host=self.host, port=self.port,
                                          socket_connect_timeout=self.timeout,
                                          socket_keepalive=self.socket_keepalive)
        self.cache_database = redis.StrictRedis(host='127.0.0.1', port=self.local_port)


    @retry()
    def set(self, key, value):
        self.database.set(key, value)

    @retry(throw_exception=False)
    def cache_get(self, key):
        record = self.cache_database.get(key)
        if record:
            record = json.loads(record)
            if datetime.datetime.now() < datetime.datetime.strptime(record['time'], '%d.%m.%Y %H:%M:%S',):
                return record['value']
        user_record = self.get(key)
        if user_record:
            user_record = int(user_record)
        return user_record


    @retry()
    def get(self, key):
        user_record = self.database.get(key)
        return user_record

    @retry(throw_exception=False)
    def cache_set(self, key, value, time):
        cache = self.cache_database.get(key)
        if cache:
            cache = json.loads(self.cache_database.get(key))
            delta = datetime.datetime.now() - datetime.datetime.strptime(cache.get('time'), '%d.%m.%Y %H:%M:%S')
            if delta.seconds > 0:
                return None
        cache = {}
        cache['value'] = value
        cache['time'] = datetime.datetime.now() + datetime.timedelta(seconds=time)
        cache['time'] = cache['time'].strftime('%d.%m.%Y %H:%M:%S')
        self.cache_database.set(key, json.dumps(cache))


if __name__ == "__main__":
    store = Store('127.0.0.1', '6379', '6370', 10, 10, 3)
    store.set('1', '[\"pets\", \"travel\", \"hi-tech\"]')
    res = store.get('2')
    print(res)
    print(json.loads(res))

