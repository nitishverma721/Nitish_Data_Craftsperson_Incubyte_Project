from src.load_redemptions import create_redemption_batch_id
from src.validate_members import is_valid_date


def test_redemption_date_format():
    assert is_valid_date("2024-01-15") is True


def test_assessment_redemption_date_format():
    assert is_valid_date("20240115") is True


def test_invalid_redemption_date():
    assert is_valid_date("2024-99-99") is False


def test_redemption_batch_id_is_stable_for_same_payload():
    payload = {
        "member_id": "223457",
        "feed_date": "20240115",
        "redemptions": [],
    }

    assert create_redemption_batch_id("redemption.json", payload) == (
        create_redemption_batch_id("redemption.json", payload)
    )
