# Data Model: Admission Classifier Completion

## Admission Envelope

Supplied evaluation input for one admission decision.

Fields inherited from 001:
- `trigger`: required Trigger object.
- `context`: optional ordered list of Context Item objects.
- `agent`: optional host/agent metadata.
- `surface`: optional shared-surface metadata.
- `request_id`: optional correlation ID echoed in successful results.

New/clarified fields:
- `classifier`: optional string selecting the classifier path. If omitted, the documented default path is used and exposed in the result.
- `classifier_config`: optional object containing path-specific options. Unsupported keys or invalid values fail clearly for the selected path.

Validation rules:
- `classifier` must match a registered classifier path.
- Missing classifier uses exactly one documented product default when its configuration is available; unavailable defaults fail clearly with no deterministic fallback.
- Invalid classifier/configuration produces no successful admission result and no fallback result.

## Trigger

The current event/comment/message being evaluated.

Fields:
- `content`: required string.
- `id`: optional string; defaults to `trigger`.
- `author`: optional string.
- `timestamp`: optional string.

Reference form in `context_checked`: `trigger:<id>`.

## Context Item

Supplied historical/environmental evidence that may support, contradict, or qualify the trigger.

Fields:
- `content`: required string.
- `id`: required string.
- `type`: optional string.
- `author`: optional string.
- `timestamp`: optional string.

Reference form in `context_checked`: `context:<id>`.

## Classifier Configuration

Host-selected classifier path and options.

Required supported paths for this slice:
- product/default classifier path: the actual admission classifier used by hosts for product evaluation. Its concrete registry name and configuration schema must be documented in the implementation artifacts and exposed in every result.
- `deterministic`: explicit offline, repeatable evidence classifier used for local and CI verification. It is not the product default and must not be selected silently as fallback.

This slice is complete only if the product classifier path exists and deterministic evidence works without network or credentials.

Validation rules:
- Unknown path is an error.
- Unavailable path is an error.
- Invalid option is an error.
- The active path must be exposed in every successful result.

## Admission Result

Successful admission decision.

Fields inherited from 001:
- `verdict`: exactly one of `PASS`, `ACK`, `ASK`, `SPEAK`.
- `confidences`: object containing confidence for each verdict.
- `reasons`: non-empty list of audit reasons.
- `context_checked`: list of inspected trigger/context references.
- `request_id`: optional echo of request ID.

New/clarified fields:
- `classifier`: machine-readable selected classifier identity/configuration summary.

Constraints:
- Successful payload must not include `message`, `reply`, `draft`, `content`, or other ordinary visible participation prose fields.
- `context_checked` may only include supplied references actually inspected by the classifier.
- Contradictory context that materially prevents PASS must appear in `context_checked` or equivalent evidence.
- Confidence distribution must reflect conflict/uncertainty rather than using the same high-confidence template for every match.

## Adversarial Evidence Case

Fixture or documented deterministic case used to prove verdict quality.

Required cases:
- False ACK guard: assignment wording includes `comment back with results`; expected verdict `SPEAK`, not `ACK`.
- False PASS guard: trigger uses resolved/no-response wording while context says evidence/work is missing; expected verdict is not `PASS` and contradictory context is checked.
- Representative `PASS`, `ACK`, `ASK`, and `SPEAK` cases.
- Invalid classifier configuration case.
