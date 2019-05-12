import unittest
import api
from functools import wraps
import datetime

def cases(cases):
    def decorator(f):
        @wraps(f)
        def wrapper(*args):
            for case in cases:
                new_args = args + (case if isinstance(case, tuple) else (case,))
                f(*new_args)
        return wrapper
    return decorator


class SimpleFieldTests(unittest.TestCase):

    def setUp(self):
        pass

    @cases([{"requered": True, "nullable": False, "value": None},
            {"requered": False, "nullable": False, "value": 0},
            {"requered": False, "nullable": False, "value": ''},
            {"requered": False, "nullable": False, "value": {}},
            ]
           )
    def test_field_exception(self, case):

        class TestField():
            __metaclass__ = api.DeclarativeMethodRequest
            field = api.Field(required=case["requered"], nullable=case["nullable"])

            def __init__(self, value):
                for field in self.__class__.__dict__['declarated_fields']:
                    self.__setattr__(field, value)

        with self.assertRaises(api.ValidationError):
            TestField = TestField(case['value'])

    @cases([{"requered": False, "nullable": False, "value": None},
            {"requered": False, "nullable": True, "value": 0},
            {"requered": False, "nullable": True, "value": ''},
            {"requered": False, "nullable": True, "value": {}},
            ]
           )
    def test_field_good(self, case):

        class TestField():
            __metaclass__ = api.DeclarativeMethodRequest
            field = api.Field(required=case["requered"], nullable=case["nullable"])

            def __init__(self, value):
                for field in self.__class__.__dict__['declarated_fields']:
                    self.__setattr__(field, value)

        TestField = TestField(case["value"])
        self.assertEqual(TestField.field, case["value"])


