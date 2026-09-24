INSERT INTO STG_MEMBER (
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
)
SELECT
    member_id,
    member_name,

    COALESCE(
        TRY_TO_DATE(enrollment_date_raw, 'YYYY-MM-DD'),
        TRY_TO_DATE(enrollment_date_raw, 'YYYY-MM-DD HH24:MI:SS'),
        TRY_TO_DATE(enrollment_date_raw, 'MMDDYYYY')
    ) AS enrollment_date,

    COALESCE(
        TRY_TO_DATE(last_flight_date_raw, 'YYYY-MM-DD'),
        TRY_TO_DATE(last_flight_date_raw, 'MMDDYYYY')
    ) AS last_flight_date,

    tier_code,

    TRY_TO_DATE(dob_raw, 'YYYY-MM-DD') AS dob,

    country,
    individual_or_corporate,

    CASE
        WHEN TRY_TO_DATE(dob_raw, 'YYYY-MM-DD') IS NULL THEN NULL
        ELSE DATEDIFF(
            year,
            TRY_TO_DATE(dob_raw, 'YYYY-MM-DD'),
            CURRENT_DATE()
        )
        -
        CASE
            WHEN DATE_FROM_PARTS(
                YEAR(CURRENT_DATE()),
                MONTH(TRY_TO_DATE(dob_raw, 'YYYY-MM-DD')),
                DAY(TRY_TO_DATE(dob_raw, 'YYYY-MM-DD'))
            ) > CURRENT_DATE()
            THEN 1
            ELSE 0
        END
    END AS age,

    CASE
        WHEN COALESCE(
            TRY_TO_DATE(last_flight_date_raw, 'YYYY-MM-DD'),
            TRY_TO_DATE(last_flight_date_raw, 'MMDDYYYY')
        ) IS NULL
        THEN NULL

        WHEN DATEDIFF(
            day,
            COALESCE(
                TRY_TO_DATE(last_flight_date_raw, 'YYYY-MM-DD'),
                TRY_TO_DATE(last_flight_date_raw, 'MMDDYYYY')
            ),
            CURRENT_DATE()
        ) > 90
        THEN TRUE

        ELSE FALSE
    END AS stale_member,

    source_file,
    ingestion_batch_id,
    ingestion_timestamp

FROM RAW_MEMBER

WHERE member_id IS NOT NULL
    AND member_name IS NOT NULL
    AND COALESCE(
                TRY_TO_DATE(enrollment_date_raw, 'YYYY-MM-DD'),
                TRY_TO_DATE(enrollment_date_raw, 'YYYY-MM-DD HH24:MI:SS'),
                TRY_TO_DATE(enrollment_date_raw, 'MMDDYYYY')
            ) IS NOT NULL;
