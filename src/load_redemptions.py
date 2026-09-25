import json
import hashlib
import logging
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REDEMPTION_FILE = PROJECT_ROOT / "assessment" / "redemption.json"


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def create_redemption_batch_id(source_file: str, payload: dict) -> str:
    """Return a stable batch ID for the same source file and JSON payload."""
    serialized_payload = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload_digest = hashlib.sha256(serialized_payload.encode("utf-8")).hexdigest()
    return str(uuid5(NAMESPACE_URL, f"{source_file}:{payload_digest}"))


def load_redemptions() -> None:
    from src.snowflake_connection import get_snowflake_connection

    configure_logging()

    logging.info("Starting redemption JSON ingestion.")

    with REDEMPTION_FILE.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    serialized_payload = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    batch_id = create_redemption_batch_id(REDEMPTION_FILE.name, payload)

    with get_snowflake_connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM RAW_REDEMPTION
                    WHERE ingestion_batch_id = %s
                       OR (
                            source_file = %s
                            AND raw_payload:member_id::VARCHAR = %s
                            AND raw_payload:feed_date::VARCHAR = %s
                       )
                    """,
                    (
                        batch_id,
                        REDEMPTION_FILE.name,
                        str(payload.get("member_id", "")),
                        str(payload.get("feed_date", "")),
                    ),
                )
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
                        serialized_payload,
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
