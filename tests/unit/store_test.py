import store
import unittest
from field_test import cases
import hashlib
import json

def calculate_key(key_parts):
    key = "uid:" + hashlib.md5("".join(key_parts)).hexdigest()
    return key

class StoreTest(unittest.TestCase):

    def setUp(self):
        self.store = store.Store('127.0.0.1', '6379', '6370', 10, 10, 3)
        key_parts = [
            "Jowndow",
            "Jowdows",
            "7999999999",
            "19910425",
        ]
        self.key = calculate_key(key_parts)
        self.value = 10
        self.store.database.delete('1')
        self.store.database.delete('2')
        self.store.cache_database.delete(self.key)
        self.store.set(calculate_key(key_parts), 10)
        self.store.set('1', '[\"pets\",\"travel\",\"hi-tech\"]')
        self.store.set('2', '[\"books\",\"music\"]')

    @cases([
        {"key":'1', "value":'[\"pets\", \"travel\", \"hi-tech\"]', "result": [u'pets', u'travel', u'hi-tech']},
        {"key": '2', "value": '[\"books\",\"music\"]', "result": [u'books', u'music']}
    ])
    def test_store_exist_get(self, case):
        self.assertEqual(json.loads(self.store.get(case['key'])), case['result'])

    def test_store_not_exist_get(self):
        self.assertEqual(self.store.get('3'), None)

    def test_store_exist_cache_get(self):
        self.assertEqual(self.store.cache_get(self.key), self.value)

    def test_store_cache_get_not_exist(self):
        self.assertEqual(self.store.cache_get('5'), None)

    def test_store_cache_set(self):
        self.store.cache_set(self.key, 5, 1)
        self.assertEqual(self.store.cache_get(self.key), 5)

    def test_store_get_timeout(self):
        self.store = store.Store('127.0.0.1', '1', '6370', 10, 10, 3)
        with self.assertRaises(Exception):
            self.store.get('1')
        self.store = store.Store('127.0.0.1', '6379', '6370', 10, 10, 3)

    def test_store_cache_get_timeout(self):
        self.store = store.Store('127.0.0.1', '6367', '1', 10, 10, 3)
        self.assertEqual(self.store.cache_get(self.key), None)
        self.store = store.Store('127.0.0.1', '6379', '6370', 10, 10, 3)

if __name__ == "__main__":
    unittest.main()





