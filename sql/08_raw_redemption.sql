CREATE TABLE IF NOT EXISTS RAW_REDEMPTION (
    raw_payload         VARIANT NOT NULL,
    source_file         VARCHAR(255) NOT NULL,
    ingestion_batch_id  VARCHAR(100) NOT NULL,
    ingestion_timestamp TIMESTAMP_NTZ NOT NULL DEFAULT CURRENT_TIMESTAMP()
);
