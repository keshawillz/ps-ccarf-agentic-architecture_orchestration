from billing.limits import needs_supervisor


def test_under_threshold():
    assert needs_supervisor(100.0) is False


def test_over_threshold():
    assert needs_supervisor(900.0) is True
