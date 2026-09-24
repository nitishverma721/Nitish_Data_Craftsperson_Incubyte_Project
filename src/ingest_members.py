import logging
from datetime import datetime, timezone
from uuid import uuid4

import pandas as pd

from src.config import ASSESSMENT_DIR, SOURCE_CONFIG

logger = logging.getLogger(__name__)

RAW_COLUMNS = [
    "member_id",
    "member_name",
    "enrollment_date_raw",
    "last_flight_date_raw",
    "tier_code",
    "dob_raw",
    "country",
    "individual_or_corporate",
]


def configure_logging() -> None:
    """Configure application logging for local ingestion runs."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def read_source_file(file_name: str) -> pd.DataFrame:
    """Read a configured source file and apply its source-specific mapping."""
    config = SOURCE_CONFIG[file_name]
    file_path = ASSESSMENT_DIR / file_name

    logger.info("Reading source file: %s", file_name)

    if not file_path.exists():
        raise FileNotFoundError(f"Source file not found: {file_path}")

    source_df = pd.read_excel(file_path)

    logger.info(
        "Read %d records from %s",
        len(source_df),
        file_name,
    )

    missing_columns = set(config["column_mapping"]) - set(source_df.columns)

    if missing_columns:
        raise ValueError(
            f"{file_name} is missing expected columns: "
            f"{sorted(missing_columns)}"
        )

    member_df = source_df.rename(columns=config["column_mapping"]).copy()

    member_df["country"] = config["country"]

    for column in RAW_COLUMNS:
        if column not in member_df.columns:
            member_df[column] = None

    return member_df[RAW_COLUMNS]


def add_ingestion_metadata(
    dataframe: pd.DataFrame,
    file_name: str,
    batch_id: str,
    ingestion_timestamp: datetime,
) -> pd.DataFrame:
    """Add metadata required to trace records back to an ingestion batch."""
    dataframe = dataframe.copy()

    dataframe["source_file"] = file_name
    dataframe["ingestion_batch_id"] = batch_id
    dataframe["ingestion_timestamp"] = ingestion_timestamp

    return dataframe


def load_member_files() -> pd.DataFrame:
    """Read all configured member files and combine them into one raw dataset."""
    batch_id = str(uuid4())
    ingestion_timestamp = datetime.now(timezone.utc)

    logger.info("Starting member ingestion. batch_id=%s", batch_id)

    dataframes = []

    for file_name in SOURCE_CONFIG:
        dataframe = read_source_file(file_name)

        dataframe = add_ingestion_metadata(
            dataframe=dataframe,
            file_name=file_name,
            batch_id=batch_id,
            ingestion_timestamp=ingestion_timestamp,
        )

        dataframes.append(dataframe)

    combined_df = pd.concat(
        [df.dropna(axis=1, how="all") for df in dataframes if not df.empty],
        ignore_index=True,
    ).reindex(columns=dataframes[0].columns)

    logger.info(
        "Member ingestion completed. batch_id=%s records=%d",
        batch_id,
        len(combined_df),
    )

    return combined_df


if __name__ == "__main__":
    configure_logging()
    load_member_files()
