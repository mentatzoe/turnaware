"""TurnAware error types and exit codes."""

EXIT_SUCCESS = 0
EXIT_RUNTIME = 1
EXIT_INPUT = 2
EXIT_VALIDATION = 3


class TurnAwareError(Exception):
    """Base error for expected TurnAware failures."""

    label = "turnaware error"


class InputError(TurnAwareError):
    """Raised when input cannot be read or parsed."""

    label = "input error"


class ValidationError(TurnAwareError):
    """Raised when an admission request is invalid."""

    label = "validation error"
