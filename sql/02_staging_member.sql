-- Standardized member staging table.
-- Source-specific values are converted into the canonical business model here.

CREATE TABLE IF NOT EXISTS STG_MEMBER (
    member_id                VARCHAR(18) NOT NULL,
    member_name              VARCHAR(255) NOT NULL,
    enrollment_date          DATE NOT NULL,
    last_flight_date         DATE,
    tier_code                VARCHAR(5),
    agent_name               VARCHAR(255),
    state                    VARCHAR(5),
    post_code                NUMBER(5, 0),
    dob                      DATE,
    active_member            VARCHAR(1),
    country                  VARCHAR(5),
    individual_or_corporate  VARCHAR(50),

    age                      INTEGER,
    stale_member              BOOLEAN,

    source_file              VARCHAR(255) NOT NULL,
    ingestion_batch_id       VARCHAR(100) NOT NULL,
    ingestion_timestamp      TIMESTAMP_NTZ NOT NULL
);
