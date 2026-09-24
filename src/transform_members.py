import logging
from datetime import date

import pandas as pd

logger = logging.getLogger(__name__)

STAGING_COLUMNS = [
    "member_id",
    "member_name",
    "enrollment_date",
    "last_flight_date",
    "tier_code",
    "dob",
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

    for column in ["enrollment_date_raw", "last_flight_date_raw", "dob_raw"]:
        staging_df[column.replace("_raw", "")] = staging_df[column].apply(
            parse_source_date
        )

    staging_df["age"] = staging_df["dob"].apply(
        lambda value: calculate_age(value, as_of_date)
    )

    staging_df["stale_member"] = staging_df["last_flight_date"].apply(
        lambda value: calculate_stale_member(value, as_of_date)
    ).astype(object)

    staging_df = staging_df.rename(
        columns={
            "enrollment_date": "enrollment_date",
            "last_flight_date": "last_flight_date",
        }
    )

    staging_df = staging_df[STAGING_COLUMNS]

    logger.info(
        "Member staging transformation completed. records=%d",
        len(staging_df),
    )

    return staging_df