class CharFieldTest(unittest.TestCase):

    def setUp(self):
        pass

    @cases([{"requered": False, "nullable": True, "value": 35},
            ])
    def test_field_exception(self, case):
        class TestField():
            __metaclass__ = api.DeclarativeMethodRequest
            field = api.CharField(required=case["requered"], nullable=case["nullable"])

            def __init__(self, value):
                for field in self.__class__.__dict__['declarated_fields']:
                    self.__setattr__(field, value)

        with self.assertRaises(api.ValidationError):
            TestField = TestField(case['value'])

    @cases([{"requered": False, "nullable": True, "value": 'new_strig'},
            ])
    def test_field_good(self, case):

        class TestField():
            __metaclass__ = api.DeclarativeMethodRequest
            field = api.CharField(required=case["requered"], nullable=case["nullable"])

            def __init__(self, value):
                for field in self.__class__.__dict__['declarated_fields']:
                    self.__setattr__(field, value)

        TestField = TestField(case["value"])
        self.assertEqual(TestField.field, case["value"])

    class ArgumentsFieldTest(unittest.TestCase):

        def setUp(self):
            pass

        @cases([{"requered": False, "nullable": True, "value": "dict"},
                ])
        def test_field_exception(self, case):
            class TestField():
                __metaclass__ = api.DeclarativeMethodRequest
                field = api.ArgumentsField(required=case["requered"], nullable=case["nullable"])

                def __init__(self, value):
                    for field in self.__class__.__dict__['declarated_fields']:
                        self.__setattr__(field, value)

            with self.assertRaises(api.ValidationError):
                TestField = TestField(case['value'])

        @cases([{"requered": False, "nullable": True, "value": {"a": 1}},
                ])
        def test_field_good(self, case):
            class TestField():
                __metaclass__ = api.DeclarativeMethodRequest
                field = api.ArgumentsField(required=case["requered"], nullable=case["nullable"])

                def __init__(self, value):
                    for field in self.__class__.__dict__['declarated_fields']:
                        self.__setattr__(field, value)

            TestField = TestField(case["value"])
            self.assertEqual(TestField.field, case["value"])

    class EmailFieldTest(unittest.TestCase):

        def setUp(self):
            pass

        @cases([{"requered": False, "nullable": True, "value": "otusotus.ru"},
                ])
        def test_field_exception(self, case):
            class TestField():
                __metaclass__ = api.DeclarativeMethodRequest
                field = api.EmailField(required=case["requered"], nullable=case["nullable"])

                def __init__(self, value):
                    for field in self.__class__.__dict__['declarated_fields']:
                        self.__setattr__(field, value)

            with self.assertRaises(api.ValidationError):
                TestField = TestField(case['value'])

        @cases([{"requered": False, "nullable": True, "value": "otus@otus.ru"},
                ])
        def test_field_good(self, case):
            class TestField():
                __metaclass__ = api.DeclarativeMethodRequest
                field = api.EmailField(required=case["requered"], nullable=case["nullable"])

                def __init__(self, value):
                    for field in self.__class__.__dict__['declarated_fields']:
                        self.__setattr__(field, value)

            TestField = TestField(case["value"])
            self.assertEqual(TestField.field, case["value"])

    class PhoneFieldTest(unittest.TestCase):

        def setUp(self):
            pass

        @cases([{"requered": False, "nullable": True, "value": "7012345678"},
                {"requered": False, "nullable": True, "value": "701234567890"},
                {"requered": False, "nullable": True, "value": '7phonenumber'},
                {"requered": False, "nullable": True, "value": 701234567890},
                {"requered": False, "nullable": True, "value": 7012345678},
                ])
        def test_field_exception(self, case):
            class TestField():
                __metaclass__ = api.DeclarativeMethodRequest
                field = api.PhoneField(required=case["requered"], nullable=case["nullable"])

                def __init__(self, value):
                    for field in self.__class__.__dict__['declarated_fields']:
                        self.__setattr__(field, value)

            with self.assertRaises(api.ValidationError):
                TestField = TestField(case['value'])

        @cases([{"requered": False, "nullable": True, "value": "70123456789"},
                ])
        def test_field_good_string(self, case):
            class TestField():
                __metaclass__ = api.DeclarativeMethodRequest
                field = api.PhoneField(required=case["requered"], nullable=case["nullable"])

                def __init__(self, value):
                    for field in self.__class__.__dict__['declarated_fields']:
                        self.__setattr__(field, value)

            TestField = TestField(case["value"])
            self.assertEqual(TestField.field, case["value"])

        @cases([{"requered": False, "nullable": True, "value": 79167948639},
                ])
        def test_field_good_int(self, case):
            class TestField():
                __metaclass__ = api.DeclarativeMethodRequest
                field = api.PhoneField(required=case["requered"], nullable=case["nullable"])

                def __init__(self, value):
                    for field in self.__class__.__dict__['declarated_fields']:
                        self.__setattr__(field, value)

            TestField = TestField(case["value"])
            self.assertEqual(TestField.field, str(case["value"]))

    class DateFieldTest(unittest.TestCase):

        def setUp(self):
            pass

        @cases([{"requered": False, "nullable": True, "value": '25/03/1970'},
                {"requered": False, "nullable": True, "value": '25031970'},
                {"requered": False, "nullable": True, "value": 'data'},
                ])
        def test_field_exception(self, case):
            class TestField():
                __metaclass__ = api.DeclarativeMethodRequest
                field = api.DateField(required=case["requered"], nullable=case["nullable"])

                def __init__(self, value):
                    for field in self.__class__.__dict__['declarated_fields']:
                        self.__setattr__(field, value)

            with self.assertRaises(api.ValidationError):
                TestField = TestField(case['value'])

        @cases([{"requered": False, "nullable": True, "value": '25.03.1970'},
                ])
        def test_field_good(self, case):
            class TestField():
                __metaclass__ = api.DeclarativeMethodRequest
                field = api.DateField(required=case["requered"], nullable=case["nullable"])

                def __init__(self, value):
                    for field in self.__class__.__dict__['declarated_fields']:
                        self.__setattr__(field, value)

            TestField = TestField(case["value"])
            self.assertEqual(TestField.field, case["value"])

    class BirthdayFieldTest(unittest.TestCase):

        def setUp(self):
            pass

        @cases([{"requered": False, "nullable": True, "value": '25.03.1940'},
                {"requered": False, "nullable": True, "value": '25/03/1970'},
                {"requered": False, "nullable": True, "value": '25031970'}
                ])
        def test_field_exception(self, case):
            class TestField():
                __metaclass__ = api.DeclarativeMethodRequest
                field = api.BirthDayField(required=case["requered"], nullable=case["nullable"])

                def __init__(self, value):
                    for field in self.__class__.__dict__['declarated_fields']:
                        self.__setattr__(field, value)

            with self.assertRaises(api.ValidationError):
                TestField = TestField(case['value'])

        @cases([{"requered": False, "nullable": True, "value": '25.03.1970'},
                ])
        def test_field_good(self, case):
            class TestField():
                __metaclass__ = api.DeclarativeMethodRequest
                field = api.BirthDayField(required=case["requered"], nullable=case["nullable"])

                def __init__(self, value):
                    for field in self.__class__.__dict__['declarated_fields']:
                        self.__setattr__(field, value)

            TestField = TestField(case["value"])
            self.assertEqual(TestField.field, datetime.datetime.strptime(case["value"], '%d.%m.%Y'))

    class GenderFieldTest(unittest.TestCase):

        def setUp(self):
            pass

        @cases([{"requered": False, "nullable": True, "value": -1},
                {"requered": False, "nullable": True, "value": 3},
                {"requered": False, "nullable": True, "value": 'male'},
                ])
        def test_field_exception(self, case):
            class TestField():
                __metaclass__ = api.DeclarativeMethodRequest
                field = api.GenderField(required=case["requered"], nullable=case["nullable"])

                def __init__(self, value):
                    for field in self.__class__.__dict__['declarated_fields']:
                        self.__setattr__(field, value)

            with self.assertRaises(api.ValidationError):
                TestField = TestField(case['value'])

        @cases([{"requered": False, "nullable": True, "value": api.MALE},
                {"requered": False, "nullable": True, "value": api.FEMALE},
                {"requered": False, "nullable": True, "value": api.UNKNOWN},
                ])
        def test_field_good(self, case):
            class TestField():
                __metaclass__ = api.DeclarativeMethodRequest
                field = api.GenderField(required=case["requered"], nullable=case["nullable"])

                def __init__(self, value):
                    for field in self.__class__.__dict__['declarated_fields']:
                        self.__setattr__(field, value)

            TestField = TestField(case["value"])
            self.assertEqual(TestField.field, case["value"])

    class ClientIDsField(unittest.TestCase):

        def setUp(self):
            pass

        @cases([{"requered": False, "nullable": True, "value": 3},
                {"requered": False, "nullable": True, "value": ['3', '4', '5']},
                ])
        def test_field_exception(self, case):
            class TestField():
                __metaclass__ = api.DeclarativeMethodRequest
                field = api.GenderField(required=case["requered"], nullable=case["nullable"])

                def __init__(self, value):
                    for field in self.__class__.__dict__['declarated_fields']:
                        self.__setattr__(field, value)

            with self.assertRaises(api.ValidationError):
                TestField = TestField(case['value'])

        @cases([{"requered": False, "nullable": True, "value": [3, 4, 5]},
                {"requered": False, "nullable": True, "value": (3, 4, 5)},
                ])
        def test_field_good(self, case):
            class TestField():
                __metaclass__ = api.DeclarativeMethodRequest
                field = api.GenderField(required=case["requered"], nullable=case["nullable"])

                def __init__(self, value):
                    for field in self.__class__.__dict__['declarated_fields']:
                        self.__setattr__(field, value)

            TestField = TestField(case["value"])
            self.assertEqual(TestField.field, case["value"])

if __name__ == "__main__":
    unittest.main()