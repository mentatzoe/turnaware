import json
import unittest
from pathlib import Path

from turnaware import evaluate
from turnaware.models import FORBIDDEN_REPLY_FIELDS, VERDICTS

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


def load_fixture(name):
    with (FIXTURE_DIR / f"{name}.json").open(encoding="utf-8") as handle:
        return json.load(handle)


class CoreVerdictTests(unittest.TestCase):
    def test_evaluate_returns_expected_verdict_for_each_fixture(self):
        cases = {
            "pass": "PASS",
            "ack": "ACK",
            "ask": "ASK",
            "speak": "SPEAK",
        }

        for fixture_name, expected in cases.items():
            with self.subTest(fixture=fixture_name):
                result = evaluate(load_fixture(fixture_name))
                self.assertEqual(result["verdict"], expected)
                self.assertEqual(set(result["confidences"]), set(VERDICTS))
                self.assertTrue(result["reasons"])

    def test_pass_result_has_no_visible_reply_fields(self):
        result = evaluate(load_fixture("pass"))

        self.assertEqual(result["verdict"], "PASS")
        self.assertTrue(FORBIDDEN_REPLY_FIELDS.isdisjoint(result))

    def test_context_checked_stops_after_decisive_pass_context(self):
        result = evaluate(load_fixture("pass"))

        self.assertIn("trigger:trigger-pass", result["context_checked"])
        self.assertIn("context:ctx-pass-handled", result["context_checked"])
        self.assertNotIn("context:ctx-pass-later", result["context_checked"])


if __name__ == "__main__":
    unittest.main()
