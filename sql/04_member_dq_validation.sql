CREATE TABLE IF NOT EXISTS DQ_MEMBER_VALIDATION (
    validation_id       VARCHAR(36) NOT NULL,
    member_id           VARCHAR(18),
    member_name         VARCHAR(255),
    country             VARCHAR(5),
    source_file         VARCHAR(255) NOT NULL,
    ingestion_batch_id  VARCHAR(100) NOT NULL,
    rule_code            VARCHAR(100) NOT NULL,
    severity             VARCHAR(20) NOT NULL,
    validation_status    VARCHAR(20) NOT NULL,
    validation_message   VARCHAR(500) NOT NULL,
    validation_timestamp TIMESTAMP_NTZ NOT NULL DEFAULT CURRENT_TIMESTAMP()
);
