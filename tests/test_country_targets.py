from datetime import datetime

import pandas as pd

from src.transform_members import get_latest_members, split_members_by_country


def test_latest_record_wins():
    data = pd.DataFrame(
        [
            {
                "member_id": "101",
                "member_name": "John Smith",
                "country": "USA",
                "ingestion_timestamp": datetime(2026, 9, 20),
                "enrollment_date": datetime(2020, 1, 1),
                "source_file": "USA.xlsx",
            },
            {
                "member_id": "202",
                "member_name": "John Smith",
                "country": "IND",
                "ingestion_timestamp": datetime(2026, 9, 25),
                "enrollment_date": datetime(2020, 1, 1),
                "source_file": "IND.xlsx",
            },
        ]
    )

    result = get_latest_members(data)

    assert len(result) == 1
    assert result.iloc[0]["country"] == "IND"
    assert result.iloc[0]["member_id"] == "202"


def test_different_members_with_same_id_are_kept_separately():
    data = pd.DataFrame(
        [
            {
                "member_id": "1",
                "member_name": "Mike",
                "country": "AUS",
                "ingestion_timestamp": datetime(2026, 9, 25),
                "enrollment_date": datetime(2020, 1, 1),
                "source_file": "AUS.xlsx",
            },
            {
                "member_id": "1",
                "member_name": "Vikas",
                "country": "IND",
                "ingestion_timestamp": datetime(2026, 9, 25),
                "enrollment_date": datetime(2020, 1, 1),
                "source_file": "IND.xlsx",
            },
        ]
    )

    result = get_latest_members(data)

    assert len(result) == 2


def test_latest_record_is_selected_when_multiple_records_exist():
    data = pd.DataFrame(
        [
            {
                "member_id": "200",
                "member_name": "Alex",
                "country": "USA",
                "ingestion_timestamp": datetime(2026, 9, 20),
                "enrollment_date": datetime(2020, 1, 1),
                "source_file": "USA.xlsx",
            },
            {
                "member_id": "200",
                "member_name": "Alex",
                "country": "AUS",
                "ingestion_timestamp": datetime(2026, 9, 21),
                "enrollment_date": datetime(2020, 1, 1),
                "source_file": "AUS.xlsx",
            },
            {
                "member_id": "200",
                "member_name": "Alex",
                "country": "IND",
                "ingestion_timestamp": datetime(2026, 9, 22),
                "enrollment_date": datetime(2020, 1, 1),
                "source_file": "IND.xlsx",
            },
        ]
    )

    result = get_latest_members(data)

    assert len(result) == 1
    assert result.iloc[0]["country"] == "IND"


def test_country_split_supports_assessment_countries():
    members = pd.DataFrame(
        [
            {"member_id": country, "member_name": country, "country": country}
            for country in ["AUS", "IND", "USA", "PHIL", "CAN"]
        ]
    )

    result = split_members_by_country(members)

    assert set(result) == {"AUS", "IND", "USA", "PHIL", "CAN"}
    assert all(len(country_members) == 1 for country_members in result.values())
