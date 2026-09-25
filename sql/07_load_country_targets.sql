-- Identify the latest record for each member.
CREATE OR REPLACE TEMPORARY TABLE TMP_LATEST_MEMBERS AS
SELECT
    member_id,
    member_name,
    enrollment_date,
    last_flight_date,
    tier_code,
    agent_name,
    state,
    post_code,
    dob,
    active_member,
    country,
    individual_or_corporate,
    age,
    stale_member,
    source_file,
    ingestion_batch_id,
    ingestion_timestamp
FROM STG_MEMBER
WHERE NOT EXISTS (
    SELECT 1
    FROM DQ_MEMBER_VALIDATION AS DQ
    WHERE DQ.rule_code = 'DUPLICATE_MEMBER_NAME_KEY'
      AND DQ.validation_status = 'FAILED'
      AND UPPER(TRIM(DQ.member_name)) = UPPER(TRIM(STG_MEMBER.member_name))
      AND DQ.ingestion_batch_id = (
          SELECT ingestion_batch_id
          FROM RAW_MEMBER
          GROUP BY ingestion_batch_id
          ORDER BY MAX(ingestion_timestamp) DESC
          LIMIT 1
      )
)
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY UPPER(TRIM(member_name))
    ORDER BY
        ingestion_timestamp DESC,
        enrollment_date DESC NULLS LAST,
        source_file DESC
) = 1;

    -- Clear previous target data inside the DML transaction.
    DELETE FROM TGT_MEMBER_AUS;
    DELETE FROM TGT_MEMBER_IND;
    DELETE FROM TGT_MEMBER_USA;
    DELETE FROM TGT_MEMBER_PHIL;
    DELETE FROM TGT_MEMBER_CAN;

-- Load the current members into each country target.
INSERT INTO TGT_MEMBER_AUS (
    member_id, member_name, enrollment_date, last_flight_date, tier_code,
    agent_name, state, post_code, dob, active_member, country,
    individual_or_corporate, age, stale_member, source_file,
    ingestion_batch_id, ingestion_timestamp
)
SELECT
    member_id, member_name, enrollment_date, last_flight_date, tier_code,
    agent_name, state, post_code, dob, active_member, country,
    individual_or_corporate, age, stale_member, source_file,
    ingestion_batch_id, ingestion_timestamp
FROM TMP_LATEST_MEMBERS
WHERE country = 'AUS';

INSERT INTO TGT_MEMBER_IND (
    member_id, member_name, enrollment_date, last_flight_date, tier_code,
    agent_name, state, post_code, dob, active_member, country,
    individual_or_corporate, age, stale_member, source_file,
    ingestion_batch_id, ingestion_timestamp
)
SELECT
    member_id, member_name, enrollment_date, last_flight_date, tier_code,
    agent_name, state, post_code, dob, active_member, country,
    individual_or_corporate, age, stale_member, source_file,
    ingestion_batch_id, ingestion_timestamp
FROM TMP_LATEST_MEMBERS
WHERE country = 'IND';

INSERT INTO TGT_MEMBER_USA (
    member_id, member_name, enrollment_date, last_flight_date, tier_code,
    agent_name, state, post_code, dob, active_member, country,
    individual_or_corporate, age, stale_member, source_file,
    ingestion_batch_id, ingestion_timestamp
)
SELECT
    member_id, member_name, enrollment_date, last_flight_date, tier_code,
    agent_name, state, post_code, dob, active_member, country,
    individual_or_corporate, age, stale_member, source_file,
    ingestion_batch_id, ingestion_timestamp
FROM TMP_LATEST_MEMBERS
WHERE country = 'USA';

INSERT INTO TGT_MEMBER_PHIL (
    member_id, member_name, enrollment_date, last_flight_date, tier_code,
    agent_name, state, post_code, dob, active_member, country,
    individual_or_corporate, age, stale_member, source_file,
    ingestion_batch_id, ingestion_timestamp
)
SELECT
    member_id, member_name, enrollment_date, last_flight_date, tier_code,
    agent_name, state, post_code, dob, active_member, country,
    individual_or_corporate, age, stale_member, source_file,
    ingestion_batch_id, ingestion_timestamp
FROM TMP_LATEST_MEMBERS
WHERE country = 'PHIL';

INSERT INTO TGT_MEMBER_CAN (
    member_id, member_name, enrollment_date, last_flight_date, tier_code,
    agent_name, state, post_code, dob, active_member, country,
    individual_or_corporate, age, stale_member, source_file,
    ingestion_batch_id, ingestion_timestamp
)
SELECT
    member_id, member_name, enrollment_date, last_flight_date, tier_code,
    agent_name, state, post_code, dob, active_member, country,
    individual_or_corporate, age, stale_member, source_file,
    ingestion_batch_id, ingestion_timestamp
FROM TMP_LATEST_MEMBERS
WHERE country = 'CAN';
