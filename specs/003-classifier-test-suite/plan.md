# Implementation Plan: Classifier Verdict Test Suite

**Branch**: `003-classifier-test-suite` | **Date**: 2026-05-25 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-classifier-test-suite/spec.md` (clarified 2026-05-25; expanded with Discord-pilot human-conversation cases the same day)

## Summary

Build a deterministic, offline test suite that exercises the TurnAware admission classifier against two evidence pools: the TUR-8/9/10 Multica-shape smoke fixtures distilled in the TUR-12 corpus, and the pilot-bot Discord session log human-conversation shapes. The suite consumes a candidate classifier through a pluggable adapter (subprocess against `turnaware admit --input` by default; a future in-process adapter would import `turnaware.core.evaluate` directly), runs each JSON fixture through the adapter, and emits per-fixture pass/fail in human-readable text plus a JSON Lines machine-readable stream. The runner exits non-zero on any failure. The suite is vendored under `specs/003-classifier-test-suite/contracts/` and is invoked by a single command from repo root. No new runtime dependency outside the existing `pyproject.toml`.

## Technical Context

**Language/Version**: Python 3.11 (matches `pyproject.toml` `requires-python = ">=3.11"`; matches the existing `turnaware` package).

**Primary Dependencies**: Stdlib only (`json`, `subprocess`, `pathlib`, `argparse`, `dataclasses`, `sys`). No third-party runtime dependency. `pytest` (already used by `tests/test_*.py`) is the harness for the suite's own self-tests.

**Storage**: Filesystem-only. Fixtures live as `*.json` files under `specs/003-classifier-test-suite/contracts/fixtures/`. No DB.

**Testing**: `pytest` for runner self-tests (per `tests/` convention). The suite itself is *exercised* by running the runner against the public CLI; that exercise is what FR-001 / FR-002 / SC-001 verify against `a132ccc`.

**Target Platform**: macOS and Linux (developer-laptop / CI). No Windows-specific paths; uses `pathlib.Path` and POSIX subprocess.

**Project Type**: CLI / library hybrid (the runner is a CLI; the fixture loader and adapter are importable so future tooling can reuse them).

**Performance Goals**: Whole suite under 5 seconds on a standard developer laptop (SC-005). Per-fixture median budget therefore ≲50ms with 50–100 fixtures. Subprocess fork dominates per-fixture cost; bench during implementation.

**Constraints**: No network, no LLM, no remote fetch (FR-009 / FR-017). Deterministic across runs and OSes (FR-015). Single-command invocation from repo root (FR-011). Exit non-zero on any failure (FR-011). Output JSONL + human-readable text covering identical field set (FR-012 / FR-013).

**Scale/Scope**: ~20–30 fixtures at v1 (10–12 Multica-shape from TUR-12 corpus, 13–15 Discord-shape from FR-018 enumeration, 4 named-suppressor fixtures from FR-021, 1 verdict-surface contract from FR-020, baselines). Extensibility budget: under 5 minutes per added fixture (SC-004).

## Constitution Check

Walked the eight Core Principles against this plan; result: PASS, no violations to track.

- **I. Admission, Not Composition** — PASS. The suite tests verdict admission only. It does not draft reply prose, does not prescribe wording, does not introduce new verdicts. The verdict-surface contract test (FR-020) reinforces this principle by failing classifiers that try to compose a transport string instead of returning a typed verdict.
- **II. Hard-Stop PASS Is Load-Bearing** — PASS. FR-020 + SC-011 directly encode this principle as a contract assertion: PASS-as-string sentinel variants (the actual pilot-bot leak) are explicitly rejected as contract failures distinct from verdict miscategorizations. The suite is one of the mechanisms the constitution requires to keep "a successful PASS MUST NOT emit a room message" enforceable.
- **III. CLI-First, Modular Core** — PASS. The pluggable adapter (FR-022) consumes the existing `turnaware admit --input` CLI today (the subprocess adapter is the default) and is explicitly designed to also consume an in-process callable core tomorrow (the principle's "stable in-process evaluation boundary"). No "CLI containing all decision logic" is created here — the runner is a thin transport over the adapter.
- **IV. Vertical, Independently Testable Slices** — PASS. The suite ships an end-to-end runnable artifact (`python -m specs.003_classifier_test_suite.contracts.runner` or equivalent single command) that exercises real fixtures against the real public CLI. Not schemas-only, not docs-only; the slice does the product job of "tell me whether this candidate gets the verdicts right" today.
- **V. Test-First Contract and Fixture Discipline** — PASS. The suite IS the contract/fixture discipline for TUR-11's classifier completion. All four verdicts (PASS, ACK, ASK, SPEAK) are covered (FR-003 baselines + FR-001 / FR-002 false-case fixtures). Contract tests cover output schema (FR-020), PASS suppression semantics (FR-020 + SC-011), `context_checked` truthfulness (FR-007), and adapter failure behaviour for invalid input (FR-022). The deterministic CI path is the subprocess adapter against the public CLI; no stochastic provider needed.
- **VI. Adapter Tier Honesty and Consumer Boundaries** — PASS. FR-022 explicitly names the adapter as a tier-aware boundary; subprocess adapter is the "wrapper/gateway" tier today; a future in-process adapter would be the "pre-input hook" or "agent-invoked tool" tier. The suite's own honesty about which adapter ran is surfaced in the JSONL output's per-fixture record so a downstream consumer can tell which tier was exercised.
- **VII. Context Truth and Room Inference** — PASS. FR-007 is the explicit test of `context_checked` truthfulness against actual consultation. The Discord-shape suppressor fixtures (FR-021) exercise room inference (the gate inferring "the room" from peer messages) without baking a "hardcoded surface taxonomy" — they assert outcomes against the `before-you-respond.md` policy, which itself comes from supplied context, not a hidden product contract.
- **VIII. Documentation Is Product** — PASS. The runner publishes a `quickstart.md` (Phase 1 below) that is runnable verbatim. FR-012 makes the human-readable output self-explanatory ("a human reader MUST NOT need to open the source comment or smoke threads to interpret a failing line"). No marketing/positioning copy ships with this slice; the README updates planned at polish stage will state the suite's scope and link the spec.

**Gate decision**: PASS — proceed to Phase 0. No violations to track in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/003-classifier-test-suite/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output: runner + fixtures + adapter
│   ├── runner.py            # CLI entry point + orchestration
│   ├── adapters.py          # SubprocessAdapter (default); InProcessAdapter (stub)
│   ├── loader.py            # fixture discovery + JSON parsing + validation
│   ├── report.py            # JSONL + human-readable rendering
│   ├── invariants.py        # the structural-invariant assertions (FR-005..FR-008, FR-020)
│   ├── fixtures/
│   │   ├── multica/         # FR-001..FR-008 fixtures (TUR-8/9/10 + corpus)
│   │   ├── discord/         # FR-018 + FR-021 fixtures (pilot-bot session)
│   │   └── contract/        # FR-020 verdict-surface contract fixture(s)
│   ├── index.json           # fixture registry: id -> path -> expected + metadata
│   └── README.md            # links spec, names entry command, lists fixture classes
├── tasks.md             # /speckit-tasks output (Phase 2; produced separately)
└── checklists/
    └── requirements.md  # spec quality checklist (already validated 2x)
```

