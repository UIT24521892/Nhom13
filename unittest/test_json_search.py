import unittest

from recursive_json_search import json_search
from test_data import data, key1, key2


class JsonSearchTest(unittest.TestCase):
    def test_search_found(self):
        """Key có trong dữ liệu phải trả về kết quả."""
        self.assertNotEqual([], json_search(key1, data))

    def test_search_not_found(self):
        """Key không có trong dữ liệu phải trả về danh sách rỗng."""
        self.assertEqual([], json_search(key2, data))

    def test_is_a_list(self):
        """Kết quả tìm kiếm phải là list."""
        self.assertIsInstance(json_search(key1, data), list)


if __name__ == "__main__":
    unittest.main()
# Fill the Python code in this file
