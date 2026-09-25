-- Raw member landing table.
-- Source values are retained as closely as possible so that
-- invalid records can be traced back to the original file.

CREATE TABLE IF NOT EXISTS RAW_MEMBER (
    member_id              VARCHAR(18),
    member_name            VARCHAR(255),
    enrollment_date_raw    VARCHAR(50),
    last_flight_date_raw   VARCHAR(50),
    tier_code              VARCHAR(5),
    agent_name             VARCHAR(255),
    state                  VARCHAR(5),
    post_code_raw          VARCHAR(20),
    dob_raw                VARCHAR(50),
    active_member          VARCHAR(1),
    country                VARCHAR(5),
    individual_or_corporate VARCHAR(50),

    source_file             VARCHAR(255) NOT NULL,
    ingestion_batch_id      VARCHAR(100) NOT NULL,
    ingestion_timestamp     TIMESTAMP_NTZ NOT NULL DEFAULT CURRENT_TIMESTAMP()
);
