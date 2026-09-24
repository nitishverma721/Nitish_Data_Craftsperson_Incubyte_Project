import pandas as pd

from src.ingest_members import RAW_COLUMNS, read_source_file


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
