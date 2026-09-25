DELETE FROM STG_REDEMPTION;

INSERT INTO STG_REDEMPTION (
    member_id,
    feed_date,
    transaction_id,
    transaction_date,
    partner,
    miles_redeemed,
    status,
    source_file,
    ingestion_batch_id,
    ingestion_timestamp
)
SELECT
    raw_payload:member_id::VARCHAR AS member_id,

    TRY_TO_DATE(
        raw_payload:feed_date::VARCHAR,
        'YYYYMMDD'
    ) AS feed_date,

    redemption.value:txn_id::VARCHAR AS transaction_id,

    TRY_TO_DATE(
        redemption.value:txn_date::VARCHAR,
        'YYYYMMDD'
    ) AS transaction_date,

    redemption.value:partner::VARCHAR AS partner,

    redemption.value:miles_redeemed::NUMBER(18, 0) AS miles_redeemed,

    redemption.value:status::VARCHAR AS status,

    source_file,

    ingestion_batch_id,

    ingestion_timestamp

FROM RAW_REDEMPTION,
LATERAL FLATTEN(
    INPUT => raw_payload:redemptions
) AS redemption
WHERE raw_payload:member_id IS NOT NULL
  AND raw_payload:feed_date IS NOT NULL
  AND redemption.value:txn_id IS NOT NULL;
