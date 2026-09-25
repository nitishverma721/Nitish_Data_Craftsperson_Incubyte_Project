import logging
from pathlib import Path

from src.snowflake_connection import get_snowflake_connection

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_FILE = PROJECT_ROOT / "sql" / "10_flatten_redemptions.sql"


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def flatten_redemptions() -> None:
    configure_logging()

    logging.info("Starting redemption JSON flattening.")

    sql = SQL_FILE.read_text(encoding="utf-8")

    with get_snowflake_connection() as connection:
        try:
            with connection.cursor() as cursor:
                for statement in sql.split(";"):
                    statement = statement.strip()

                    if statement:
                        cursor.execute(statement)

            connection.commit()

            logging.info("Redemption JSON flattening completed successfully.")

        except Exception:
            connection.rollback()
            logging.exception("Redemption JSON flattening failed.")
            raise


if __name__ == "__main__":
    flatten_redemptions()