### Source Code (repository root)

```text
src/
└── turnaware/                # existing package; NOT modified by this slice
    ├── cli.py
    ├── core.py
    ├── errors.py
    ├── models.py
    ├── schema.py
    └── __init__.py

tests/
├── test_cli.py                       # existing
├── test_core.py                      # existing
├── test_schema.py                    # existing
├── test_003_runner.py                # NEW: pytest exercising the runner's own behaviour
│                                     #      (loader correctness, report shape, adapter contract)
└── fixtures/                         # existing per-verdict baselines used by test_core/test_cli;
                                      # the suite's fixtures live under specs/003-*/contracts/fixtures/
                                      # so they're co-located with the spec, not mixed with unit tests.
```

**Structure Decision**: The runner and fixtures are vendored under the spec directory (`specs/003-classifier-test-suite/contracts/`) per FR-017 and per SpecKit convention for contract artifacts. The runner is invokable via `python -m` from repo root; a thin wrapper script may be added in `bin/` at polish stage if Zoe wants a shorter invocation. The runner's own self-tests live in `tests/test_003_runner.py` so they're picked up by the existing `pytest` setup. No modifications to `src/turnaware/` in this slice — the classifier under test is consumed via the adapter, not patched.

## Complexity Tracking

No Constitution Check violations to justify. This section intentionally empty.

## Phase 0 outline (executed during /speckit-plan)

See `research.md` for the resolved decisions. Topics covered:

- **R1**: How to invoke the public CLI from the runner reliably across macOS/Linux (subprocess concerns, signal handling, stdout/stderr separation).
- **R2**: How to express "predicted, not runtime-observed" in fixture metadata so the runner can surface the distinction (FR-004 / SC-008).
- **R3**: How to express the verdict-surface contract fixture (FR-020 / SC-011) without coupling the suite to a Python type system — the contract must hold for a future Rust/Go/Node adapter too.
- **R4**: Fixture id naming convention (raised as low-impact in clarify; resolved here so the index.json is consistent).
- **R5**: How the four named Discord suppressors (FR-021) are exercised against the *current* `turnaware.core.evaluate` which has no Discord-suppressor concept yet — these fixtures are expected to fail on `a132ccc`, and the failure-mode column documents why.

## Phase 1 outline (executed during /speckit-plan)

See `data-model.md`, `contracts/README.md`, and `quickstart.md` for the artifacts.

- **Data model**: documents the fixture envelope schema (extending the public `turnaware admit` request shape with `source_shape` and per-item `timestamp`), the runner result schema (JSONL line + summary), the adapter interface, and the per-fixture index entry shape.
- **Contracts**: the `contracts/` directory carries the runner + adapter + fixture index + per-source fixture trees. The contract is "given a fixture JSON, the adapter MUST produce a typed verdict and the runner MUST report pass/fail with the metadata in FR-012."
- **Quickstart**: a short, runnable doc showing how to run the suite against the bundled subprocess adapter, how to add a fixture, and how to plug in a non-default adapter. Lives at `specs/003-classifier-test-suite/quickstart.md`.

**Agent context update**: The CLAUDE.md SPECKIT block in this worktree points at this plan after Phase 1 completes (per the speckit-plan skill step 3.3).

## Re-check Constitution Check post-Phase 1

Phase 1 introduces no new architecture, only the concrete file layout. The eight gates above still PASS. No new violations.
