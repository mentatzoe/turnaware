# Tasks: Core CLI MVP

**Input**: Design documents from `/specs/001-core-cli-mvp/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/admission-cli.md, quickstart.md
**Tests**: Required by spec FR-015 and FR-016. Test tasks must be written before corresponding implementation tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish package skeleton, fixture locations, and repository hygiene.

- [X] T001 Create Python package metadata and console script entry in `pyproject.toml`
- [X] T002 Create source package skeleton in `src/turnaware/__init__.py`, `src/turnaware/__main__.py`, `src/turnaware/cli.py`, `src/turnaware/core.py`, `src/turnaware/errors.py`, `src/turnaware/models.py`, and `src/turnaware/schema.py`
- [X] T003 Create test package and fixture directories in `tests/__init__.py` and `tests/fixtures/.gitkeep`
- [X] T004 Verify `.gitignore` contains Python build, cache, virtualenv, log, and local environment patterns

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add deterministic request fixtures and test helpers used by every user story.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 [P] Create PASS fixture in `tests/fixtures/pass.json`
- [X] T006 [P] Create ACK fixture in `tests/fixtures/ack.json`
- [X] T007 [P] Create ASK fixture in `tests/fixtures/ask.json`
- [X] T008 [P] Create SPEAK fixture in `tests/fixtures/speak.json`
- [X] T009 Create fixture-loading helper functions in `tests/test_core.py`

**Checkpoint**: Fixtures exist for all four verdicts and are ready for failing tests.

---

## Phase 3: User Story 1 - Evaluate Admission From a Supplied Context Package (Priority: P1) MVP

**Goal**: Developers can evaluate valid admission requests through the core and CLI, receiving auditable JSON verdicts for all four verdict categories.

**Independent Test**: `python -m unittest tests.test_core tests.test_cli` verifies all four fixtures through the core plus stdin/file CLI success paths.

### Tests for User Story 1

- [X] T010 [US1] Add failing core verdict tests for all four fixtures in `tests/test_core.py`
- [X] T011 [P] [US1] Add failing successful CLI stdin/file tests in `tests/test_cli.py`
- [X] T012 [P] [US1] Add failing result schema tests for verdict values, confidence keys, and audit fields in `tests/test_schema.py`

### Implementation for User Story 1

- [X] T013 [US1] Implement admission dataclasses and result serialization in `src/turnaware/models.py`
- [X] T014 [US1] Implement request validation and result schema helpers in `src/turnaware/schema.py`
- [X] T015 [US1] Implement deterministic verdict evaluation and confidence generation in `src/turnaware/core.py`
- [X] T016 [US1] Implement CLI success path for stdin/file JSON input in `src/turnaware/cli.py` and `src/turnaware/__main__.py`
- [X] T017 [US1] Export the callable core boundary from `src/turnaware/__init__.py`

**Checkpoint**: User Story 1 is independently functional and returns valid verdict JSON for every committed fixture.

---

## Phase 4: User Story 2 - Preserve Hard-Stop PASS and Context Truth (Priority: P2)

**Goal**: PASS results contain no visible reply content, and `context_checked` names only inspected trigger/context references.

**Independent Test**: `python -m unittest tests.test_core tests.test_schema` verifies PASS hard-stop output and context subset truthfulness.

### Tests for User Story 2

- [X] T018 [US2] Add failing PASS hard-stop assertions in `tests/test_core.py`
- [X] T019 [P] [US2] Add failing `context_checked` truthfulness assertions in `tests/test_schema.py`

### Implementation for User Story 2

- [X] T020 [US2] Enforce forbidden reply-field exclusion during result serialization in `src/turnaware/models.py`
- [X] T021 [US2] Ensure inspected context tracking only emits request-derived references in `src/turnaware/core.py`

**Checkpoint**: User Stories 1 and 2 both work independently without violating PASS or context-truth invariants.

---

## Phase 5: User Story 3 - Fail Clearly on Invalid Input (Priority: P3)

**Goal**: Developers and host harnesses can distinguish invalid input or unreadable files from successful PASS verdicts.

**Independent Test**: `python -m unittest tests.test_cli tests.test_schema` verifies malformed JSON, missing trigger, duplicate context IDs, and missing file behavior.

### Tests for User Story 3

- [X] T022 [P] [US3] Add failing validation error tests in `tests/test_schema.py`
- [X] T023 [US3] Add failing CLI failure tests for malformed stdin, missing trigger, and missing input file in `tests/test_cli.py`

### Implementation for User Story 3

- [X] T024 [US3] Implement typed TurnAware exceptions and exit-code constants in `src/turnaware/errors.py`
- [X] T025 [US3] Wire validation, input, and runtime failure handling to stderr and exit codes in `src/turnaware/cli.py`

**Checkpoint**: All user stories are independently functional and invalid input cannot be confused with PASS.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Keep documentation truthful and verify the committed product path.

- [X] T026 Update runnable CLI/core documentation in `README.md`
- [X] T027 Validate quickstart commands in `specs/001-core-cli-mvp/quickstart.md`
- [X] T028 Run `python3 -m unittest` and record results
- [X] T029 Run CLI smoke checks for stdin success, file success, and invalid input behavior
- [X] T030 Review `specs/001-core-cli-mvp/tasks.md` and mark completed tasks as `[X]`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Phase 1 completion and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2 and is the MVP.
- **User Story 2 (Phase 4)**: Depends on User Story 1 result structure.
- **User Story 3 (Phase 5)**: Depends on User Story 1 CLI and schema boundaries.
- **Polish (Phase 6)**: Depends on all user stories selected for delivery.

### User Story Dependencies

- **US1**: Required MVP slice and base for CLI/core contract.
- **US2**: Builds on US1 outputs but remains independently testable through PASS/context assertions.
- **US3**: Builds on US1 CLI/schema but remains independently testable through invalid input commands.

### Within Each User Story

- Tests must be written before implementation.
- Models and schema precede core logic.
- Core logic precedes CLI wiring.
- CLI failure handling depends on typed exceptions.
- Mark tasks complete in this file as implementation progresses.

### Parallel Opportunities

- T005-T008 can run in parallel because each fixture is a separate file.
- T011 and T012 can run in parallel after T010 because they touch different test files.
- T019 can run in parallel with T018 because it touches `tests/test_schema.py` while T018 touches `tests/test_core.py`.
- T022 can run in parallel with early US3 planning, but T023 should follow once CLI expectations are known.

## Parallel Example: User Story 1

```text
Task: "Add failing successful CLI stdin/file tests in tests/test_cli.py"
Task: "Add failing result schema tests for verdict values, confidence keys, and audit fields in tests/test_schema.py"
```

## Implementation Strategy

### MVP First

1. Complete Setup and Foundational phases.
2. Complete US1 tests and implementation.
3. Validate US1 independently with all four verdict fixtures.

### Incremental Delivery

1. Add US2 PASS/context truth tests and enforcement.
2. Add US3 invalid-input tests and failure handling.
3. Update docs only after commands are runnable.
4. Run the full verification suite before reporting completion.
