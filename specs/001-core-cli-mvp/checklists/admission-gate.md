# Admission Gate Requirements Checklist: Core CLI MVP

**Purpose**: Unit-test the requirements for the TurnAware admission-gate MVP before implementation planning.
**Created**: 2026-05-23
**Feature**: [spec.md](../spec.md)
**Audience**: Reviewer gate before planning

## Requirement Completeness

- [x] CHK001 Are all four verdicts explicitly named and bounded to the admission decision surface? [Completeness, Spec FR-006]
- [x] CHK002 Are command input modes for stdin and file both specified as product requirements? [Completeness, Spec FR-001, FR-002]
- [x] CHK003 Are successful output fields required for verdict, confidences, checked context, and audit reasons? [Completeness, Spec FR-004, FR-005]
- [x] CHK004 Is the internal callable core required separately from the command wrapper? [Completeness, Spec FR-012]
- [x] CHK005 Are deterministic fixtures or tests required for all four verdict outcomes? [Completeness, Spec FR-015]

## Requirement Clarity

- [x] CHK006 Is `PASS` defined as terminal for ordinary visible participation rather than as a quiet reply? [Clarity, Spec US2, FR-010]
- [x] CHK007 Is reply composition explicitly excluded for admitted verdicts as well as PASS? [Clarity, Spec FR-011]
- [x] CHK008 Is `context_checked` constrained to actually inspected trigger or context items? [Clarity, Spec FR-008, FR-009]
- [x] CHK009 Are invalid-input outcomes separated from successful PASS outcomes? [Clarity, Spec US3, FR-013, FR-014]
- [x] CHK010 Are audit reasons required without implying final reply wording? [Clarity, Spec FR-005, Assumptions]

## Requirement Consistency

- [x] CHK011 Do the user stories, requirements, and success criteria use the same four verdict names without aliases? [Consistency, Spec US1, FR-006, SC-003]
- [x] CHK012 Do PASS scenarios align with the constitution by forbidding visible room-message output? [Consistency, Spec US2, FR-010, SC-005]
- [x] CHK013 Do context-truth requirements align across acceptance scenarios, functional requirements, and measurable outcomes? [Consistency, Spec US2, FR-008, SC-006]
- [x] CHK014 Do invalid-input requirements consistently require stderr diagnostics and non-zero status? [Consistency, Spec US3, FR-014, SC-007]

## Acceptance Criteria Quality

- [x] CHK015 Are success criteria measurable through committed commands, fixtures, or automated verification? [Acceptance Criteria, Spec SC-001-SC-007]
- [x] CHK016 Is the stdout/stderr separation measurable for success and failure cases? [Acceptance Criteria, Spec FR-004, FR-014, SC-007]
- [x] CHK017 Is stdin/file parity measurable without depending on a live provider? [Acceptance Criteria, Spec SC-001, SC-002, Assumptions]

## Scenario Coverage

- [x] CHK018 Are primary successful evaluation flows covered for both participation and non-participation? [Coverage, Spec US1]
- [x] CHK019 Are ACK and ASK outcomes included in fixture coverage even though they are not the dominant MVP examples? [Coverage, Spec US1, FR-015, SC-003]
- [x] CHK020 Are missing context, irrelevant context, and context subset scenarios addressed? [Coverage, Spec US2, Edge Cases]
- [x] CHK021 Are malformed JSON, missing trigger, and missing file scenarios addressed? [Coverage, Spec US3]

## Dependencies & Assumptions

- [x] CHK022 Is the deterministic local decision path documented as an MVP assumption? [Assumption, Spec Assumptions]
- [x] CHK023 Are downstream adapters and live retrieval mechanisms explicitly out of scope for this slice? [Assumption, Spec Assumptions]
- [x] CHK024 Is documentation truthfulness tied to runnable commands and verification outcomes? [Completeness, Spec SC-001-SC-007]

## Notes

- Checklist result: PASS. No requirements-quality blockers found before planning.
