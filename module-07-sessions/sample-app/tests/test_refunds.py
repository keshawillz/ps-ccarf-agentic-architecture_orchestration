from billing.refunds import process_refund


def test_refund_posted_charge():
    result = process_refund("CHG-5501", "duplicate")
    assert result["success"] is True


def test_refund_missing_charge():
    result = process_refund("CHG-0000", "typo")
    assert result["success"] is False
