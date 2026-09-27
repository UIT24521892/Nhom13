"""Functional and security tests for recursive JSON search."""

import unittest

from recursive_json_search import json_search
from test_data import data, key1, key2


class TestJsonSearch(unittest.TestCase):
    def test_searches_nested_dict_and_list(self):
        """Find matching fields nested in dictionaries inside lists."""
        results = json_search(key1, data)
        self.assertEqual(len(results), 1)
        self.assertIn("Unreachable", results[0])

    def test_searches_arbitrary_key(self):
        """Return an empty list when a key does not occur in the input."""
        self.assertEqual(json_search(key2, data), [])

    def test_aggregates_all_matching_values(self):
        """Collect every occurrence of a key throughout nested containers."""
        sample = {"entry": {"target": 1}, "items": [{"target": 2}, [ {"target": 3} ]]}
        self.assertEqual(json_search("target", sample), [1, 2, 3])

    def test_viewer_cannot_read_api_key(self):
        """Deny direct access to the admin-only API key for viewers."""
        self.assertEqual(json_search("apiKey", data, role="viewer"), [])

    def test_viewer_cannot_read_management_address(self):
        """Deny direct access to the management address for viewers."""
        self.assertEqual(json_search("managementIpAddress", data, role="viewer"), [])

    def test_parent_result_is_redacted_for_viewer(self):
        """Remove protected descendants when returning a parent object."""
        result = json_search("deviceDetails", data, role="viewer")
        self.assertEqual(len(result), 1)
        self.assertNotIn("apiKey", result[0])
        self.assertNotIn("managementIpAddress", result[0])

    def test_missing_role_defaults_to_viewer_access(self):
        """Apply viewer-level restrictions when no role is supplied."""
        self.assertEqual(json_search("apiKey", data), [])
        self.assertTrue(json_search("issueSummary", data))


if __name__ == "__main__":
    unittest.main()
