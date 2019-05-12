from functools import wraps
import hashlib
from store import Store
import unittest
import api
import datetime
import random
import json

def cases(cases):
    def decorator(f):
        @wraps(f)
        def wrapper(*args):
            for case in cases:
                new_args = args + (case if isinstance(case, tuple) else (case,))
                f(*new_args)
        return wrapper
    return decorator

def calculate_key(**kwargs):
    key_parts = [
        kwargs['first_name'] if kwargs.get('first_name') else "",
        kwargs['last_name'] if kwargs.get('last_name') else "",
        str(kwargs['phone']) if  kwargs.get('phone') else "",
        datetime.datetime.strptime(kwargs['birthday'],("%d.%m.%Y")).strftime("%Y%m%d")
        if kwargs.get('birthday') else "",
    ]
    key = "uid:" + hashlib.md5("".join(key_parts)).hexdigest()
    return key

class IntegrationTestsSuit(unittest.TestCase):

    def setUp(self):
        self.context = {}
        self.headers = {}
        self.store = Store('127.0.0.1', '6379', '6370', 10, 10, 3)
        client_ids = [1, 2, 3]
        const_interests = ["cars", "pets", "travel", "hi-tech", "sport", "music", "books",
                           "tv", "cinema", "geek", "otus"]
        self.interests_dict = {}
        for id_number in client_ids:
            id = 'i:'+str(id_number)
            interests = random.sample(const_interests, 2)
            interests = json.dumps(interests)
            self.interests_dict[id_number] = json.loads(interests)
            self.store.database.set(id, interests)

    def get_admin_token(self, request):
        request["token"] = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT).hexdigest()

    def get_user_token(self, request):
        try:
            msg = request.get("account", "") + request.get("login", "") + api.SALT
        except TypeError:
            msg = str(request.get("account", "")) + str(request.get("login", "")) + api.SALT
        request["token"] = hashlib.sha512(msg).hexdigest()

    def set_valid_auth(self, request):
        if request.get('login') == 'admin':
            self.get_admin_token(request)
        else:
            self.get_user_token(request)

    def get_response(self, request):
        return api.method_handler({"body": request, "headers": self.headers}, self.context, self.store)

    @cases([{"phone": 79175002040, "email": "stupnikov@otus.ru"}])
    def test_score_request_store(self, case):
        key = calculate_key(**case)
        self.store.database.set(key, 9)
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": case}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual((code, response.get('score')), (200, 9))
        self.store.database.delete(key)

    @cases([{"first_name": "a", "last_name": "b", "result": 0.5},
            {"phone": 79012345678, "email": "solar@otus.ru", "result": 3},
            {'birthday': '02.03.1980', 'gender': 1, "result": 1.5},
            {"first_name": "a", "last_name": "b", "phone": 79012345678,
             'email': "solar@otus.ru", 'birthday': '02.03.1980', 'gender': 1, "result": 5}])
    def test_score_set_get_chache(self, case):
        key = calculate_key(**case)
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": case}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(json.loads(self.store.cache_database.get(key))['value'], case['result'])
        self.assertIsNotNone(json.loads(self.store.cache_database.get(key))['time'])
        self.store.set(key, 9)
        response, code = self.get_response(request)
        self.assertEqual(response.get('score'), case['result'])

    @cases([{"client_ids": [1, 2, 3]}])
    def test_get_interests(self, case):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": case}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(code, 200)
        self.assertEqual(response, self.interests_dict)


if __name__ == "__main__":
    unittest.main()