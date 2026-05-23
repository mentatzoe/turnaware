# Feature Specification: Core CLI MVP

**Feature Branch**: `001-core-cli-mvp`

**Created**: 2026-05-23

**Status**: Draft

**Input**: User description: "A developer can supply a shared-conversation trigger plus available context to TurnAware and receive an auditable admission verdict that a host harness could obey."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Evaluate Admission From a Supplied Context Package (Priority: P1)

A developer runs TurnAware with a trigger and explicit shared-conversation context, then receives a machine-readable admission verdict that tells a host harness whether this agent should visibly participate.

**Why this priority**: This is the minimum vertical product path. Without a runnable verdict path, schemas, fixtures, or documentation do not deliver the product job.

**Independent Test**: Can be fully tested by passing valid admission requests through the command surface and the in-process core, then verifying the returned verdict payload for each verdict category.

**Acceptance Scenarios**:

1. **Given** a valid trigger and context where the agent should participate substantively, **When** the developer evaluates the request, **Then** TurnAware returns `SPEAK` with confidence values, checked context references, and audit reasons.
2. **Given** a valid trigger and context where another participant has already handled the matter, **When** the developer evaluates the request, **Then** TurnAware returns `PASS` with confidence values, checked context references, and audit reasons.
3. **Given** valid fixtures representing `PASS`, `ACK`, `ASK`, and `SPEAK`, **When** each fixture is evaluated, **Then** each expected verdict is produced without relying on a live stochastic provider.

---

### User Story 2 - Preserve Hard-Stop PASS and Context Truth (Priority: P2)

A developer can trust that a `PASS` verdict is safe for a host harness to obey and that the audit trail does not claim to have inspected context that was not supplied or checked.

**Why this priority**: PASS semantics and context truth are load-bearing product promises. A gate that passes but still speaks, or invents inspected context, creates coordination noise and false assurance.

**Independent Test**: Can be fully tested by evaluating PASS-oriented requests and context subsets, then checking that outputs contain no reply-composition payload and that `context_checked` is limited to inspected input items.

**Acceptance Scenarios**:

1. **Given** a request that evaluates to `PASS`, **When** TurnAware returns the verdict, **Then** the output contains no ordinary room-message text, reply draft, or sentinel message for the host to emit.
2. **Given** a request with three supplied context items and only two items inspected by the gate, **When** TurnAware returns the verdict, **Then** `context_checked` names only the two inspected items.
3. **Given** a request with no available context beyond the trigger, **When** TurnAware evaluates it, **Then** `context_checked` does not imply any unavailable history was inspected.

---

### User Story 3 - Fail Clearly on Invalid Input (Priority: P3)

A developer receives a documented, non-ambiguous failure when the request cannot be evaluated, so a host harness can distinguish invalid input from a valid `PASS`.

**Why this priority**: Harnesses must not confuse "the gate ran and decided PASS" with "the gate could not run." Clear failures are required before downstream adapters can safely obey the CLI.

**Independent Test**: Can be fully tested by passing malformed JSON, missing required fields, and unsupported input-source combinations, then checking stdout, stderr, and exit status.

**Acceptance Scenarios**:

1. **Given** malformed JSON input, **When** the developer evaluates it, **Then** TurnAware writes a diagnostic to stderr, exits non-zero, and does not emit a success verdict on stdout.
2. **Given** JSON input missing the trigger, **When** the developer evaluates it, **Then** TurnAware writes a validation error to stderr, exits non-zero, and does not emit a success verdict on stdout.
3. **Given** a missing input file path, **When** the developer evaluates it, **Then** TurnAware writes a file-access error to stderr, exits non-zero, and does not emit a success verdict on stdout.

### Edge Cases

