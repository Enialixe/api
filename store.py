import redis
import datetime
import hashlib

class Store(object):

    def __init__(self):
        self.cache = {}
        self.connect(3)

    def connect(self, trys):
        for i in range(trys):
            try:
                self.database = redis.StrictRedis(socket_connect_timeout=10, socket_keepalive=60)
                return True
            except:
                continue
        return False

    def cache_get(self, key):
        if self.cache and self.cache.get(key):
            if datetime.datetime.now() < self.cache[key].get('time'):
                return self.cache[key]['value']
        user_record = self.get(key)
        if user_record:
            user_record = int(user_record)
        return user_record


    def get(self, request):
        conn_success = self.connect(3)
        user_record = None
        if conn_success:
            try:
                user_record = self.database.get(request)
            except:
                self.conn_succes = False
            if user_record:
                return user_record


    def cache_set(self, key, value, time):
        if self.cache.get(key):
            delta = datetime.datetime.now() - self.cache[key].get('time')
            if delta.seconds > 0:
                self.cache[key]['value'] = value
                self.cache[key]['time'] = datetime.datetime.now() + datetime.timedelta(seconds=time)
                return None
        self.cache[key] = {}
        self.cache[key]['value'] = value
        self.cache[key]['time'] = datetime.datetime.now() + datetime.timedelta(seconds=time)



if __name__ == "__main__":
    store = Store()
    key_parts = [
        "Jowndow",
        "Jowdows",
        "7999999999",
        "19910425",
    ]
    key = "uid:" + hashlib.md5("".join(key_parts)).hexdigest()
    #store.database.set(key, '9')
