import json
import logging
import uuid
from pathlib import Path

from src.snowflake_connection import get_snowflake_connection

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REDEMPTION_FILE = PROJECT_ROOT / "assessment" / "redemption.json"


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def load_redemptions() -> None:
    configure_logging()

    logging.info("Starting redemption JSON ingestion.")

    with REDEMPTION_FILE.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    batch_id = str(uuid.uuid4())

    with get_snowflake_connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO RAW_REDEMPTION (
                        raw_payload,
                        source_file,
                        ingestion_batch_id
                    )
                    SELECT PARSE_JSON(%s), %s, %s
                    """,
                    (
                        json.dumps(payload),
                        REDEMPTION_FILE.name,
                        batch_id,
                    ),
                )

            connection.commit()

            logging.info(
                "Redemption JSON loaded successfully. batch_id=%s",
                batch_id,
            )

        except Exception:
            connection.rollback()
            logging.exception("Redemption JSON ingestion failed.")
            raise


if __name__ == "__main__":
    load_redemptions()
