import logging
from datetime import date

import pandas as pd

from src.config import COUNTRY_CODE_ALIASES, SUPPORTED_COUNTRIES

logger = logging.getLogger(__name__)

STAGING_COLUMNS = [
    "member_id",
    "member_name",
    "enrollment_date",
    "last_flight_date",
    "tier_code",
    "agent_name",
    "state",
    "post_code",
    "dob",
    "active_member",
    "country",
    "individual_or_corporate",
    "age",
    "stale_member",
    "source_file",
    "ingestion_batch_id",
    "ingestion_timestamp",
]


def parse_source_date(value):
    """
    Convert source date values into a consistent date representation.

    Different source files use different date formats, so parsing is
    intentionally handled before the data reaches the staging layer.
    """
    if pd.isna(value) or value == "":
        return pd.NaT

    if isinstance(value, pd.Timestamp):
        return value.normalize()

    if isinstance(value, date):
        return pd.Timestamp(value)

    value = str(value).strip()

    # ISO-style dates such as 2021-08-01.
    parsed = pd.to_datetime(
        value,
        format="%Y-%m-%d",
        errors="coerce",
    )

    if not pd.isna(parsed):
        return parsed

    # Assessment feed format such as 20101012.
    parsed = pd.to_datetime(
        value,
        format="%Y%m%d",
        errors="coerce",
    )

    if not pd.isna(parsed):
        return parsed

    # Timestamp-like source strings.
    parsed = pd.to_datetime(
        value,
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce",
    )

    if not pd.isna(parsed):
        return parsed

    # Source values such as 6152022 or 12282021.
    parsed = pd.to_datetime(
        value,
        format="%m%d%Y",
        errors="coerce",
    )

    return parsed


def calculate_age(dob, as_of_date: date) -> int | None:
    """Calculate completed years of age as of the supplied date."""
    if pd.isna(dob):
        return None

    birth_date = dob.date() if isinstance(dob, pd.Timestamp) else dob

    age = as_of_date.year - birth_date.year

    if (as_of_date.month, as_of_date.day) < (
        birth_date.month,
        birth_date.day,
    ):
        age -= 1

    return age


def calculate_stale_member(
    last_flight_date,
    as_of_date: date,
) -> bool | None:
    """
    Mark a member stale when more than 90 days have passed
    since the last available flight date.
    """
    if pd.isna(last_flight_date):
        return None

    flight_date = (
        last_flight_date.date()
        if isinstance(last_flight_date, pd.Timestamp)
        else last_flight_date
    )

    return (as_of_date - flight_date).days > 90


def transform_members(
    raw_df: pd.DataFrame,
    as_of_date: date,
) -> pd.DataFrame:
    """Transform canonical raw member data into staging format."""
    logger.info("Starting member staging transformation. records=%d", len(raw_df))

    staging_df = raw_df.copy()

    for column in [
        "agent_name",
        "state",
        "post_code_raw",
        "active_member",
        "individual_or_corporate",
    ]:
        if column not in staging_df.columns:
            staging_df[column] = None

    for column in ["enrollment_date_raw", "last_flight_date_raw", "dob_raw"]:
        staging_df[column.replace("_raw", "")] = staging_df[column].apply(
            parse_source_date
        )

    staging_df["post_code"] = pd.to_numeric(
        staging_df["post_code_raw"],
        errors="coerce",
    )

    staging_df["country"] = (
        staging_df["country"].astype("string").str.strip().str.upper()
    ).replace(COUNTRY_CODE_ALIASES)

    member_name_keys = (
        staging_df["member_name"].astype("string").str.strip().str.casefold()
    )
    duplicate_name_rows = pd.DataFrame(
        {
            "ingestion_batch_id": staging_df["ingestion_batch_id"],
            "member_name_key": member_name_keys,
        },
        index=staging_df.index,
    ).duplicated(
        subset=["ingestion_batch_id", "member_name_key"],
        keep=False,
    )
    valid_rows = (
        staging_df["member_id"].notna()
        & member_name_keys.notna()
        & member_name_keys.ne("")
        & staging_df["enrollment_date"].notna()
        & staging_df["country"].isin(SUPPORTED_COUNTRIES)
        & ~duplicate_name_rows
    )
    staging_df = staging_df.loc[valid_rows].copy()

    staging_df["age"] = staging_df["dob"].apply(
        lambda value: calculate_age(value, as_of_date)
    )

    staging_df["stale_member"] = staging_df["last_flight_date"].apply(
        lambda value: calculate_stale_member(value, as_of_date)
    ).astype(object)

    staging_df = staging_df[STAGING_COLUMNS]

    logger.info(
        "Member staging transformation completed. records=%d",
        len(staging_df),
    )

    return staging_df


def get_latest_members(member_df: pd.DataFrame) -> pd.DataFrame:
    """Select the most recent record for each assessment Member Name key."""
    latest_df = member_df.assign(
        _member_name_key=(
            member_df["member_name"].astype("string").str.strip().str.casefold()
        )
    )
    return (
        latest_df.sort_values(
            ["ingestion_timestamp", "enrollment_date", "source_file"],
            ascending=[False, False, False],
            na_position="last",
        )
        .drop_duplicates(
            subset=["_member_name_key"],
            keep="first",
        )
        .drop(columns="_member_name_key")
        .reset_index(drop=True)
    )


def split_members_by_country(member_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Split latest member records using the configured country targets."""
    return {
        country: member_df.loc[member_df["country"] == country].reset_index(
            drop=True
        )
        for country in sorted(SUPPORTED_COUNTRIES)
    }
