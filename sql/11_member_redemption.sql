CREATE OR REPLACE TABLE TGT_MEMBER_REDEMPTION (
    member_id           VARCHAR(18) NOT NULL,
    member_name         VARCHAR(255),
    country             VARCHAR(5),
    tier_code           VARCHAR(5),
    transaction_id      VARCHAR(100) NOT NULL,
    transaction_date    DATE NOT NULL,
    partner             VARCHAR(255),
    miles_redeemed      NUMBER(18, 0),
    status              VARCHAR(50),
    feed_date           DATE NOT NULL,
    source_file         VARCHAR(255) NOT NULL,
    ingestion_batch_id  VARCHAR(100) NOT NULL,
    ingestion_timestamp TIMESTAMP_NTZ NOT NULL
);

TRUNCATE TABLE TGT_MEMBER_REDEMPTION;

INSERT INTO TGT_MEMBER_REDEMPTION (
    member_id,
    member_name,
    country,
    tier_code,
    transaction_id,
    transaction_date,
    partner,
    miles_redeemed,
    status,
    feed_date,
    source_file,
    ingestion_batch_id,
    ingestion_timestamp
)
WITH CURRENT_MEMBERS AS (
    SELECT
        member_id,
        member_name,
        country,
        tier_code
    FROM TGT_MEMBER_AUS

    UNION ALL

    SELECT
        member_id,
        member_name,
        country,
        tier_code
    FROM TGT_MEMBER_IND

    UNION ALL

    SELECT
        member_id,
        member_name,
        country,
        tier_code
    FROM TGT_MEMBER_USA
)

SELECT
    r.member_id,
    m.member_name,
    m.country,
    m.tier_code,
    r.transaction_id,
    r.transaction_date,
    r.partner,
    r.miles_redeemed,
    r.status,
    r.feed_date,
    r.source_file,
    r.ingestion_batch_id,
    r.ingestion_timestamp
FROM STG_REDEMPTION r
LEFT JOIN CURRENT_MEMBERS m
    ON r.member_id = m.member_id;
