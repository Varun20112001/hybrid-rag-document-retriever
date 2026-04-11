from document.tasks import _is_recoverable_error


def test_retry_classifier_non_recoverable():
    assert _is_recoverable_error(ValueError("bad input")) is False


def test_retry_classifier_recoverable():
    assert _is_recoverable_error(TimeoutError("timeout")) is True
