import unittest

from tests.test_core import load_fixture
from turnaware import evaluate
from turnaware.errors import ValidationError
from turnaware.models import FORBIDDEN_REPLY_FIELDS, VERDICTS
from turnaware.schema import validate_request, validate_result


class SchemaTests(unittest.TestCase):
    def test_success_result_schema_has_verdict_confidences_context_and_reasons(self):
        result = evaluate(load_fixture("speak"))
        validated = validate_result(result)

        self.assertIs(validated, result)
        self.assertIn(result["verdict"], VERDICTS)
        self.assertEqual(set(result["confidences"]), set(VERDICTS))
        self.assertIsInstance(result["context_checked"], list)
        self.assertGreaterEqual(len(result["context_checked"]), 1)
        self.assertIsInstance(result["reasons"], list)
        self.assertTrue(result["reasons"])

    def test_success_result_contains_no_reply_composition_fields(self):
        for fixture_name in ("pass", "ack", "ask", "speak"):
            with self.subTest(fixture=fixture_name):
                result = evaluate(load_fixture(fixture_name))
                self.assertTrue(FORBIDDEN_REPLY_FIELDS.isdisjoint(result))

    def test_context_checked_references_only_request_items(self):
        request = load_fixture("pass")
        result = evaluate(request)
        allowed = {"trigger:trigger-pass", "context:ctx-pass-handled", "context:ctx-pass-later"}

        self.assertLess(set(result["context_checked"]), allowed)
        self.assertNotIn("context:missing", result["context_checked"])

    def test_missing_trigger_is_validation_error(self):
        with self.assertRaises(ValidationError):
            validate_request({"context": []})

    def test_duplicate_context_ids_are_validation_error(self):
        request = load_fixture("pass")
        request["context"][1]["id"] = request["context"][0]["id"]

        with self.assertRaises(ValidationError):
            validate_request(request)


if __name__ == "__main__":
    unittest.main()
