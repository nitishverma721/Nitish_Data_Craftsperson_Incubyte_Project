import logging
from pathlib import Path

from src.snowflake_connection import get_snowflake_connection

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_FILE = PROJECT_ROOT / "sql" / "03_transform_member.sql"


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def load_staging_members(batch_id: str | None = None) -> None:
    logger.info("Starting RAW_MEMBER to STG_MEMBER transformation.")

    if not SQL_FILE.exists():
        raise FileNotFoundError(f"SQL file not found: {SQL_FILE}")

    transformation_sql = SQL_FILE.read_text(encoding="utf-8")

    with get_snowflake_connection() as connection:
        cursor = connection.cursor()

        try:
            if batch_id is None:
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

            logger.info("Transforming member batch: %s", batch_id)
            batch_sql = transformation_sql.replace("{batch_id}", batch_id)
            for statement in batch_sql.split(";"):
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
            connection.commit()

            logger.info("RAW_MEMBER to STG_MEMBER transformation completed.")

        except Exception:
            connection.rollback()
            logger.exception(
                "RAW_MEMBER to STG_MEMBER transformation failed."
            )
            raise

        finally:
            cursor.close()


if __name__ == "__main__":
    configure_logging()
    load_staging_members()
