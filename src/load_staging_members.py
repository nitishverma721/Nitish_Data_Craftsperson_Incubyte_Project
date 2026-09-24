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


def load_staging_members() -> None:
    logger.info("Starting RAW_MEMBER to STG_MEMBER transformation.")

    if not SQL_FILE.exists():
        raise FileNotFoundError(f"SQL file not found: {SQL_FILE}")

    transformation_sql = SQL_FILE.read_text(encoding="utf-8")

    with get_snowflake_connection() as connection:
        cursor = connection.cursor()

        try:
            cursor.execute(transformation_sql)
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
