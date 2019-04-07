from tests.unit.unit_tests import cases, calculate_key
import hashlib
from store import Store
import unittest
import api
import datetime
import random
import json


class IntegrationTestsSuit(unittest.TestCase):

    def setUp(self):
        self.context = {}
        self.headers = {}
        self.store = Store()

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

    @cases([{"first_name": "a", "last_name": "b"},
            {"phone": 79012345678, "email": "solar@otus.ru"},
            {'birthday': '02.03.1980', 'gender': 1},
            {"first_name": "a", "last_name": "b", "phone": 79012345678,
             'email': "solar@otus.ru", 'birthday': '02.03.1980', 'gender': 1}])
    def test_score_set_get_chache(self, case):
        key = calculate_key(**case)
        result = 0
        if case.get('phone'):
            result += 1.5
        if case.get('email'):
            result += 1.5
        if case.get('birthday') and case.get('gender'):
            result += 1.5
        if case.get('first_name') and case.get('last_name'):
            result += 0.5
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": case}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(self.store.cache[key]['value'], result)
        self.assertIsNotNone(self.store.cache[key]['time'])
        self.store.database.set(key, 9)
        response, code = self.get_response(request)
        self.assertEqual(response.get('score'), result)
        self.store.database.delete(key)

    @cases([{"client_ids": [1, 2, 3]}])
    def test_get_interests(self, case):
        const_interests = ["cars", "pets", "travel", "hi-tech", "sport", "music", "books",
                           "tv", "cinema", "geek", "otus"]
        interests_dict = {}
        for id_number in case["client_ids"]:
            id = 'i:'+str(id_number)
            interests = random.sample(const_interests, 2)
            interests = json.dumps(interests)
            interests_dict[id_number] = json.loads(interests)
            self.store.database.set(id, interests)
        request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": case}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(code, 200)
        self.assertEqual(response, interests_dict)




if __name__ == "__main__":
    unittest.main()