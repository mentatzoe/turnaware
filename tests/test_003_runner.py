"""Self-tests for the verdict test suite runner.

These exercise loader correctness, report shape, the adapter contract, and
the --mock-adapter-output flag. They do NOT exercise the actual fixtures —
that is what the runner does. Self-tests run in milliseconds.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_SPEC_CONTRACTS = (
    Path(__file__).resolve().parent.parent
    / "specs"
    / "003-classifier-test-suite"
    / "contracts"
)
if str(_SPEC_CONTRACTS) not in sys.path:
    sys.path.insert(0, str(_SPEC_CONTRACTS))

import adapters  # noqa: E402
import loader  # noqa: E402
import report  # noqa: E402
import runner  # noqa: E402

FIXTURES_ROOT = _SPEC_CONTRACTS / "fixtures"


def test_loader_discovers_all_fixtures_and_validates_pairs():
    fixtures = loader.discover_fixtures(FIXTURES_ROOT)
    assert len(fixtures) >= 19
    # Every fixture id has both envelope and meta files
    for f in fixtures:
        assert f.envelope_path.exists()
        assert f.meta_path.exists()
        assert f.meta_path.name == f.envelope_path.stem + ".meta.json"
    # Sorted by id (FR-015 determinism)
    ids = [f.id for f in fixtures]
    assert ids == sorted(ids)


def test_loader_source_filter_partitions_correctly():
    multica = loader.discover_fixtures(FIXTURES_ROOT, source="multica")
    discord = loader.discover_fixtures(FIXTURES_ROOT, source="discord")
    contract = loader.discover_fixtures(FIXTURES_ROOT, source="contract")
    all_ = loader.discover_fixtures(FIXTURES_ROOT)
    assert len(multica) + len(discord) + len(contract) == len(all_)
    assert all(f.source_shape == "multica" for f in multica)
    assert all(f.source_shape == "discord" for f in discord)
    assert all(f.source_shape == "contract" for f in contract)


def test_subprocess_adapter_rejects_sentinel_leak_3_underscores():
    mock = adapters.MockAdapter("__CC_CONNECT_SILENT_PASS___")
    result = mock.classify({"trigger": {"content": "x"}})
    assert result["ok"] is False
    assert result["error_kind"] == "sentinel-leak"


def test_subprocess_adapter_rejects_sentinel_leak_4_underscores():
    mock = adapters.MockAdapter("__CC_CONNECT_SILENT_PASS____")
    result = mock.classify({"trigger": {"content": "x"}})
    assert result["ok"] is False
    assert result["error_kind"] == "sentinel-leak"


def test_subprocess_adapter_rejects_bare_pass_string():
    mock = adapters.MockAdapter("PASS")
    result = mock.classify({"trigger": {"content": "x"}})
    assert result["ok"] is False
    # bare "PASS" trips the sentinel-leak path because it matches the CC_CONNECT_SILENT_PASS marker substring,
    # OR the malformed-output path because it isn't JSON. Either is a contract violation.
    assert result["error_kind"] in ("sentinel-leak", "malformed-output")


def test_subprocess_adapter_accepts_typed_verdict_object():
    mock = adapters.MockAdapter('{"verdict": "PASS", "confidences": {"PASS": 0.85, "ACK": 0.05, "ASK": 0.05, "SPEAK": 0.05}, "context_checked": ["trigger"]}')
    result = mock.classify({"trigger": {"content": "x"}})
    assert result["ok"] is True
    assert result["verdict"] == "PASS"


def test_in_process_adapter_against_a_known_fixture():
    fixtures = loader.discover_fixtures(FIXTURES_ROOT, source="multica")
    baseline = next(f for f in fixtures if f.id == "m-baseline-pass-adapter-resolved")
    adapter = adapters.InProcessAdapter()
    result = adapter.classify(baseline.envelope)
    assert result["ok"] is True
    assert result["verdict"] == "PASS"


def test_run_one_fixture_handles_contract_fixture_via_mock_adapter():
    fixtures = loader.discover_fixtures(FIXTURES_ROOT, source="contract")
    f3 = next(f for f in fixtures if f.id == "c-verdict-surface-sentinel-leak-3-underscores")
    adapter = adapters.InProcessAdapter()
    response, status, observed, detail = runner._run_one_fixture(
        f3, adapter, deterministic_time=True
    )
    assert status == "pass"
    assert response["error_kind"] == "sentinel-leak"


def test_run_one_fixture_handles_known_false_ack():
    fixtures = loader.discover_fixtures(FIXTURES_ROOT, source="multica")
    f = next(f for f in fixtures if f.id == "m-substring-trap-back-results")
    adapter = adapters.InProcessAdapter()
    response, status, observed, detail = runner._run_one_fixture(
        f, adapter, deterministic_time=True
    )
    assert status == "fail"
    assert observed == "ACK"


def test_report_jsonl_round_trips():
    fixtures = loader.discover_fixtures(FIXTURES_ROOT, source="multica")
    f = next(f for f in fixtures if f.id == "m-baseline-pass-adapter-resolved")
    response = {"ok": True, "verdict": "PASS", "confidences": {"PASS": 0.85, "ACK": 0.05, "ASK": 0.05, "SPEAK": 0.05}, "context_checked": ["trigger", "ctx-pass-handled"]}
    rec = report.fixture_result_record(
        f, response, "pass", "PASS", None, "test-adapter", 12.3
    )
    serialized = json.dumps(rec, sort_keys=True)
    parsed = json.loads(serialized)
    assert parsed["id"] == f.id
    assert parsed["status"] == "pass"
    assert parsed["observed_verdict"] == "PASS"


def test_summary_record_partitions_by_source_and_evidence():
    records = [
        {"kind": "fixture-result", "status": "pass", "source_shape": "multica", "evidence": "runtime"},
        {"kind": "fixture-result", "status": "fail", "source_shape": "discord", "evidence": "runtime"},
        {"kind": "fixture-result", "status": "fail", "source_shape": "discord", "evidence": "predicted"},
    ]
    summary = report.summary_record(records, duration_ms=100.0, adapter_name="x")
    assert summary["fixture_count"] == 3
    assert summary["pass_count"] == 1
    assert summary["fail_count"] == 2
    assert summary["by_source_shape"]["discord"]["fail"] == 2
    assert summary["by_evidence"]["predicted"]["fail"] == 1


def test_determinism_two_in_process_runs_byte_identical(tmp_path, capsys):
    """FR-015: two consecutive runs produce byte-identical JSONL output."""
    exit1 = runner.main([
        "--adapter", "in-process",
        "--format", "jsonl",
        "--deterministic-time",
    ])
    out1 = capsys.readouterr().out
    exit2 = runner.main([
        "--adapter", "in-process",
        "--format", "jsonl",
        "--deterministic-time",
    ])
    out2 = capsys.readouterr().out
    assert exit1 == exit2
    assert out1 == out2


def test_source_filter_union_equals_unfiltered_run(capsys):
    """FR-019: unioned --source runs match the unfiltered run per-fixture."""
    runner.main(["--adapter", "in-process", "--format", "jsonl", "--deterministic-time"])
    all_lines = [l for l in capsys.readouterr().out.splitlines() if '"kind": "fixture-result"' in l]
    all_ids = {json.loads(l)["id"] for l in all_lines}

    union = set()
    for source in ("multica", "discord", "contract"):
        runner.main([
            "--adapter", "in-process",
            "--format", "jsonl",
            "--source", source,
            "--deterministic-time",
        ])
        out = capsys.readouterr().out
        for l in out.splitlines():
            if '"kind": "fixture-result"' in l:
                union.add(json.loads(l)["id"])
    assert union == all_ids
