INSERT INTO DQ_MEMBER_VALIDATION (
    validation_id,
    member_id,
    member_name,
    country,
    source_file,
    ingestion_batch_id,
    rule_code,
    severity,
    validation_status,
    validation_message
)

-- Mandatory member ID
SELECT
    UUID_STRING(),
    member_id,
    member_name,
    country,
    source_file,
    ingestion_batch_id,
    'MANDATORY_MEMBER_ID',
    'ERROR',
    'FAILED',
    'Member ID is mandatory'
FROM RAW_MEMBER
WHERE ingestion_batch_id = '{batch_id}'
  AND member_id IS NULL

UNION ALL

-- Mandatory member name
SELECT
    UUID_STRING(),
    member_id,
    member_name,
    country,
    source_file,
    ingestion_batch_id,
    'MANDATORY_MEMBER_NAME',
    'ERROR',
    'FAILED',
    'Member name is mandatory'
FROM RAW_MEMBER
WHERE ingestion_batch_id = '{batch_id}'
  AND member_name IS NULL

UNION ALL

-- Mandatory enrollment date / invalid enrollment date
SELECT
    UUID_STRING(),
    member_id,
    member_name,
    country,
    source_file,
    ingestion_batch_id,
    'INVALID_ENROLLMENT_DATE',
    'ERROR',
    'FAILED',
    'Enrollment date is missing or invalid'
FROM RAW_MEMBER
WHERE ingestion_batch_id = '{batch_id}'
  AND (
      enrollment_date_raw IS NULL
      OR COALESCE(
          TRY_TO_DATE(enrollment_date_raw, 'YYYY-MM-DD'),
          TRY_TO_DATE(enrollment_date_raw, 'YYYY-MM-DD HH24:MI:SS'),
          TRY_TO_DATE(enrollment_date_raw, 'YYYYMMDD'),
          TRY_TO_DATE(enrollment_date_raw, 'MMDDYYYY')
      ) IS NULL
  )

UNION ALL

-- Invalid last flight date
SELECT
    UUID_STRING(),
    member_id,
    member_name,
    country,
    source_file,
    ingestion_batch_id,
    'INVALID_LAST_FLIGHT_DATE',
    'ERROR',
    'FAILED',
    'Last flight date is invalid'
FROM RAW_MEMBER
WHERE ingestion_batch_id = '{batch_id}'
  AND last_flight_date_raw IS NOT NULL
  AND COALESCE(
      TRY_TO_DATE(last_flight_date_raw, 'YYYY-MM-DD'),
      TRY_TO_DATE(last_flight_date_raw, 'YYYY-MM-DD HH24:MI:SS'),
      TRY_TO_DATE(last_flight_date_raw, 'YYYYMMDD'),
      TRY_TO_DATE(last_flight_date_raw, 'MMDDYYYY')
  ) IS NULL

UNION ALL

-- Invalid DOB
SELECT
    UUID_STRING(),
    member_id,
    member_name,
    country,
    source_file,
    ingestion_batch_id,
    'INVALID_DOB',
    'ERROR',
    'FAILED',
    'Date of birth is invalid'
FROM RAW_MEMBER
WHERE ingestion_batch_id = '{batch_id}'
  AND dob_raw IS NOT NULL
    AND COALESCE(
            TRY_TO_DATE(dob_raw, 'YYYY-MM-DD'),
            TRY_TO_DATE(dob_raw, 'YYYY-MM-DD HH24:MI:SS'),
            TRY_TO_DATE(dob_raw, 'YYYYMMDD'),
            TRY_TO_DATE(dob_raw, 'MMDDYYYY')
    ) IS NULL

UNION ALL

-- Future DOB
SELECT
    UUID_STRING(),
    member_id,
    member_name,
    country,
    source_file,
    ingestion_batch_id,
    'FUTURE_DOB',
    'ERROR',
    'FAILED',
    'Date of birth cannot be in the future'
FROM RAW_MEMBER
WHERE ingestion_batch_id = '{batch_id}'
    AND COALESCE(
            TRY_TO_DATE(dob_raw, 'YYYY-MM-DD'),
            TRY_TO_DATE(dob_raw, 'YYYY-MM-DD HH24:MI:SS'),
            TRY_TO_DATE(dob_raw, 'YYYYMMDD'),
            TRY_TO_DATE(dob_raw, 'MMDDYYYY')
    ) > CURRENT_DATE()

