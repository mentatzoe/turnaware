import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from tests.test_core import load_fixture
from turnaware import evaluate

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "tests" / "fixtures"


def run_cli(args=None, stdin=None):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    cmd = [sys.executable, "-m", "turnaware", "admit"]
    if args:
        cmd.extend(args)
    return subprocess.run(
        cmd,
        cwd=ROOT,
        env=env,
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


class CliTests(unittest.TestCase):
    def test_admit_reads_json_from_stdin_and_writes_success_json(self):
        fixture = (FIXTURE_DIR / "speak.json").read_text(encoding="utf-8")

        completed = run_cli(stdin=fixture)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["classifier"], "product")
        self.assertEqual(payload["verdict"], "SPEAK")
        self.assertEqual(completed.stderr, "")

    def test_admit_reads_json_from_file(self):
        completed = run_cli(["--classifier", "deterministic", "--input", str(FIXTURE_DIR / "pass.json")])

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["classifier"], "deterministic")
        self.assertEqual(payload["verdict"], "PASS")
        self.assertNotIn("reply", payload)

    def test_cli_classifier_overrides_envelope_classifier(self):
        completed = run_cli(["--classifier", "product", "--input", str(FIXTURE_DIR / "speak_cli_precedence.json")])

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["classifier"], "product")
        self.assertEqual(payload["verdict"], "SPEAK")

    def test_cli_classifier_config_json_is_used(self):
        completed = run_cli([
            "--classifier",
            "deterministic",
            "--classifier-config",
            '{"strict": true}',
            "--input",
            str(FIXTURE_DIR / "speak.json"),
        ])

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["classifier"], "deterministic")

    def test_cli_and_core_are_contract_equivalent_for_fixture_set(self):
        fixture_names = (
            "pass",
            "ack",
            "ask",
            "speak",
            "false_ack_comment_back",
            "false_pass_contradicted_done",
            "false_pass_no_corroboration",
        )
        for fixture_name in fixture_names:
            with self.subTest(fixture=fixture_name):
                completed = run_cli(["--classifier", "deterministic", "--input", str(FIXTURE_DIR / f"{fixture_name}.json")])
                self.assertEqual(completed.returncode, 0, completed.stderr)
                cli_payload = json.loads(completed.stdout)
                core_payload = evaluate(load_fixture(fixture_name), classifier="deterministic")
                self.assertEqual(cli_payload, core_payload)

    def test_invalid_classifier_fails_without_success_stdout(self):
        completed = run_cli(["--classifier", "does-not-exist", "--input", str(FIXTURE_DIR / "speak.json")])

        self.assertEqual(completed.returncode, 3)
        self.assertEqual(completed.stdout, "")
        self.assertIn("unsupported classifier", completed.stderr.lower())

    def test_malformed_json_fails_as_input_error(self):
        completed = run_cli(stdin="{not json")

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertIn("input error", completed.stderr.lower())

    def test_missing_trigger_fails_as_validation_error(self):
        completed = run_cli(stdin="{}")

        self.assertEqual(completed.returncode, 3)
        self.assertEqual(completed.stdout, "")
        self.assertIn("validation error", completed.stderr.lower())

    def test_missing_input_file_fails_as_input_error(self):
        completed = run_cli(["--input", str(FIXTURE_DIR / "missing.json")])

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertIn("input error", completed.stderr.lower())


if __name__ == "__main__":
    unittest.main()
