from datetime import date

import pandas as pd

from src.validate_members import (
    has_valid_date_sequence,
    is_valid_date,
)


def test_invalid_enrollment_date():
    assert is_valid_date("2021-13-13") is False


def test_valid_enrollment_date():
    assert is_valid_date("2022-05-11") is True


def test_assessment_yyyy_mm_dd_compact_date():
    assert is_valid_date("20101012") is True


def test_assessment_dob_compact_date():
    assert is_valid_date("03051985") is True


def test_missing_enrollment_date():
    assert is_valid_date(None) is False


def test_invalid_last_flight_date():
    assert is_valid_date("2022-99-99") is False


def test_invalid_dob():
    assert is_valid_date("1998-15-10") is False


def test_valid_date_sequence():
    assert has_valid_date_sequence(
        date(2022, 1, 1),
        date(2022, 6, 15),
    ) is True


def test_invalid_date_sequence():
    assert has_valid_date_sequence(
        date(2022, 6, 15),
        date(2022, 1, 1),
    ) is False


def test_missing_date_sequence_is_valid():
    assert has_valid_date_sequence(
        date(2022, 1, 1),
        None,
    ) is True
