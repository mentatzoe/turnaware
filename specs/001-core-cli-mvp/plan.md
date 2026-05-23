# Implementation Plan: Core CLI MVP

**Branch**: `001-core-cli-mvp` | **Date**: 2026-05-23 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-core-cli-mvp/spec.md`

**Note**: This template was seeded by the `/speckit-plan` workflow and filled for the first TurnAware vertical CLI slice.

## Summary

Deliver the first vertical TurnAware product path: a developer supplies a shared-conversation trigger and optional context as JSON, then receives an auditable admission verdict (`PASS`, `ACK`, `ASK`, or `SPEAK`) that a host harness can obey. Implement a Python standard-library package with an internal callable core and a thin `turnaware` CLI wrapper. The deterministic MVP classifier is fixture-oriented and local-only so CI can verify all verdicts without a live stochastic provider.

## Technical Context

**Language/Version**: Python 3.11+ using the standard library

**Primary Dependencies**: None at runtime; package metadata via `pyproject.toml`

**Storage**: N/A; single-request evaluation with no persistence

**Testing**: `python -m unittest`

**Target Platform**: Local POSIX-like developer shell and CI runner with Python 3.11+

**Project Type**: Library plus CLI

**Performance Goals**: Each committed fixture evaluates in under 2 seconds from process start on a typical developer machine

**Constraints**: Admission-only; no reply composition; deterministic provider path; JSON stdin/file input; JSON stdout for success; stderr and non-zero status for failures

**Scale/Scope**: MVP handles one admission request per CLI invocation and uses only supplied trigger/context data

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Admission, Not Composition | PASS | Result contains admission verdicts and audit reasons only; final reply prose remains out of scope. |
| II. Hard-Stop PASS Is Load-Bearing | PASS | PASS contract forbids ordinary room-message text, reply drafts, or sentinel text. |
| III. CLI-First, Modular Core | PASS | CLI delegates to internal callable core in `src/turnaware/core.py`; JSON stdin/file and exit semantics are planned. |
| IV. Vertical, Independently Testable Slices | PASS | MVP covers request input through verdict output with fixtures for all verdicts. |
| V. Test-First Contract and Fixture Discipline | PASS | Tasks will create fixtures and tests before implementation; tests cover schema, PASS, context truth, and invalid input. |
| VI. Adapter Tier Honesty and Consumer Boundaries | PASS | Downstream adapters are out of scope; CLI contract states host-harness behavior. |
| VII. Context Truth and Room Inference | PASS | `context_checked` is limited to inspected trigger/context IDs supplied in the request. |
| VIII. Documentation Is Product | PASS | Quickstart commands must be runnable and verified before done. |

## Project Structure

### Documentation (this feature)

```text
specs/001-core-cli-mvp/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── admission-cli.md
└── tasks.md
```

### Source Code (repository root)

```text
pyproject.toml
README.md
src/
└── turnaware/
    ├── __init__.py
    ├── __main__.py
    ├── cli.py
    ├── core.py
    ├── errors.py
    ├── models.py
    └── schema.py
tests/
├── fixtures/
│   ├── pass.json
│   ├── ack.json
│   ├── ask.json
│   └── speak.json
├── test_cli.py
├── test_core.py
└── test_schema.py
```

**Structure Decision**: Single Python package with a dedicated internal core and thin CLI wrapper. This keeps the first slice portable, avoids runtime dependencies, and makes adapter reuse possible without shelling out.

## Phase 0: Research Summary

Research decisions are captured in [research.md](./research.md). Key decisions: Python standard library, deterministic local classifier, compact JSON contract, explicit exit-code categories, and runnable docs only.

## Phase 1: Design Summary

Design artifacts are captured in [data-model.md](./data-model.md), [contracts/admission-cli.md](./contracts/admission-cli.md), and [quickstart.md](./quickstart.md). The CLI contract and internal core share the same request/result model.

## Constitution Check - Post-Design

| Principle | Status | Notes |
|-----------|--------|-------|
| Admission, Not Composition | PASS | Contract excludes `message`, `reply`, and `draft` fields. |
| Hard-Stop PASS | PASS | PASS examples and tests assert no visible reply content. |
| CLI-First, Modular Core | PASS | Project structure separates `cli.py` from `core.py`. |
| Vertical Slice | PASS | Tasks can deliver stdin/file input through verified verdict output. |
| Test-First Contract | PASS | Fixtures and tests precede implementation in task order. |
| Adapter Honesty | PASS | Quickstart describes CLI/core only; adapters remain future work. |
| Context Truth | PASS | Data model defines checked context references as a subset of inspected request items. |
| Documentation Is Product | PASS | Quickstart commands are part of verification tasks. |

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
