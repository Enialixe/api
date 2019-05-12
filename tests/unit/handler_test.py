import unittest
import api
from field_test import cases
import hashlib
import datetime

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

class HandlerTest(unittest.TestCase):

    def setUp(self):
        return None

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

    @cases([
        {"account": "h&f", "method": "online_score", "arguments":{}},

    ])
    def test_method_handler_bad_request(self, case):
        request = {}
        request['body'] = case
        self.assertEqual(api.method_handler(request, '', ''),
                         ('Field token must be present\r\nField login must be present\r\n', 422))

    @cases([
        {"login": "user", "token": "sd", "account": "h&f", "method": "online_score", "arguments": {}},
        {"login": "admin", "token": "sd", "account": "h&f", "method": "online_score", "arguments": {}},
    ])
    def test_bad_auth(self, case):
        request = {}
        request['body'] = case
        self.assertEqual(api.method_handler(request, '', ''),
                         ('Forbidden', 403))

    @cases([{"login": "admin",  "account": "h&f",
             "method": "online_score", "arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru"}}])
    def test_admin_online_score(self, case):
        self.set_valid_auth(case)
        request = {}
        request['body'] = case
        self.assertEqual(api.method_handler(request, '', ''), ({'score': 42}, 200))

    @cases([{"login": "admin",  "account": "h&f",
             "method": "my_method", "arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru"}}])
    def test_wrong_method(self, case):
        self.set_valid_auth(case)
        request = {}
        request['body'] = case
        self.assertEqual(api.method_handler(request, '', ''), ('Wrong request method', 400))

    @cases([{"phone": "79175002040", "first_name": "a"},
             {"phone": "79175002040", "last_name": "a"},
            {"phone": "79175002040", "gender": 1},
            {"phone": "79175002040", "birthday": '25.11.1980'},
            {"email": "stupnikov@otus.ru", "first_name": "a"},
            {"email": "stupnikov@otus.ru", "first_name": "a", "birthday": '25.11.1980'}
            ])
    def test_online_score_request_null_fields(self, case):
        body = {"login": "user",  "account": "h&f",
             "method": "online_score", "arguments": case}

        class Store():
            def cache_get(self, key):
                return None

            def cache_set(self, key, value, time):
                return None

        store = Store()
        self.set_valid_auth(body)
        request = {}
        request['body'] = body
        self.assertEqual(api.method_handler(request, {}, store), ('Two much null arguments', 422))

if __name__ == "__main__":
    unittest.main()


