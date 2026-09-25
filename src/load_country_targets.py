from pathlib import Path
import logging

from src.snowflake_connection import get_snowflake_connection

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_FILE = PROJECT_ROOT / "sql" / "07_load_country_targets.sql"


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def load_country_targets() -> None:
    configure_logging()

    logging.info("Starting country target load.")

    sql = SQL_FILE.read_text(encoding="utf-8")

    with get_snowflake_connection() as connection:
        try:
            with connection.cursor() as cursor:
                for statement in sql.split(";"):
                    statement = statement.strip()

                    if statement:
                        cursor.execute(statement)

            connection.commit()
            logging.info("Country target load completed successfully.")

        except Exception:
            connection.rollback()
            logging.exception("Country target load failed.")
            raise


if __name__ == "__main__":
    load_country_targets()
