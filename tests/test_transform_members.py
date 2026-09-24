from datetime import date

import pandas as pd

from src.transform_members import (
    calculate_age,
    calculate_stale_member,
    parse_source_date,
    transform_members,
)


def test_parse_iso_date():
    result = parse_source_date("2022-08-01")

    assert result == pd.Timestamp("2022-08-01")


def test_parse_numeric_style_date():
    result = parse_source_date("12282021")

    assert result == pd.Timestamp("2021-12-28")


def test_parse_timestamp_date():
    result = parse_source_date(
        pd.Timestamp("2022-08-01")
    )

    assert result == pd.Timestamp("2022-08-01")


def test_parse_python_date():
    result = parse_source_date(
        date(2022, 8, 1)
    )

    assert result == pd.Timestamp("2022-08-01")


def test_missing_date_returns_null():
    result = parse_source_date(None)

    assert pd.isna(result)


def test_invalid_date_returns_null():
    result = parse_source_date("2021-13-13")

    assert pd.isna(result)


def test_age_calculation():
    dob = pd.Timestamp("2000-09-24")

    assert calculate_age(dob, date(2026, 9, 24)) == 26


def test_age_before_birthday():
    dob = pd.Timestamp("2000-12-01")

    assert calculate_age(dob, date(2026, 9, 24)) == 25


def test_stale_member():
    flight_date = pd.Timestamp("2026-06-01")

    assert calculate_stale_member(
        flight_date,
        date(2026, 9, 24),
    ) is True


def test_recent_member_is_not_stale():
    flight_date = pd.Timestamp("2026-08-01")

    assert calculate_stale_member(
        flight_date,
        date(2026, 9, 24),
    ) is False


def test_missing_flight_date_returns_null():
    assert calculate_stale_member(
        pd.NaT,
        date(2026, 9, 24),
    ) is None


def test_member_transformation():
    raw_df = pd.DataFrame(
        [
            {
                "member_id": "101",
                "member_name": "Test Member",
                "enrollment_date_raw": "2022-01-10",
                "last_flight_date_raw": "2026-06-01",
                "tier_code": "GLD",
                "dob_raw": "2000-01-15",
                "country": "USA",
                "individual_or_corporate": None,
                "source_file": "USA.xlsx",
                "ingestion_batch_id": "test-batch",
                "ingestion_timestamp": pd.Timestamp("2026-09-24"),
            }
        ]
    )

    result = transform_members(
        raw_df,
        date(2026, 9, 24),
    )

    assert len(result) == 1
    assert result.loc[0, "member_id"] == "101"
    assert result.loc[0, "age"] == 26
    assert result.loc[0, "stale_member"] is True
