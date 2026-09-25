CREATE TABLE IF NOT EXISTS STG_REDEMPTION (
    member_id            VARCHAR(18) NOT NULL,
    feed_date            DATE NOT NULL,
    transaction_id       VARCHAR(100) NOT NULL,
    transaction_date     DATE NOT NULL,
    partner              VARCHAR(255),
    miles_redeemed       NUMBER(18, 0),
    status               VARCHAR(50),
    source_file          VARCHAR(255) NOT NULL,
    ingestion_batch_id   VARCHAR(100) NOT NULL,
    ingestion_timestamp  TIMESTAMP_NTZ NOT NULL
);
