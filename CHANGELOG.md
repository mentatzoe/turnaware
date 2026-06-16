# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-06-16

### Added

- **Admission core.** A pre-reply admission gate that returns exactly one of the
  four verdicts `PASS`, `ACK`, `ASK`, or `SPEAK`. `PASS` is a hard stop: no
  ordinary user-visible room message is emitted. Admission results never carry
  reply prose (`message`, `reply`, `draft`, and `content` are forbidden result
  fields), keeping the boundary at admission rather than reply composition.
- **Provider-backed classifier.** A `product` classifier backed by an
  OpenAI-compatible chat-completions client built on the standard library
  (`urllib`), defaulting to OpenRouter. Configuration is security-hardened:
  API keys come from the environment (`OPENROUTER_API_KEY` or
  `TURNAWARE_CLASSIFIER_API_KEY`), the model is set via
  `TURNAWARE_CLASSIFIER_MODEL`, and the base URL is overridable via
  `TURNAWARE_CLASSIFIER_BASE_URL`.
- **Classifier rubric and live model selection.** A documented rubric for the
  four-verdict decision, with `gemini-3.1-flash-lite` as the default live model
  selection (plus an open-weight alternative captured in the selection evidence).
- **Transport-neutral channel adapter.** A `turnaware-channel` adapter that emits
  a transport-neutral verdict-plus-silent JSON envelope by default, exposes a
  generic suppression token for any transport, and offers a `cc-connect` preset
  (`--format cc-connect`) emitting the `CC_CONNECT_SILENT_PASS` sentinel.
- **CLI.** A `turnaware` console script with an `admit` command that reads a
  request from stdin and writes the admission verdict as JSON.
- **Packaging.** A stdlib-only distribution (zero runtime dependencies) that
  installs cleanly in one line and ships the `turnaware` and `turnaware-channel`
  console scripts.
- **CI.** A fully offline GitHub Actions matrix (Python 3.11/3.12/3.13) running
  the `unittest` suite plus a clean-install packaging job that verifies the
  public surface and console scripts.
- **Integration guide.** Documentation covering configuration and adapter
  integration for embedding the admission gate.

[Unreleased]: https://github.com/mentatzoe/turnaware/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/mentatzoe/turnaware/releases/tag/v0.1.0
