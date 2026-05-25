# Quickstart: Classifier Verdict Test Suite

**Feature**: 003-classifier-test-suite

This is the runnable, copy-paste integration doc the spec promises. If any command here does not work after `/speckit-implement` completes, that is a Constitution VIII violation — please file an issue.

## Run the suite against the bundled public CLI

```bash
# from repo root
pip install -e .                                          # one-time, installs the `turnaware` CLI
python -m specs.003-classifier-test-suite.contracts.runner
```

Exit code is `0` if every fixture passed; `1` if any fixture failed or any adapter-level error occurred.

Expected on `a132ccc` (the smoke commit): exit code `1` with at least the two false-verdict cases from FR-001 / FR-002 failing, plus the four Discord-suppressor fixtures from FR-021 failing (no suppressor concept in the current classifier — see research.md R5), plus the bracketed-persona and vocative-greeting fixtures from FR-018 failing on the ASK fallthrough mechanism. Baselines (FR-003) should pass.

## Get just the JSONL output for CI

```bash
python -m specs.003-classifier-test-suite.contracts.runner --format jsonl > results.jsonl
```

Each line is a `fixture-result` object; the last line is a `summary` object. See `data-model.md` for the schema.

## Filter to one source pool

```bash
python -m specs.003-classifier-test-suite.contracts.runner --source discord     # FR-019
python -m specs.003-classifier-test-suite.contracts.runner --source multica
python -m specs.003-classifier-test-suite.contracts.runner --source contract
```

Filtering does not change the pass/fail status of any included fixture; the unfiltered run and the unioned filtered runs report the same per-fixture outcomes.

## List fixtures without running them

```bash
python -m specs.003-classifier-test-suite.contracts.runner --list
```

Prints the index (id, source, evidence, expected verdict, FR refs) one per line.

## Add a fixture (under 5 minutes — SC-004)

1. Copy an existing fixture-pair as a template:

   ```bash
   cd specs/003-classifier-test-suite/contracts/fixtures/discord
   cp d-vocative-greeting-first-bot.json d-my-new-case.json
   cp d-vocative-greeting-first-bot.meta.json d-my-new-case.meta.json
   ```

2. Edit `d-my-new-case.json` — replace `trigger.content`, `trigger.id`, `request_id`, and any `context` items. Keep `source_shape` accurate. The envelope is a `turnaware admit --input` request; `turnaware admit --input d-my-new-case.json` should run end-to-end.

3. Edit `d-my-new-case.meta.json` — set `id`, `title`, `expected.verdict`, `failure_mode`, `invariant`, `rationale`, `fr_refs`, `sc_refs`. If the case came from runtime evidence, set `evidence: "runtime"` and `runtime_source`; if it came from code reading, set `evidence: "predicted"` and `predicted_basis`.

4. Run the suite. Your fixture appears in the report with no runner code changes.

   ```bash
   python -m specs.003-classifier-test-suite.contracts.runner
   ```

## Plug in a non-default adapter

The bundled subprocess adapter calls `turnaware admit --input <tmp>.json`. To test against an in-process candidate (e.g., a future `turnaware.core.evaluate` import):

```bash
python -m specs.003-classifier-test-suite.contracts.runner --adapter in-process
```

To test against a CLI on a different path (e.g., a candidate build):

```bash
python -m specs.003-classifier-test-suite.contracts.runner --adapter subprocess --cmd /path/to/candidate-turnaware
```

To test a third-party / non-Python adapter, implement the `Adapter` protocol (see `contracts/adapters.py` `class Adapter(Protocol)`) and pass `--adapter custom:path/to/your_adapter.py:YourAdapter`.

## Run the runner's own self-tests

```bash
pytest tests/test_003_runner.py
```

These exercise loader correctness, report shape, JSONL stream validity, the adapter contract, and the `--mock-adapter-output` flag that the verdict-surface contract fixtures rely on. They do NOT exercise the actual fixtures — that's what the runner does. The self-tests run in milliseconds; the actual suite runs in seconds.

## Troubleshooting

- **`turnaware: command not found`** — run `pip install -e .` from repo root, or use `--adapter subprocess --cmd "$(python -c 'import sys; print(sys.executable)') -m turnaware"` to invoke the module directly.
- **All fixtures report `error_kind: subprocess-crash`** — the adapter cannot find or execute the CLI. Verify with `turnaware admit --input tests/fixtures/pass.json` directly.
- **Determinism check** — run twice; the JSONL output should be byte-identical (per FR-015). If not, file a bug.
