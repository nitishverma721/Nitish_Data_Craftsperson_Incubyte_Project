import logging
from datetime import date, datetime
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_FILE = PROJECT_ROOT / "sql" / "05_validate_members.sql"

SUPPORTED_DATE_FORMATS = (
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M:%S",
    "%Y%m%d",
    "%m%d%Y",
)


def is_valid_date(value) -> bool:
    """Return True when the value matches a supported source date format."""
    if value is None or value == "":
        return False

    value = str(value).strip()

    for date_format in SUPPORTED_DATE_FORMATS:
        try:
            datetime.strptime(value, date_format)
            return True
        except ValueError:
            continue

    return False


def has_valid_date_sequence(
    enrollment_date: date | None,
    last_flight_date: date | None,
) -> bool:
    """Return False when enrollment occurs after the last flight."""
    if enrollment_date is None or last_flight_date is None:
        return True

    return enrollment_date <= last_flight_date


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def validate_members() -> None:
    from src.snowflake_connection import get_snowflake_connection

    logger.info("Starting member data quality validation.")

    if not SQL_FILE.exists():
        raise FileNotFoundError(f"SQL file not found: {SQL_FILE}")

    with get_snowflake_connection() as connection:
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                SELECT ingestion_batch_id
                FROM RAW_MEMBER
                GROUP BY ingestion_batch_id
                ORDER BY MAX(ingestion_timestamp) DESC
                LIMIT 1
                """
            )

            result = cursor.fetchone()

            if not result:
                logger.warning("No member records found in RAW_MEMBER.")
                return

            batch_id = result[0]

            logger.info(
                "Validating member ingestion batch: %s",
                batch_id,
            )

            cursor.execute(
                "DELETE FROM DQ_MEMBER_VALIDATION "
                "WHERE ingestion_batch_id = %s",
                (batch_id,),
            )

            validation_sql = SQL_FILE.read_text(encoding="utf-8")
            validation_sql = validation_sql.replace(
                "{batch_id}",
                batch_id,
            )

            cursor.execute(validation_sql)
            connection.commit()

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS failed_records,
                    COUNT(DISTINCT member_id) AS affected_members
                FROM DQ_MEMBER_VALIDATION
                WHERE ingestion_batch_id = %s
                  AND validation_status = 'FAILED'
                """,
                (batch_id,),
            )

            failed_records, affected_members = cursor.fetchone()

            logger.info(
                "Validation completed. failed_records=%d affected_members=%d",
                failed_records,
                affected_members,
            )

        except Exception:
            connection.rollback()
            logger.exception("Member data quality validation failed.")
            raise

        finally:
            cursor.close()


if __name__ == "__main__":
    configure_logging()
    validate_members()
