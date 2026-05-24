"""Admission classifier registry and built-in classifier paths."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .errors import ValidationError
from .models import AdmissionRequest, AdmissionResult, VERDICTS

PRODUCT_CLASSIFIER = "product"
DETERMINISTIC_CLASSIFIER = "deterministic"
SUPPORTED_CLASSIFIERS = (PRODUCT_CLASSIFIER, DETERMINISTIC_CLASSIFIER)


@dataclass(frozen=True)
class ClassifierDecision:
    verdict: str
    confidences: dict[str, float]
    context_checked: tuple[str, ...]
    reasons: tuple[str, ...]


def _lower(text: str) -> str:
    return text.casefold()


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = _lower(text)
    return any(needle in lowered for needle in needles)


def _confidences(verdict: str, *, strength: str = "normal") -> dict[str, float]:
    if strength == "conflict":
        table = {
            "PASS": {"PASS": 0.10, "ACK": 0.10, "ASK": 0.35, "SPEAK": 0.45},
            "ACK": {"PASS": 0.05, "ACK": 0.65, "ASK": 0.15, "SPEAK": 0.15},
            "ASK": {"PASS": 0.05, "ACK": 0.10, "ASK": 0.55, "SPEAK": 0.30},
            "SPEAK": {"PASS": 0.05, "ACK": 0.10, "ASK": 0.20, "SPEAK": 0.65},
        }
        return dict(table[verdict])
    if strength == "low":
        table = {
            "PASS": {"PASS": 0.55, "ACK": 0.10, "ASK": 0.20, "SPEAK": 0.15},
            "ACK": {"PASS": 0.05, "ACK": 0.70, "ASK": 0.10, "SPEAK": 0.15},
            "ASK": {"PASS": 0.05, "ACK": 0.10, "ASK": 0.60, "SPEAK": 0.25},
            "SPEAK": {"PASS": 0.05, "ACK": 0.10, "ASK": 0.15, "SPEAK": 0.70},
        }
        return dict(table[verdict])
    return {candidate: (0.80 if candidate == verdict else round(0.20 / 3, 2)) for candidate in VERDICTS}


class RoomAdmissionClassifier:
    """Built-in admission classifier for supplied shared-work envelopes.

    The classifier is intentionally admission-only: it chooses PASS/ACK/ASK/SPEAK
    and audit evidence, never reply prose.  It inspects the trigger and supplied
    context for assignment, acknowledgement, clarification, completion, and
    contradiction evidence rather than returning on the first substring match.
    """

    def __init__(self, name: str, config: dict[str, Any] | None = None) -> None:
        self.name = name
        self.config = config or {}
        unsupported = set(self.config).difference({"strict"})
        if unsupported:
            names = ", ".join(sorted(unsupported))
            raise ValidationError(f"unsupported classifier_config for {name}: {names}")
        strict = self.config.get("strict", True)
        if not isinstance(strict, bool):
            raise ValidationError(f"classifier_config.strict for {name} must be boolean")

    def classify(self, request: AdmissionRequest) -> ClassifierDecision:
        checked = [request.trigger.reference]
        trigger_text = request.trigger.content
        context_texts: list[tuple[str, str]] = []
        for item in request.context:
            checked.append(item.reference)
            context_texts.append((item.reference, item.content))

        trigger_assignment = self._assignment_signal(trigger_text)
        context_assignment = any(self._assignment_signal(text) for _, text in context_texts)
        ack_request = self._ack_signal(trigger_text)
        ask_signal = self._ask_signal(trigger_text) or any(self._ask_signal(text) for _, text in context_texts)
        pass_signal = self._pass_signal(trigger_text) or any(self._pass_signal(text) for _, text in context_texts)
        corroborated_completion = any(self._completion_support(text) for _, text in context_texts)
        contradiction_refs = tuple(ref for ref, text in context_texts if self._contradiction_signal(text))

        if ask_signal and self._ask_signal(trigger_text):
            return ClassifierDecision(
                verdict="ASK",
                confidences=_confidences("ASK", strength="low"),
                context_checked=tuple(checked),
                reasons=("The trigger asks whether clarification is needed before substantive participation.",),
            )

        if trigger_assignment:
            return ClassifierDecision(
                verdict="SPEAK",
                confidences=_confidences("SPEAK"),
                context_checked=tuple(checked),
                reasons=("The trigger asks this agent to perform substantive work, so visible participation is warranted.",),
            )

        if pass_signal and contradiction_refs:
            return ClassifierDecision(
                verdict="SPEAK" if context_assignment else "ASK",
                confidences=_confidences("SPEAK" if context_assignment else "ASK", strength="conflict"),
                context_checked=tuple(checked),
                reasons=("Resolved-looking language is contradicted by supplied missing-work or missing-evidence context.",),
            )

        if pass_signal and corroborated_completion:
            return ClassifierDecision(
                verdict="PASS",
                confidences=_confidences("PASS", strength="low"),
                context_checked=tuple(checked),
                reasons=("Inspected context corroborates that the requested matter is already complete and no visible participation is needed.",),
            )

        if pass_signal and not corroborated_completion:
            return ClassifierDecision(
                verdict="ASK",
                confidences=_confidences("ASK", strength="conflict"),
                context_checked=tuple(checked),
                reasons=("Resolved-looking language has no corroborating supplied completion context; PASS is not safe.",),
            )

        if ack_request:
            return ClassifierDecision(
                verdict="ACK",
                confidences=_confidences("ACK", strength="low"),
                context_checked=tuple(checked),
                reasons=("The trigger asks for visible acknowledgement rather than substantive work.",),
            )

        if ask_signal:
            return ClassifierDecision(
                verdict="ASK",
                confidences=_confidences("ASK", strength="low"),
                context_checked=tuple(checked),
                reasons=("Supplied material indicates a clarification is needed before substantive participation.",),
            )

        if context_assignment:
            return ClassifierDecision(
                verdict="SPEAK",
                confidences=_confidences("SPEAK", strength="low"),
                context_checked=tuple(checked),
                reasons=("Supplied context assigns substantive work to this agent.",),
            )

        return ClassifierDecision(
            verdict="ASK",
            confidences=_confidences("ASK", strength="low"),
            context_checked=tuple(checked),
            reasons=("No supplied context made participation clearly safe; a clarifying question is warranted.",),
        )

    @staticmethod
    def _assignment_signal(text: str) -> bool:
        return _contains_any(
            text,
            (
                "please implement",
                "implement ",
                "build ",
                "fix ",
                "redo ",
                "complete ",
                "take this",
                "assigned",
                "owner",
                "proceed",
                "comment back with results",
                "report back with results",
                "what's dropping",
                "what is blocking",
            ),
        )

    @staticmethod
    def _ack_signal(text: str) -> bool:
        return _contains_any(text, ("acknowledge", "ack ", "acknowledgement", "confirm receipt", "saw it"))

    @staticmethod
    def _ask_signal(text: str) -> bool:
        return _contains_any(text, ("need clarification", "clarification", "unclear", "ambiguous", "not specified"))

    @staticmethod
    def _pass_signal(text: str) -> bool:
        return _contains_any(
            text,
            ("already handled", "handled this", "posted the fix", "resolved", "no response needed", "complete", "done", "merged", "shipped"),
        )

    @staticmethod
    def _completion_support(text: str) -> bool:
        return _contains_any(text, ("already handled", "posted the fix", "merged", "tests pass", "implemented", "complete", "done", "resolved", "reviewed"))

    @staticmethod
    def _contradiction_signal(text: str) -> bool:
        return _contains_any(
            text,
            (
                "not implemented",
                "not complete",
                "not done",
                "missing",
                "no evidence",
                "evidence is missing",
                "work is missing",
                "blocked",
                "unavailable",
                "failed",
                "failing",
                "still at the start",
                "not the main path",
            ),
        )


def _normalise_config(config: dict[str, Any] | None) -> dict[str, Any] | None:
    if config is None:
        return None
    if not isinstance(config, dict):
        raise ValidationError("classifier_config must be an object when supplied")
    return dict(config)


def get_classifier(name: str | None, config: dict[str, Any] | None = None) -> RoomAdmissionClassifier:
    selected = name or PRODUCT_CLASSIFIER
    if selected not in SUPPORTED_CLASSIFIERS:
        supported = ", ".join(SUPPORTED_CLASSIFIERS)
        raise ValidationError(f"unsupported classifier {selected!r}; supported classifiers: {supported}")
    return RoomAdmissionClassifier(selected, _normalise_config(config))


def classify(request: AdmissionRequest, *, classifier: str | None = None, classifier_config: dict[str, Any] | None = None) -> AdmissionResult:
    selected = classifier or request.classifier or PRODUCT_CLASSIFIER
    config = classifier_config if classifier_config is not None else request.classifier_config
    engine = get_classifier(selected, config)
    decision = engine.classify(request)
    return AdmissionResult(
        classifier=engine.name,
        verdict=decision.verdict,
        confidences=decision.confidences,
        context_checked=decision.context_checked,
        reasons=decision.reasons,
        request_id=request.request_id,
    )
