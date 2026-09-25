from datetime import datetime

import pandas as pd


def get_latest_members(df: pd.DataFrame) -> pd.DataFrame:
    """Return the latest record for each member."""
    return (
        df.sort_values(
            ["ingestion_timestamp", "enrollment_date", "source_file"],
            ascending=[False, False, False],
        )
        .drop_duplicates(
            subset=["member_id", "member_name"],
            keep="first",
        )
        .reset_index(drop=True)
    )


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
                "member_id": "101",
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