- The request is valid JSON but has no context items beyond the trigger.
- Context item identifiers are duplicated or absent.
- Context items are supplied but irrelevant to the trigger.
- The trigger appears to require only acknowledgement rather than substantive participation.
- The trigger appears to require a clarifying question before substantive participation.
- The input source is absent, unreadable, or conflicts with another input source.
- The input is larger than the MVP accepts for a single local evaluation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: TurnAware MUST accept an admission request from standard input.
- **FR-002**: TurnAware MUST accept an admission request from a named file path.
- **FR-003**: An admission request MUST include a trigger and MAY include explicitly supplied context items, agent identity, surface metadata, and request identifiers.
- **FR-004**: A successful evaluation MUST emit exactly one JSON result on stdout.
- **FR-005**: A successful evaluation result MUST include `verdict`, `confidences`, `context_checked`, and auditable `reasons`.
- **FR-006**: `verdict` MUST be exactly one of `PASS`, `ACK`, `ASK`, or `SPEAK`.
- **FR-007**: `confidences` MUST include numeric confidence values for all four verdicts.
- **FR-008**: `context_checked` MUST name only trigger or context items that were actually inspected during evaluation.
- **FR-009**: If no context beyond the trigger is inspected, `context_checked` MUST truthfully reflect that limited inspection.
- **FR-010**: A `PASS` result MUST NOT include ordinary room-message text, reply prose, a reply draft, or a sentinel message intended for visible emission.
- **FR-011**: TurnAware MUST NOT compose final reply prose for `ACK`, `ASK`, or `SPEAK`; those verdicts only admit participation.
- **FR-012**: The verdict logic MUST be available through an internal callable core that uses the same admission request and result contract as the command surface.
- **FR-013**: The command surface MUST document exit-code semantics that distinguish successful evaluation from input, validation, and runtime failures.
- **FR-014**: Invalid input MUST write diagnostics to stderr and MUST NOT emit a success verdict payload on stdout.
- **FR-015**: The MVP MUST include deterministic fixtures or tests that exercise `PASS`, `ACK`, `ASK`, and `SPEAK`.
- **FR-016**: Tests MUST verify output schema, PASS hard-stop semantics, `context_checked` truthfulness, and invalid input behavior.

### Key Entities *(include if feature involves data)*

- **Admission Request**: The submitted evaluation envelope containing the trigger, supplied context items, optional agent identity, optional surface metadata, and optional request identifiers.
- **Trigger**: The event or message being evaluated for visible participation.
- **Context Item**: A supplied piece of shared-conversation context with an identifier, type, and content available for inspection.
- **Admission Result**: The successful evaluation output containing the verdict, confidence distribution, checked context references, and audit reasons.
- **Verdict Confidence**: A per-verdict numeric confidence value for `PASS`, `ACK`, `ASK`, and `SPEAK`.
- **Error Result**: A failure communicated outside the success verdict stream through stderr and a non-zero exit status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can run one documented command with JSON from stdin and receive a valid admission result in under 2 seconds for each committed fixture.
- **SC-002**: A developer can run one documented command with JSON from a file and receive the same admission result as the equivalent stdin input.
- **SC-003**: The committed verification suite includes at least one deterministic passing example for each verdict: `PASS`, `ACK`, `ASK`, and `SPEAK`.
- **SC-004**: Automated verification proves that every successful result contains only the four allowed verdict values and the required audit fields.
- **SC-005**: Automated verification proves that `PASS` outputs contain no visible reply text or reply draft fields.
- **SC-006**: Automated verification proves that `context_checked` never names a context item absent from the submitted request.
- **SC-007**: Automated verification proves that malformed input, missing required trigger data, and missing file input fail with non-zero status and stderr diagnostics.

## Assumptions

- The first slice uses a deterministic local decision path suitable for fixtures and CI rather than a live stochastic provider.
- The command surface is the primary operator surface for the MVP, while downstream adapters remain out of scope.
- Supplied context is the only context available to the gate unless a future feature adds an authenticated retrieval mechanism.
- Audit reasons explain why a verdict was selected, but they do not provide final reply wording.
- The MVP may use a compact local schema as long as it is documented and verified by runnable commands.
