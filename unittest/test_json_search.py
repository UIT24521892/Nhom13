import unittest

from recursive_json_search import json_search
from test_data import data, key1, key2


class JsonSearchTest(unittest.TestCase):
    def test_search_found(self):
        self.assertNotEqual([], json_search(key1, data))

    def test_search_not_found(self):
        self.assertEqual([], json_search(key2, data))

    def test_is_a_list(self):
        self.assertIsInstance(json_search(key1, data), list)

    def test_viewer_cannot_read_api_key(self):
        self.assertEqual([], json_search("apiKey", data, role="viewer"))

    def test_viewer_cannot_read_management_ip(self):
        self.assertEqual([], json_search("managementIpAddress", data, role="viewer"))

    def test_operator_cannot_read_api_key(self):
        self.assertEqual([], json_search("apiKey", data, role="operator"))

    def test_admin_can_read_api_key(self):
        self.assertNotEqual([], json_search("apiKey", data, role="admin"))

    def test_parent_object_does_not_leak_secrets(self):
        result = json_search("deviceDetails", data, role="viewer")
        self.assertTrue(result)
        self.assertNotIn("apiKey", result[0]["deviceDetails"])
        self.assertNotIn("managementIpAddress", result[0]["deviceDetails"])


if __name__ == "__main__":
    unittest.main()
