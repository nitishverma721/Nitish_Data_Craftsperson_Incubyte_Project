from src.validate_members import is_valid_date


def test_redemption_date_format():
    assert is_valid_date("2024-01-15") is True


def test_invalid_redemption_date():
    assert is_valid_date("2024-99-99") is False
