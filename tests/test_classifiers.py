import unittest

from tests.test_core import load_fixture
from turnaware import evaluate
from turnaware.classifiers import SUPPORTED_CLASSIFIERS
from turnaware.errors import ValidationError


class ClassifierTests(unittest.TestCase):
    def test_registry_supports_product_default_and_deterministic_evidence_paths(self):
        self.assertIn("product", SUPPORTED_CLASSIFIERS)
        self.assertIn("deterministic", SUPPORTED_CLASSIFIERS)

    def test_false_ack_comment_back_is_speak_not_ack(self):
        for classifier in ("product", "deterministic"):
            with self.subTest(classifier=classifier):
                result = evaluate(load_fixture("false_ack_comment_back"), classifier=classifier)
                self.assertEqual(result["classifier"], classifier)
                self.assertEqual(result["verdict"], "SPEAK")
                self.assertNotEqual(result["verdict"], "ACK")
                self.assertIn("context:ctx-false-ack-assignment", result["context_checked"])

    def test_false_pass_contradicted_done_is_not_pass_and_checks_contradiction(self):
        for classifier in ("product", "deterministic"):
            with self.subTest(classifier=classifier):
                result = evaluate(load_fixture("false_pass_contradicted_done"), classifier=classifier)
                self.assertEqual(result["classifier"], classifier)
                self.assertNotEqual(result["verdict"], "PASS")
                self.assertIn("context:ctx-false-pass-missing-work", result["context_checked"])
                self.assertIn("contradicted", " ".join(result["reasons"]).casefold())

    def test_no_corroborating_context_does_not_become_high_confidence_pass(self):
        result = evaluate(load_fixture("false_pass_no_corroboration"), classifier="deterministic")

        self.assertEqual(result["verdict"], "ASK")
        self.assertLess(result["confidences"]["PASS"], result["confidences"]["ASK"])

    def test_legitimate_pass_remains_reachable_with_corroborating_context(self):
        result = evaluate(load_fixture("pass"), classifier="deterministic")

        self.assertEqual(result["verdict"], "PASS")
        self.assertIn("context:ctx-pass-handled", result["context_checked"])

    def test_unsupported_classifier_fails_without_fallback(self):
        with self.assertRaises(ValidationError):
            evaluate(load_fixture("speak"), classifier="does-not-exist")


if __name__ == "__main__":
    unittest.main()
