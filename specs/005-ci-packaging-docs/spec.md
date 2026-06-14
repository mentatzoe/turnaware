# Feature Specification: CI, Packaging, and Integration Documentation

**Feature Branch**: `005-ci-packaging-docs`

**Created**: 2026-06-14

**Status**: Implemented

**Tier**: Hardening / documentation. No change to the admission contract or the
classifier; this makes the existing product verifiable, installable, and
integrable.

## Why this exists

Three gaps remained after the core (`002`), suite (`003`), and adapter (`004`)
shipped:

- **No CI.** "Run the tests before claiming done" relied on discipline; nothing
  enforced it on push/PR.
- **No clean-install evidence.** The package was importable via the `tests/`
  `sys.path` shim, but nothing proved `pip install .` yields a working public
  surface and console scripts.
- **No integration guide.** Consumption docs were scattered (README section,
  `004` spec, demo). There was no single guide covering scope, how an agent
  *installs and wires* the gate, and how integration differs across channel
  adapters.

## Scope

In scope:

- A GitHub Actions workflow running the full offline suite on a Python matrix,
  plus a clean-install packaging job that exercises the installed console
  scripts end-to-end (stubbed classifier — no secrets).
- Committed packaging evidence from a clean virtualenv install.
- An integration/installation guide (`docs/integration.md`) covering the product
  scope boundary, the distinct agentic install/integration paths, and how to
  wire the gate into different channel adapters — grounded in how pilot-bot and
  cc-connect actually do it.

Out of scope:

- Live-provider testing in CI (offline only; live evidence stays a manual
  release step — `specs/003-classifier-test-suite/evidence/`).
- Publishing to PyPI; any new runtime dependency (the package stays stdlib-only).

## Requirements

- **FR-001**: CI runs `python -m unittest` on Python 3.11/3.12/3.13 on push to
  `main` and on PRs, with no provider secrets, and fails the build on any test
  failure.
- **FR-002**: CI includes a clean-install job: `pip install .` into a fresh
  venv, import the public surface without the test shim, and drive both console
  scripts (`turnaware`, `turnaware-channel`) end-to-end with a stubbed
  classifier.
- **FR-003**: `docs/integration.md` documents the scope boundary, the install
  paths, and per-adapter integration, with runnable commands; the README links
  it.

## Success Criteria

- **SC-001**: All CI steps are validated locally before commit (the packaging
  smoke and the `--list` smoke both pass against a clean install).
- **SC-002**: Packaging evidence is committed
  (`specs/005-ci-packaging-docs/evidence/packaging-2026-06-14.txt`).
- **SC-003**: A new integrator can wire the gate into a channel from
  `docs/integration.md` alone, choosing the path (loader instruction / in-process
  / subprocess) that fits their host.
