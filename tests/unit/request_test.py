import unittest
import api
from field_test import cases

class RequestTests(unittest.TestCase):

    def setUp(self):
        pass

    @cases([{'value': 'h&s'},
            {'value': 'h', 'value_1': 'h&s'},
            ])
    def test_request_good(self, case):
        class TestRequest(api.Request):
            for key in case['req'].keys():
                locals()[key] = api.CharField(required=True, nullable=False)

        Request = TestRequest(case)
        for key in case.keys():
            self.assertEqual(Request.__dict__[key], case[key])
        self.assertEqual(Request.is_valid, True)


    @cases([{'req': {'value': 23}, 'err': ['Field value is not a string']},
            {'req': {'value': 23, 'value_1': 30}, 'err': ['Field value_1 is not a string',
                                                      'Field value is not a string']}])
    def test_request_good(self, case):
        class TestRequest(api.Request):
            for key in case['req'].keys():
                locals()[key] = api.CharField(required=True, nullable=False)

        Request = TestRequest(case['req'])
        self.assertEqual(Request.__dict__['errors'], case['err'])
        self.assertEqual(Request.is_valid, False)


    @cases([{"login": "horns&hoofs", 'is_admin': False},
            {"login": "admin", 'is_admin': True}])
    def test_admin_method_request(self, case):
        Method = api.MethodRequest(case)
        self.assertEqual(Method.is_admin, case['is_admin'])


if __name__ == "__main__":
    unittest.main()