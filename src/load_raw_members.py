import logging

import pandas as pd

from src.ingest_members import load_member_files
from src.snowflake_connection import get_snowflake_connection

logger = logging.getLogger(__name__)

RAW_VALUE_COLUMNS = {
    "member_id",
    "member_name",
    "enrollment_date_raw",
    "last_flight_date_raw",
    "tier_code",
    "dob_raw",
    "country",
    "individual_or_corporate",
}

INSERT_SQL = """
INSERT INTO RAW_MEMBER (
    member_id,
    member_name,
    enrollment_date_raw,
    last_flight_date_raw,
    tier_code,
    dob_raw,
    country,
    individual_or_corporate,
    source_file,
    ingestion_batch_id,
    ingestion_timestamp
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
"""


def _to_snowflake_value(column, value):
    """Convert source and metadata values to Snowflake-bindable values."""
    if pd.isna(value):
        return None

    if column in RAW_VALUE_COLUMNS:
        if isinstance(value, pd.Timestamp):
            return value.strftime("%Y-%m-%d")

        return str(value)

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    return value


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def load_raw_members() -> None:
    dataframe = load_member_files()

    records = [
        tuple(
            _to_snowflake_value(column, value)
            for column, value in zip(dataframe.columns, row)
        )
        for row in dataframe.itertuples(index=False, name=None)
    ]

    logger.info("Loading %d member records into RAW_MEMBER", len(records))

    with get_snowflake_connection() as connection:
        cursor = connection.cursor()

        try:
            cursor.executemany(INSERT_SQL, records)
            connection.commit()

            logger.info(
                "Successfully loaded %d records into RAW_MEMBER",
                len(records),
            )
        except Exception:
            connection.rollback()
            logger.exception("Failed to load records into RAW_MEMBER")
            raise
        finally:
            cursor.close()


if __name__ == "__main__":
    configure_logging()
    load_raw_members()
