import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

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
        self.assertEqual(payload["verdict"], "SPEAK")
        self.assertEqual(completed.stderr, "")

    def test_admit_reads_json_from_file(self):
        completed = run_cli(["--input", str(FIXTURE_DIR / "pass.json")])

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["verdict"], "PASS")
        self.assertNotIn("reply", payload)

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
