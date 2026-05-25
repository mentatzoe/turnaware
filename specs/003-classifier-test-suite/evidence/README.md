# Evidence

This directory carries runtime artifacts produced by exercising the suite. The
artifacts here are the suite's first runtime evidence and are what TUR-11's
classifier-completion implementor consumes.

## a132ccc-baseline.jsonl

The complete suite output (JSONL form, deterministic time zeroed) against the
public `turnaware` CLI at the worktree HEAD. The classifier code itself is at
the `a132ccc` smoke commit unchanged — the worktree's commits are SpecKit
artifacts only.

### Summary at capture time (2026-05-25)

```
19 fixtures total
  6 PASS:
     - 4 Multica baselines (FR-003 per-verdict): PASS, ACK, ASK, SPEAK
     - 2 contract sentinel-leak rejections (FR-020 / SC-011)
 13 FAIL (broken down):
   Multica:
     - m-substring-trap-back-results        false ACK from "ack " ∈ "back "  (FR-001)
     - m-trigger-only-pass-fake-done        false PASS, trigger-first short-circuit  (FR-002)
     - m-trigger-only-pass-empty-context    PASS from bare claim with empty context  (FR-005)
     - m-no-keyword-negative-control        ASK fallthrough at 0.85  (FR-006)
   Discord:
     - d-bracketed-persona-podcast          ASK fallthrough on persona framing  (FR-018)
     - d-casual-pivot-stock-market          ASK fallthrough; embedded ask missed  (FR-018)
     - d-named-ask-dalgos-addressed         ASK fallthrough on direct-named ask  (FR-018)
     - d-vocative-greeting-first-bot        ASK fallthrough on vocative greeting  (FR-018)
     - d-vocative-greeting-second-bot       no Covered suppressor  (FR-021)
     - d-suppressor-covered                 no Covered suppressor  (FR-021)
     - d-suppressor-self-caused             no Self-caused suppressor  (FR-021)
     - d-suppressor-duplicate               no Duplicate suppressor  (FR-021)
     - d-suppressor-stale                   no Stale suppressor  (FR-021)
  0 ERROR (no adapter-level failures)
```

### How this satisfies the spec's success criteria

- **SC-001**: ≥2 failures on `a132ccc` — 13 observed, including FR-001 and FR-002.
- **SC-002**: independently reproducible — `python -m pytest tests/test_003_runner.py::test_determinism_two_in_process_runs_byte_identical` passes; two consecutive runs are byte-identical with `--deterministic-time`.
- **SC-003**: every required fixture class covered — FR-001, FR-002, FR-003 (×4), FR-005, FR-006, FR-018 (subset of the 11 named cases shipped at MVP), FR-020 (×2), FR-021 (×4).
- **SC-005**: full suite executes in ~0.7s (subprocess adapter, real CLI) and ~0.0s (in-process adapter) — well under the 5s budget.
- **SC-008**: distinguishes runtime vs. predicted in both forms — `evidence` field carried in JSONL, `[runtime]` / `[predicted]` prefix in human-readable.
- **SC-009**: source filter is correct — `tests/test_003_runner.py::test_source_filter_union_equals_unfiltered_run` passes.
- **SC-010**: Discord-pilot-shape cases exercised — 9 Discord fixtures shipped at MVP (vocative ×2, persona, casual pivot, named ask, 4 suppressors); FR-018's full 11-case enumeration has 6 cases deferred to follow-up (mixed-address, operator-pivot, self-iteration ×2, peer-imperative, Discord-mention ×2, multi-step constraint) — tracked under tasks.md Phase 4.
- **SC-011**: sentinel-leak rejected and labelled as such — `error_kind: "sentinel-leak"` distinct from `error_kind: "schema-violation"`.

### MVP scope vs. full FR-018 enumeration

The shipped MVP covers 5 of the 11 named Discord-shape cases (FR-018):
vocative, persona framing, casual pivot, named ask, and the structural
counterpart via the 4 named-suppressor fixtures (FR-021). The remaining 6
Discord cases (mixed-address ×2, operator topic-pivot, self-iteration ×2,
peer-imperative, Discord-mention ×2, multi-step constraint) follow the same
fixture shape and adapter path; they are tractable in a follow-up because
the runner does not change. Tracked in `tasks.md` Phase 4.

### Reproduce

```bash
# From repo root, after `pip install -e .`
python specs/003-classifier-test-suite/contracts/runner.py \
  --adapter subprocess \
  --format jsonl \
  --deterministic-time \
  > /tmp/baseline.jsonl
diff specs/003-classifier-test-suite/evidence/a132ccc-baseline.jsonl /tmp/baseline.jsonl
```

If `diff` reports differences, either the classifier has moved (re-baseline
the file) or the fixtures have been edited (verify the change was intended).
