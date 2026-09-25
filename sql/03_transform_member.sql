DELETE FROM STG_MEMBER
WHERE ingestion_batch_id = '{batch_id}';

INSERT INTO STG_MEMBER (
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
)
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
    UPPER(TRIM(country)) AS country,
    individual_or_corporate,

    CASE
        WHEN dob IS NULL THEN NULL
        ELSE DATEDIFF(
            year,
            dob,
            CURRENT_DATE()
        )
        -
        CASE
            WHEN DATE_FROM_PARTS(
                YEAR(CURRENT_DATE()),
                MONTH(dob),
                DAY(dob)
            ) > CURRENT_DATE()
            THEN 1
            ELSE 0
        END
    END AS age,

    CASE
        WHEN last_flight_date IS NULL
        THEN NULL

        WHEN DATEDIFF(
            day,
            last_flight_date,
            CURRENT_DATE()
        ) > 90
        THEN TRUE

        ELSE FALSE
    END AS stale_member,

    source_file,
    ingestion_batch_id,
    ingestion_timestamp

FROM (
    SELECT
        *,
        COUNT(*) OVER (
            PARTITION BY UPPER(TRIM(member_name)), ingestion_batch_id
        ) AS member_name_count,
        COALESCE(
            TRY_TO_DATE(enrollment_date_raw, 'YYYY-MM-DD'),
            TRY_TO_DATE(enrollment_date_raw, 'YYYY-MM-DD HH24:MI:SS'),
            TRY_TO_DATE(enrollment_date_raw, 'YYYYMMDD'),
            TRY_TO_DATE(enrollment_date_raw, 'MMDDYYYY')
        ) AS enrollment_date,
        COALESCE(
            TRY_TO_DATE(last_flight_date_raw, 'YYYY-MM-DD'),
            TRY_TO_DATE(last_flight_date_raw, 'YYYY-MM-DD HH24:MI:SS'),
            TRY_TO_DATE(last_flight_date_raw, 'YYYYMMDD'),
            TRY_TO_DATE(last_flight_date_raw, 'MMDDYYYY')
        ) AS last_flight_date,
        COALESCE(
            TRY_TO_DATE(dob_raw, 'YYYY-MM-DD'),
            TRY_TO_DATE(dob_raw, 'YYYY-MM-DD HH24:MI:SS'),
            TRY_TO_DATE(dob_raw, 'YYYYMMDD'),
            TRY_TO_DATE(dob_raw, 'MMDDYYYY')
        ) AS dob,
        TRY_TO_NUMBER(post_code_raw) AS post_code
    FROM RAW_MEMBER
) AS RAW_MEMBER

WHERE member_id IS NOT NULL
    AND member_name IS NOT NULL
    AND TRIM(member_name) <> ''
    AND member_name_count = 1
    AND ingestion_batch_id = '{batch_id}'
    AND UPPER(TRIM(country)) IN ('AUS', 'IND', 'USA', 'PHIL', 'CAN')
    AND COALESCE(
                TRY_TO_DATE(enrollment_date_raw, 'YYYY-MM-DD'),
                TRY_TO_DATE(enrollment_date_raw, 'YYYY-MM-DD HH24:MI:SS'),
                TRY_TO_DATE(enrollment_date_raw, 'YYYYMMDD'),
                TRY_TO_DATE(enrollment_date_raw, 'MMDDYYYY')
            ) IS NOT NULL;
