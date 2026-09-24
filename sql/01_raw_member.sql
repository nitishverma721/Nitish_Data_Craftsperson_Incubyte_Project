-- Raw member landing table.
-- Source values are retained as closely as possible so that
-- invalid records can be traced back to the original file.

CREATE OR REPLACE TABLE RAW_MEMBER (
    member_id              VARCHAR(18),
    member_name            VARCHAR(255),
    enrollment_date_raw    VARCHAR(50),
    last_flight_date_raw   VARCHAR(50),
    tier_code              VARCHAR(5),
    dob_raw                VARCHAR(50),
    country                VARCHAR(5),
    individual_or_corporate VARCHAR(50),

    source_file             VARCHAR(255) NOT NULL,
    ingestion_batch_id      VARCHAR(100) NOT NULL,
    ingestion_timestamp     TIMESTAMP_NTZ NOT NULL DEFAULT CURRENT_TIMESTAMP()
);
