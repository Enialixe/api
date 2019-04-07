import unittest
import api
from functools import wraps
import hashlib
import datetime
from store import Store
import time

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



class TestSuite(unittest.TestCase):

    def setUp(self):
        pass

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

    def test_declarative_method_request(self):

        class TestClass():
            __metaclass__ = api.DeclarativeMethodRequest
            a = int()
            b = str()
            c = dict()
            d = list()

        TestClass = TestClass()
        self.assertDictContainsSubset({'a': 0}, TestClass.__class__.__dict__)
        self.assertDictContainsSubset({'b': ''}, TestClass.__class__.__dict__)
        self.assertDictContainsSubset({'c': {}}, TestClass.__class__.__dict__)
        self.assertDictContainsSubset({'d': []}, TestClass.__class__.__dict__)

    @cases([{"requered": True, "nullable": False, "value": None, "field_type": api.Field, "exception": True},
           {"requered": False, "nullable": False, "value": None, "field_type": api.Field,"exception": False},
           {"requered": False, "nullable": False, "value": 0, "field_type": api.Field, "exception": True},
           {"requered": False, "nullable": False, "value": '', "field_type": api.Field, "exception": True},
           {"requered": False, "nullable": False, "value": {}, "field_type": api.Field, "exception": True},
            {"requered": False, "nullable": True, "value": 0, "field_type": api.Field, "exception": False},
            {"requered": False, "nullable": True, "value": '', "field_type": api.Field, "exception": False},
            {"requered": False, "nullable": True, "value": {}, "field_type": api.Field, "exception": False},
            {"requered": False, "nullable": True, "value": 'new_strig', "field_type": api.CharField,
             "exception": False},
            {"requered": False, "nullable": True, "value": 35, "field_type": api.CharField,
             "exception": True},
            {"requered": False, "nullable": True, "value": {"a":1}, "field_type": api.ArgumentsField,
             "exception": False},
            {"requered": False, "nullable": True, "value": "dict", "field_type": api.ArgumentsField,
             "exception": True},
            {"requered": False, "nullable": True, "value": "otus@otus.ru", "field_type": api.EmailField,
             "exception": False},
            {"requered": False, "nullable": True, "value": "otusotus.ru", "field_type": api.EmailField,
             "exception": True},
            {"requered": False, "nullable": True, "value": "70123456789", "field_type": api.PhoneField,
             "exception": False},
            {"requered": False, "nullable": True, "value": "7012345678", "field_type": api.PhoneField,
             "exception": True},
            {"requered": False, "nullable": True, "value": "701234567890", "field_type": api.PhoneField,
             "exception": True},
            {"requered": False, "nullable": True, "value": 70123456789, "field_type": api.PhoneField,
             "exception": False},
            {"requered": False, "nullable": True, "value": 7012345678, "field_type": api.PhoneField,
             "exception": True},
            {"requered": False, "nullable": True, "value": 701234567890, "field_type": api.PhoneField,
             "exception": True},
            {"requered": False, "nullable": True, "value": '7phonenumber', "field_type": api.PhoneField,
             "exception": True},
            {"requered": False, "nullable": True, "value": '25.03.1970', "field_type": api.DateField,
             "exception": False},
            {"requered": False, "nullable": True, "value": '25/03/1970', "field_type": api.DateField,
             "exception": True},
            {"requered": False, "nullable": True, "value": '25031970', "field_type": api.DateField,
             "exception": True},
            {"requered": False, "nullable": True, "value": 'data', "field_type": api.DateField,
             "exception": True},
            {"requered": False, "nullable": True, "value": '25.03.1970', "field_type": api.BirthDayField,
             "exception": False},
            {"requered": False, "nullable": True, "value": '25.03.1940', "field_type": api.BirthDayField,
             "exception": True},
            {"requered": False, "nullable": True, "value": '25/03/1970', "field_type": api.BirthDayField,
             "exception": True},
            {"requered": False, "nullable": True, "value": '25031970', "field_type": api.BirthDayField,
             "exception": True},
            {"requered": False, "nullable": True, "value": api.MALE, "field_type": api.GenderField,
             "exception": False},
            {"requered": False, "nullable": True, "value": api.FEMALE, "field_type": api.GenderField,
             "exception": False},
            {"requered": False, "nullable": True, "value": api.UNKNOWN, "field_type": api.GenderField,
             "exception": False},
            {"requered": False, "nullable": True, "value": -1, "field_type": api.GenderField,
             "exception": True},
            {"requered": False, "nullable": True, "value": 3, "field_type": api.GenderField,
             "exception": True},
            {"requered": False, "nullable": True, "value": 'male', "field_type": api.GenderField,
             "exception": True},
            {"requered": False, "nullable": True, "value": [3, 4, 5], "field_type": api.ClientIDsField,
             "exception": False},
            {"requered": False, "nullable": True, "value": (3, 4, 5), "field_type": api.ClientIDsField,
             "exception": False},
            {"requered": False, "nullable": True, "value": 3, "field_type": api.ClientIDsField,
             "exception": True},
            {"requered": False, "nullable": True, "value": ['3', '4', '5'], "field_type": api.ClientIDsField,
             "exception": True},
            ]
           )
    def test_field(self, case):

        class TestField():
            __metaclass__ = api.DeclarativeMethodRequest
            if case['field_type'] != api.ClientIDsField:
                field = case['field_type'](requred=case["requered"], nullable=case["nullable"])
            else:
                field = case['field_type'](requred=case["requered"])
            def __init__(self, value):
                self.field = value

        if case["exception"]:
            with self.assertRaises(api.ValidationError):
                TestField = TestField(case['value'])
        else:
            TestField = TestField(case["value"])
            if case['field_type'] == api.PhoneField and isinstance(case['value'], int):
                self.assertEqual(TestField.field, str(case["value"]))
            elif case['field_type'] == api.BirthDayField:
                self.assertEqual(TestField.field, datetime.datetime.strptime(case["value"], '%d.%m.%Y'))
            else:
                self.assertEqual(TestField.field, case["value"])

    @cases([{'req': {'value': 'h&s'}, 'err': None},
            {'req': {'value': 23}, 'err': ['Field value is not a string']},
            {'req': {'value': 'h', 'value_1': 'h&s'}, 'err': None},
            {'req':{'value': 23, 'value_1': 30}, 'err': ['Field value_1 is not a string',
                                                         'Field value is not a string']}])
    def test_request(self, case):

        class TestRequest(api.Request):
            for key in case['req'].keys():
                locals()[key] = api.CharField(requred=True, nullable=False)

        Request = TestRequest(case['req'])
        if not case['err']:
            for key in case['req'].keys():
                self.assertEqual(Request.__dict__[key], case['req'][key])
            self.assertEqual(Request.is_valid, (0, ''))
        else:
            self.assertEqual(Request.__dict__['errors'], case['err'])
            self.assertEqual(Request.is_valid, (api.INVALID_REQUEST, '\r\n'.join(case['err'])+'\r\n'))

    @cases([{"login": "horns&hoofs", 'is_admin': False},
            {"login": "admin", 'is_admin': True}])
    def test_method_request(self, case):

        Method = api.MethodRequest(case)
        self.assertEqual(Method.is_admin, case['is_admin'])

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
        print(api.method_handler(request, '', ''))
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
        self.set_valid_auth(body)
        request = {}
        request['body'] = body
        self.assertEqual(api.method_handler(request, '', ''), ('Two much null arguments', 422))

    @cases(
        [({"phone": "79324254528", "email": "stupnikov@otus.ru", "value": 3.5})])
    def test_cache_set(self, case):
        store = Store()
        key = calculate_key(phone = case['phone'])
        store.cache_set(key, case["value"], 30)
        print(store.cache)
        self.assertEqual(store.cache[key]['value'], case["value"])
        self.assertIsNotNone(store.cache[key]['time'])


    @cases(
        [({'phone': "79324254528", "value": 3},  {"phone": "79324254528", "value": 5})])
    def test_recache(self, value_1, value_2):
        store = Store()
        key = calculate_key(phone =value_1["phone"])
        store.cache_set(key, value_1["value"], 0)
        time.sleep(0.1)
        store.cache_set(key, value_2["value"], 5)
        self.assertEqual(store.cache_get(key), value_2["value"])

    @cases(
        [({"phone": "79324254528", "value": 3},  {"phone": "79324254528", "value": 5})])
    def test_cachedget_timeout(self, value_1, value_2):
        store = Store()
        key = calculate_key(phone=value_2["phone"])
        store.database.set(key, value_1["value"])
        store.cache_set(key, value_2, 0)
        time.sleep(0.1)
        print(store.cache_get(key))
        print(type(store.cache_get(key)))
        self.assertEqual(store.cache_get(key), value_1["value"])



if __name__ == "__main__":
    unittest.main()