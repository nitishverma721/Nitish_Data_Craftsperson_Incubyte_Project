import csv
import hashlib
import logging
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import pandas as pd

from src.config import ASSESSMENT_DIR, COUNTRY_CODE_ALIASES, SOURCE_CONFIG

logger = logging.getLogger(__name__)

RAW_COLUMNS = [
    "member_id",
    "member_name",
    "enrollment_date_raw",
    "last_flight_date_raw",
    "tier_code",
    "agent_name",
    "state",
    "post_code_raw",
    "dob_raw",
    "active_member",
    "country",
    "individual_or_corporate",
]

PIPE_COLUMN_MAPPING = {
    "Member_Name": "member_name",
    "Member_Id": "member_id",
    "Enrollment_Date": "enrollment_date_raw",
    "Last_Flight_Date": "last_flight_date_raw",
    "Tier_Code": "tier_code",
    "Agent_Name": "agent_name",
    "State": "state",
    "Country": "country",
    "Post_Code": "post_code_raw",
    "DOB": "dob_raw",
    "Is_Active": "active_member",
}

REQUIRED_PIPE_COLUMNS = {
    "Member_Name",
    "Member_Id",
    "Enrollment_Date",
}


def configure_logging() -> None:
    """Configure application logging for local ingestion runs."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def read_source_file(file_name: str, file_path: Path | None = None) -> pd.DataFrame:
    """Read a configured source file and apply its source-specific mapping."""
    config = SOURCE_CONFIG[file_name]
    file_path = file_path or ASSESSMENT_DIR / file_name

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


def parse_pipe_delimited_member_text(contents: str) -> pd.DataFrame:
    """Parse the assessment's pipe-delimited header/detail member format."""
    header = None
    records = []

    for fields in csv.reader(StringIO(contents), delimiter="|"):
        fields = [field.strip() for field in fields]
        if not fields or all(not field for field in fields):
            continue

        if fields[0] == "":
            fields = fields[1:]
        if not fields:
            continue

        record_type, *values = fields

        if record_type == "H":
            header = values
            missing_columns = REQUIRED_PIPE_COLUMNS - set(header)
            if missing_columns:
                raise ValueError(
                    "Member flat file is missing required headers: "
                    f"{sorted(missing_columns)}"
                )
            continue

        if record_type != "D":
            continue
        if header is None:
            raise ValueError("Member detail record appeared before header record")

        if len(values) == len(header) + 1 and values[-1] == "":
            values.pop()
        if len(values) != len(header):
            raise ValueError(
                "Member detail record has "
                f"{len(values)} values; expected {len(header)}"
            )

        source_record = dict(zip(header, values))
        member_record = {
            target: source_record[source]
            for source, target in PIPE_COLUMN_MAPPING.items()
            if source in source_record
        }
        country = member_record.get("country")
        if country:
            normalized_country = country.strip().upper()
            member_record["country"] = COUNTRY_CODE_ALIASES.get(
                normalized_country,
                normalized_country,
            )
        records.append(member_record)

    if header is None:
        raise ValueError("Member flat file does not contain a header record")

    member_df = pd.DataFrame(records)
    for column in RAW_COLUMNS:
        if column not in member_df.columns:
            member_df[column] = None

    return member_df[RAW_COLUMNS]


def read_pipe_delimited_member_file(file_path: Path) -> pd.DataFrame:
    """Read and parse a pipe-delimited member file from disk."""
    if not file_path.exists():
        raise FileNotFoundError(f"Source file not found: {file_path}")

    return parse_pipe_delimited_member_text(
        file_path.read_text(encoding="utf-8")
    )


def create_ingestion_batch_id(source_files: list[Path]) -> str:
    """Create a stable batch ID from source file names and contents."""
    digest = hashlib.sha256()

    for source_path in sorted(source_files, key=lambda path: str(path.resolve())):
        digest.update(source_path.name.encode("utf-8"))
        with source_path.open("rb") as source_file:
            for chunk in iter(lambda: source_file.read(1024 * 1024), b""):
                digest.update(chunk)

    return str(uuid5(NAMESPACE_URL, digest.hexdigest()))


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


def load_member_files(source_files: list[Path] | None = None) -> pd.DataFrame:
    """Read all configured member files and combine them into one raw dataset."""
    if source_files is None:
        source_files = [ASSESSMENT_DIR / file_name for file_name in SOURCE_CONFIG]
    if not source_files:
        raise ValueError("At least one member source file must be provided")

    batch_id = create_ingestion_batch_id(source_files)
    ingestion_timestamp = datetime.now(timezone.utc)

    logger.info("Starting member ingestion. batch_id=%s", batch_id)

    dataframes = []

    for source_path in source_files:
        file_name = source_path.name
        if source_path.suffix.lower() == ".xlsx":
            dataframe = read_source_file(file_name, source_path)
        else:
            dataframe = read_pipe_delimited_member_file(source_path)

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
