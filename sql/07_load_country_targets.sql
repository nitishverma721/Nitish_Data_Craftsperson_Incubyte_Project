-- Clear previous target data so the load is idempotent.
TRUNCATE TABLE TGT_MEMBER_AUS;
TRUNCATE TABLE TGT_MEMBER_IND;
TRUNCATE TABLE TGT_MEMBER_USA;

-- Identify the latest record for each member.
CREATE OR REPLACE TEMPORARY TABLE TMP_LATEST_MEMBERS AS
SELECT
    member_id,
    member_name,
    enrollment_date,
    last_flight_date,
    tier_code,
    dob,
    country,
    individual_or_corporate,
    age,
    stale_member,
    source_file,
    ingestion_batch_id,
    ingestion_timestamp
FROM STG_MEMBER
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY member_id, member_name
    ORDER BY
        ingestion_timestamp DESC,
        enrollment_date DESC NULLS LAST,
        source_file DESC
) = 1;

-- Load the current members into the Australia target.
INSERT INTO TGT_MEMBER_AUS
SELECT *
FROM TMP_LATEST_MEMBERS
WHERE country = 'AUS';

-- Load the current members into the India target.
INSERT INTO TGT_MEMBER_IND
SELECT *
FROM TMP_LATEST_MEMBERS
WHERE country = 'IND';

-- Load the current members into the USA target.
INSERT INTO TGT_MEMBER_USA
SELECT *
FROM TMP_LATEST_MEMBERS
WHERE country = 'USA';
