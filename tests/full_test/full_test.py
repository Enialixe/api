from tests.unit.unit_tests import cases, calculate_key
import unittest
import requests
from store import Store
import json
import subprocess
import os
import signal
import time
import hashlib
import api
import datetime
import random

class Full_Test(unittest.TestCase):

    def setUp(self):
        api_dir = os.path.dirname(os.path.dirname(os.getcwd()))
        self.process = subprocess.Popen('python {dir}/api.py'.format(dir = api_dir),
                                        shell=True)
        time.sleep(5)
        self.store = Store()

    def tearDown(self):
        print(self.process.pid)
        os.kill(self.process.pid+1, signal.SIGINT)
        time.sleep(10)

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
    
    @cases([{"phone": 79175002040, "email": "stupnikov@otus.ru"}])
    def test_full_server_online_score(self, case):
        key = calculate_key(**case)
        self.store.database.set(key, 9)
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": case}
        self.set_valid_auth(request)
        headers = {'Content-Type': 'application/json'}
        data_json = json.dumps(request)
        resp = requests.post('http://127.0.0.1:8080/method', headers=headers, data=data_json)
        resp = json.loads(resp.text)
        print(resp)
        self.assertEqual((resp[u'code'], resp[u'responce'][u'score']), (200, 9))
        self.store.database.delete(key)

    @cases([{"client_ids": [1, 2, 3]}])
    def test_full_server_client_interests(self, case):
        const_interests = ["cars", "pets", "travel", "hi-tech", "sport", "music", "books",
                           "tv", "cinema", "geek", "otus"]
        interests_dict = {}
        for id_number in case["client_ids"]:
            id = 'i:'+str(id_number)
            interests = random.sample(const_interests, 2)
            interests = json.dumps(interests)
            interests_dict[str(id_number)] = json.loads(interests)
            self.store.database.set(id, interests)
        request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": case}
        self.set_valid_auth(request)
        headers = {'Content-Type': 'application/json'}
        data_json = json.dumps(request)
        resp = requests.post('http://127.0.0.1:8080/method', headers=headers, data=data_json)
        resp = json.loads(resp.text)
        self.assertEqual(resp['code'], 200)
        self.assertEqual(resp['responce'], interests_dict)
        for id_number in case["client_ids"]:
            id = 'i:' + str(id_number)
            self.store.database.delete(id)


if __name__ == "__main__":
    unittest.main()
