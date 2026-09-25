import pandas as pd

from src.ingest_members import (
    RAW_COLUMNS,
    create_ingestion_batch_id,
    parse_pipe_delimited_member_text,
    read_source_file,
)


def test_aus_source_mapping():
    dataframe = read_source_file("AUS.xlsx")

    assert len(dataframe) == 3
    assert list(dataframe.columns) == RAW_COLUMNS
    assert dataframe["country"].unique().tolist() == ["AUS"]
    assert dataframe["member_id"].notna().all()
    assert dataframe["member_name"].notna().all()


def test_ind_source_mapping():
    dataframe = read_source_file("IND.xlsx")

    assert len(dataframe) == 3
    assert list(dataframe.columns) == RAW_COLUMNS
    assert dataframe["country"].unique().tolist() == ["IND"]
    assert dataframe["member_id"].notna().all()
    assert dataframe["member_name"].notna().all()


def test_usa_source_mapping():
    dataframe = read_source_file("USA.xlsx")

    assert len(dataframe) == 3
    assert list(dataframe.columns) == RAW_COLUMNS
    assert dataframe["country"].unique().tolist() == ["USA"]
    assert dataframe["member_id"].notna().all()
    assert dataframe["member_name"].notna().all()


def test_all_source_files_can_be_loaded():
    from src.ingest_members import load_member_files

    dataframe = load_member_files()

    assert len(dataframe) == 9
    assert set(dataframe["country"]) == {"AUS", "IND", "USA"}


def test_assessment_pipe_file_maps_fields_and_country_alias():
    contents = (
        "|H|Member_Name|Member_Id|Enrollment_Date|Last_Flight_Date|"
        "Tier_Code|Agent_Name|State|Country|DOB|Is_Active\n"
        "|D|Elena|223457|20101012|20121013|GLD|Sam|CA|AU|03051985|A\n"
    )

    dataframe = parse_pipe_delimited_member_text(contents)

    assert len(dataframe) == 1
    assert dataframe.loc[0, "member_id"] == "223457"
    assert dataframe.loc[0, "enrollment_date_raw"] == "20101012"
    assert dataframe.loc[0, "last_flight_date_raw"] == "20121013"
    assert dataframe.loc[0, "agent_name"] == "Sam"
    assert dataframe.loc[0, "state"] == "CA"
    assert dataframe.loc[0, "dob_raw"] == "03051985"
    assert dataframe.loc[0, "active_member"] == "A"
    assert dataframe.loc[0, "country"] == "AUS"


def test_batch_id_is_repeatable_for_same_source_content(tmp_path):
    source_file = tmp_path / "members.dat"
    source_file.write_text("sample feed", encoding="utf-8")

    first_batch_id = create_ingestion_batch_id([source_file])
    repeated_batch_id = create_ingestion_batch_id([source_file])

    assert first_batch_id == repeated_batch_id

    source_file.write_text("updated feed", encoding="utf-8")
    assert create_ingestion_batch_id([source_file]) != first_batch_id
