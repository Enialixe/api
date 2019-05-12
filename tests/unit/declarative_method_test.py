import unittest
import api

class DeclarativeMethodTest(unittest.TestCase):

    def setUp(self):
        pass


    def test_declarative_method_request(self):

        class TestClass(object):
            __metaclass__ = api.DeclarativeMethodRequest
            a = api.Field(required=True, nullable=False)
            b = api.Field(required=False, nullable=True)


        Test = TestClass()
        self.assertItemsEqual(['a', 'b'], Test.declarated_fields)
        self.assertEqual(Test.__class__.__dict__['a'].label, 'a')
        self.assertEqual(Test.__class__.__dict__['b'].label, 'b')

if __name__ == "__main__":
    unittest.main()
