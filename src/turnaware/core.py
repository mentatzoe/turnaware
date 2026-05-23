"""Internal callable admission core."""

from .models import AdmissionResult, VERDICTS, result_to_dict
from .schema import validate_request, validate_result


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(needle in lowered for needle in needles)


def _classify_text(text: str, *, source: str) -> tuple[str, str] | None:
    if _contains_any(text, ("already handled", "handled this", "posted the fix", "resolved", "no response needed")):
        return "PASS", "Supplied context indicates the requested matter is already handled."
    if _contains_any(text, ("acknowledge", "ack ", "acknowledgement", "saw it")):
        return "ACK", "The trigger calls for visible acknowledgement rather than substantive work."
    if _contains_any(text, ("need clarification", "clarification", "unclear", "ambiguous", "not specified")):
        return "ASK", "The supplied material indicates a clarification is needed before substantive participation."
    if _contains_any(text, ("please implement", "implement", "take this", "assigned", "owner", "proceed")):
        return "SPEAK", "The trigger asks this agent to participate substantively."
    return None


def _confidences(verdict: str) -> dict[str, float]:
    return {candidate: (0.85 if candidate == verdict else 0.05) for candidate in VERDICTS}


def evaluate(request):
    admission_request = validate_request(request)
    checked = [admission_request.trigger.reference]

    decision = _classify_text(admission_request.trigger.content, source="trigger")

    if decision is None:
        for item in admission_request.context:
            checked.append(item.reference)
            decision = _classify_text(item.content, source="context")
            if decision is not None:
                break

    if decision is None:
        decision = (
            "ASK",
            "No supplied context made participation clearly safe; a clarifying question is warranted.",
        )

    verdict, reason = decision
    result = AdmissionResult(
        verdict=verdict,
        confidences=_confidences(verdict),
        context_checked=tuple(checked),
        reasons=(reason,),
        request_id=admission_request.request_id,
    )
    payload = result_to_dict(result)
    validate_result(payload)
    return payload
