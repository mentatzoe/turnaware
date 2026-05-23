# Research: Core CLI MVP

## Decision: Use Python 3.11+ and the standard library

**Rationale**: The repository has no existing runtime package. Python provides a portable CLI, JSON parsing, dataclasses, subprocess-friendly tests, and packaging metadata without adding runtime dependencies. Standard-library-only implementation keeps the first vertical slice small and deterministic.

**Alternatives considered**:
- Node.js: good CLI ergonomics, but would introduce package-manager and dependency choices before the first core path exists.
- Rust: strong binary distribution story, but more setup than needed for a first audited MVP.
- Go: portable binary story, but no existing project signals prefer it over Python for this initial slice.

## Decision: Separate CLI wrapper from internal callable core

**Rationale**: The constitution requires both CLI reachability and an in-process evaluation boundary. `cli.py` will own argument parsing, stdin/file IO, stdout/stderr, and exit codes. `core.py` will expose `evaluate(request)` returning a structured result.

**Alternatives considered**:
- Put all logic in the command: rejected because it would violate the modular-core requirement.
- Build an adapter abstraction now: rejected because downstream adapters are explicitly out of scope.

## Decision: Deterministic local classifier for MVP fixtures

**Rationale**: CI must verify all four verdicts without a live stochastic provider. The first classifier should use explicit trigger/context signals and conservative defaults so fixtures can demonstrate `PASS`, `ACK`, `ASK`, and `SPEAK`.

**Alternatives considered**:
- Live LLM/provider call: rejected for nondeterminism and external dependency.
- Hardcoded fixture filenames: rejected because the CLI must evaluate request content, not test-file names.

## Decision: Compact JSON request/result contract

**Rationale**: The feature requires JSON input and JSON output. A compact object contract is easy for host harnesses to produce and inspect while still allowing audit fields and context references.

**Alternatives considered**:
- Free-form text input: rejected because context truth and output schema tests need structured IDs.
- Multiple subcommands before MVP: rejected because one admission command is enough for the first vertical path.

## Decision: Exit-code categories

**Rationale**: Harnesses must distinguish a valid `PASS` from failure to evaluate. The CLI will return `0` on successful evaluation, `2` for input/read errors, `3` for validation errors, and `1` for unexpected runtime failures.

**Alternatives considered**:
- Single non-zero error: rejected because file-access and validation failures are different integration problems.
- Emit error JSON on stdout: rejected because successful verdict JSON must remain unambiguous.

## Decision: Documentation only for runnable CLI/core behavior

**Rationale**: Documentation is product in this repository. README and quickstart updates must be backed by commands and tests in this slice and must not claim downstream adapters or provider quality that do not exist yet.

**Alternatives considered**:
- Add adapter examples: rejected as out of scope.
- Add DevRel or marketing examples: rejected until runnable verification exists.
