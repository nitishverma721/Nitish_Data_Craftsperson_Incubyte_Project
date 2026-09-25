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


def test_parse_assessment_compact_date():
    result = parse_source_date("20101012")

    assert result == pd.Timestamp("2010-10-12")


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


def test_transform_parses_assessment_compact_dates_and_profile_fields():
    raw_df = pd.DataFrame(
        [
            {
                "member_id": "223457",
                "member_name": "Elena",
                "enrollment_date_raw": "20101012",
                "last_flight_date_raw": "20121013",
                "tier_code": "GLD",
                "agent_name": "Sam",
                "state": "CA",
                "post_code_raw": "90210",
                "dob_raw": "03051985",
                "active_member": "A",
                "country": "USA",
                "source_file": "member.dat",
                "ingestion_batch_id": "batch-1",
                "ingestion_timestamp": pd.Timestamp("2026-09-25"),
            }
        ]
    )

    result = transform_members(raw_df, date(2026, 9, 25))

    assert result.loc[0, "enrollment_date"] == pd.Timestamp("2010-10-12")
    assert result.loc[0, "last_flight_date"] == pd.Timestamp("2012-10-13")
    assert result.loc[0, "dob"] == pd.Timestamp("1985-03-05")
    assert result.loc[0, "age"] == 41
    assert result.loc[0, "post_code"] == 90210
    assert result.loc[0, "agent_name"] == "Sam"
    assert result.loc[0, "active_member"] == "A"


def test_transform_quarantines_duplicate_member_names_in_same_batch():
    raw_df = pd.DataFrame(
        [
            {
                "member_id": "1",
                "member_name": "Mike",
                "enrollment_date_raw": "2022-01-01",
                "last_flight_date_raw": "2022-08-01",
                "tier_code": "GLD",
                "dob_raw": None,
                "country": "AUS",
                "source_file": "AUS.xlsx",
                "ingestion_batch_id": "same-batch",
                "ingestion_timestamp": pd.Timestamp("2026-09-25"),
            },
            {
                "member_id": "3",
                "member_name": " Mike ",
                "enrollment_date_raw": "2021-12-28",
                "last_flight_date_raw": "2021-12-30",
                "tier_code": "GLD",
                "dob_raw": None,
                "country": "USA",
                "source_file": "USA.xlsx",
                "ingestion_batch_id": "same-batch",
                "ingestion_timestamp": pd.Timestamp("2026-09-25"),
            },
        ]
    )

    result = transform_members(raw_df, date(2026, 9, 25))

    assert result.empty


def test_assessment_workbooks_exclude_invalid_and_duplicate_key_rows():
    from src.ingest_members import load_member_files

    result = transform_members(
        load_member_files(),
        date(2026, 9, 25),
    )

    assert len(result) == 6
    assert result["country"].value_counts().to_dict() == {
        "IND": 3,
        "AUS": 1,
        "USA": 2,
    }
    assert "Jonnathan" not in set(result["member_name"])
    assert "Mike" not in set(result["member_name"])


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
