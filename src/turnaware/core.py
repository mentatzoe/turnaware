"""Internal callable admission core."""

from .classifiers import classify
from .models import result_to_dict
from .schema import validate_request, validate_result


def evaluate(request, *, classifier: str | None = None, classifier_config: dict | None = None):
    """Evaluate one admission request through the selected classifier path."""

    admission_request = validate_request(request)
    result = classify(admission_request, classifier=classifier, classifier_config=classifier_config)
    payload = result_to_dict(result)
    validate_result(payload)
    return payload
