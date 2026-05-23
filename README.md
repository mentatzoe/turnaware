# TurnAware

Pre-reply judgment for turn-aware agents.

TurnAware is a portable CLI/library for deciding whether an agent should visibly
participate on an unstructured shared surface before ordinary reply generation.
It returns an auditable admission verdict:

- `PASS` — hard stop; no ordinary visible reply
- `ACK` — brief acknowledgement is warranted
- `ASK` — clarification is warranted
- `SPEAK` — substantive contribution is warranted

## Status

The first vertical CLI slice is implemented on the `001-core-cli-mvp` branch.
It provides a deterministic local admission path for supplied JSON context,
backed by an internal callable core and fixture tests for all four verdicts.

Downstream adapters, live provider evaluation, central orchestration, and reply
composition remain out of scope for this slice.

## Quickstart

Evaluate a request from stdin:

```sh
PYTHONPATH=src python3 -m turnaware admit < tests/fixtures/speak.json
```

Evaluate a request from a file:

```sh
PYTHONPATH=src python3 -m turnaware admit --input tests/fixtures/pass.json
```

Run the verification suite:

```sh
python3 -m unittest
```

## Product contract

The core output contract is:

- `verdict`
- `confidences`
- `context_checked`
- `reasons`

Successful CLI evaluations write one JSON object to stdout and exit `0`.
Failures write diagnostics to stderr and do not emit a success verdict on
stdout.

Exit codes:

- `0` — successful evaluation
- `1` — unexpected runtime failure
- `2` — input source or JSON parse failure
- `3` — admission request validation failure

TurnAware owns admission, not composition. It does not draft the final reply and
it does not prescribe speech shape beyond the admission verdict.

## Python API

The in-process core is available without shelling out:

```python
import os
import sys
sys.path.insert(0, os.path.abspath("src"))

from turnaware import evaluate

result = evaluate({
    "trigger": {"content": "turnaware-vigil, please implement the CLI MVP."},
    "context": [],
})
```

`result["verdict"]` is one of `PASS`, `ACK`, `ASK`, or `SPEAK`.

## Development method

This repository uses Spec Kit. The constitution at
`.specify/memory/constitution.md` is the source of governance for all specs,
plans, tasks, implementation, documentation, and release claims.

For production work, use:

```text
constitution -> specify -> clarify -> checklist -> plan -> tasks -> analyze -> implement
```

The first product spec should prove an end-to-end runnable path from supplied
conversation context to a verdict a harness can obey.

## License

TurnAware is dual-licensed under MIT OR Apache-2.0, at your option. See
`LICENSE-MIT` and `LICENSE-APACHE`.