UNION ALL

-- Enrollment date cannot be after last flight date
SELECT
    UUID_STRING(),
    member_id,
    member_name,
    country,
    source_file,
    ingestion_batch_id,
    'INVALID_DATE_SEQUENCE',
    'ERROR',
    'FAILED',
    'Enrollment date cannot be after last flight date'
FROM RAW_MEMBER
WHERE ingestion_batch_id = '{batch_id}'
  AND COALESCE(
      TRY_TO_DATE(enrollment_date_raw, 'YYYY-MM-DD'),
      TRY_TO_DATE(enrollment_date_raw, 'YYYY-MM-DD HH24:MI:SS'),
    TRY_TO_DATE(enrollment_date_raw, 'YYYYMMDD'),
      TRY_TO_DATE(enrollment_date_raw, 'MMDDYYYY')
  ) IS NOT NULL
  AND COALESCE(
      TRY_TO_DATE(last_flight_date_raw, 'YYYY-MM-DD'),
    TRY_TO_DATE(last_flight_date_raw, 'YYYY-MM-DD HH24:MI:SS'),
    TRY_TO_DATE(last_flight_date_raw, 'YYYYMMDD'),
      TRY_TO_DATE(last_flight_date_raw, 'MMDDYYYY')
  ) IS NOT NULL
  AND COALESCE(
      TRY_TO_DATE(enrollment_date_raw, 'YYYY-MM-DD'),
      TRY_TO_DATE(enrollment_date_raw, 'YYYY-MM-DD HH24:MI:SS'),
    TRY_TO_DATE(enrollment_date_raw, 'YYYYMMDD'),
      TRY_TO_DATE(enrollment_date_raw, 'MMDDYYYY')
  )
  >
  COALESCE(
      TRY_TO_DATE(last_flight_date_raw, 'YYYY-MM-DD'),
            TRY_TO_DATE(last_flight_date_raw, 'YYYY-MM-DD HH24:MI:SS'),
            TRY_TO_DATE(last_flight_date_raw, 'YYYYMMDD'),
      TRY_TO_DATE(last_flight_date_raw, 'MMDDYYYY')
  )

UNION ALL

-- Country must be present and supported by a country target.
SELECT
        UUID_STRING(),
        member_id,
        member_name,
        country,
        source_file,
        ingestion_batch_id,
        'INVALID_COUNTRY',
        'ERROR',
        'FAILED',
        'Country is missing or unsupported'
FROM RAW_MEMBER
WHERE ingestion_batch_id = '{batch_id}'
    AND (
            country IS NULL
            OR TRIM(country) = ''
            OR UPPER(TRIM(country)) NOT IN ('AUS', 'IND', 'USA', 'PHIL', 'CAN')
    )

UNION ALL

-- Member Name is marked as the key in the assessment.
SELECT
        UUID_STRING(),
    member_id,
        member_name,
        country,
    source_file,
        ingestion_batch_id,
        'DUPLICATE_MEMBER_NAME_KEY',
        'ERROR',
        'FAILED',
        'Duplicate member name found within the ingestion batch'
FROM (
    SELECT
        *,
        COUNT(*) OVER (
            PARTITION BY UPPER(TRIM(member_name)), ingestion_batch_id
        ) AS member_name_count
    FROM RAW_MEMBER
    WHERE ingestion_batch_id = '{batch_id}'
    AND member_name IS NOT NULL
    AND TRIM(member_name) <> ''
) AS MEMBER_NAME_KEYS
WHERE member_name_count > 1

UNION ALL

-- Duplicate country/member combination
SELECT
    UUID_STRING(),
    member_id,
    MAX(member_name) AS member_name,
    country,
    MAX(source_file) AS source_file,
    ingestion_batch_id,
    'DUPLICATE_MEMBER_KEY',
    'ERROR',
    'FAILED',
    'Duplicate member ID found for the same country'
FROM RAW_MEMBER
WHERE ingestion_batch_id = '{batch_id}'
    AND member_id IS NOT NULL
GROUP BY
    member_id,
    country,
    ingestion_batch_id
HAVING COUNT(*) > 1;
