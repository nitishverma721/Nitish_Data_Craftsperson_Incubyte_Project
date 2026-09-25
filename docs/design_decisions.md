# Design Decisions

## 1. Preserve Raw Source Data

Member and redemption data are first written to raw tables. This retains original values and source/batch metadata for audit, investigation, and replay. Member date strings remain strings in `RAW_MEMBER`; the JSON payload remains a Snowflake `VARIANT` in `RAW_REDEMPTION`.

## 2. Parse Dates After Landing

The Excel and assessment pipe-file sources use different representations, including ISO dates, timestamp-like values, `YYYYMMDD`, and compact `MMDDYYYY` values. The member raw table therefore stores date values as strings. Staging and validation attempt explicit supported formats. Invalid values, such as `2021-13-13`, are not guessed or silently corrected.

## 3. Map Country from Source Configuration

The supplied Excel files do not provide a country field, so configuration associates `AUS.xlsx`, `IND.xlsx`, and `USA.xlsx` with their respective codes. The assessment pipe file supplies Country; its `AU` value is normalized to `AUS`. The target set supports AUS, IND, USA, PHIL, and CAN.

## 4. Member Identity and Key Assumptions

The PDF marks Member Name as the key and Member ID as non-key. Latest-target selection therefore uses normalized Member Name. The Excel files repeat `Mike` across countries with different IDs; both same-batch rows are recorded as DQ errors and excluded from staging and country targets rather than merged or arbitrarily selected. Target rebuilding also filters names flagged by the latest DQ batch so older staged history cannot reintroduce them. If they are different people, the source owner must provide an immutable global key before either can be safely promoted.

Redemption data contains only `member_id`. The current profile join enriches only IDs unique across the country targets. Missing or ambiguous profiles leave one redemption row with null profile fields. Production integration should supply a globally unique key or additional matching attributes such as country.

## 5. Latest Record Wins

No authoritative source update timestamp is supplied. `ingestion_timestamp` is used to choose the latest member record, with enrollment date and source filename as deterministic tie-breakers. If the source later supplies an effective/update timestamp, it should replace ingestion time as the business recency field.

## 6. Invalid Records and Data Quality

The raw layer is the source of truth for values requiring investigation. DQ rules run against `RAW_MEMBER` so that a record filtered from `STG_MEMBER` can still be reported. Staging currently requires member ID, member name, and a parseable enrollment date.

The implemented DQ SQL checks mandatory ID/name, enrollment validity, flight-date validity, DOB validity/future DOB, enrollment/flight order, supported country codes, assessment-declared member-name uniqueness, and duplicate country/member ID keys. Validation selects the newest batch by ingestion timestamp and deletes prior findings for that batch before inserting new findings.

## 7. Left Join for Redemption Enrichment

The redemption-to-profile operation is a `LEFT JOIN` so missing member profiles do not cause transactions to be dropped. Unmatched member attributes remain `NULL` for later monitoring or reconciliation.

## 8. Python and Snowflake Roles

Python handles source-file access, configuration, batch metadata, logging, and SQL orchestration. Snowflake performs set-based transformations, windowing, JSON flattening, and joins. This keeps large transformations close to stored data.

## 9. Repeatability and Idempotency

Country member targets, redemption staging, and the member/redemption target are cleared and rebuilt by their current scripts using DML deletes under explicit non-autocommit transactions. Member raw and staging loads use content-derived batch IDs and replace the same batch on retry; redemption raw loading follows the same pattern and replaces a matching source/member/feed-date payload from an earlier run. DQ findings for the selected batch are replaced before validation. These full-refresh target strategies are repeatable for the sample but should become incremental batch-keyed merges at production scale.

## 10. Testing and Verification

Unit tests cover business behavior using local data and do not require Snowflake execution for their assertions. Snowflake verification queries are used separately to confirm actual table counts, contents, and uniqueness. Local tests alone do not validate SQL behavior against Snowflake.

## 11. Scale Limitations and Future Production Changes

The assessment describes millions or billions of records per day, while the supplied implementation processes small Excel and JSON samples. Production scaling would require bulk staged file loads rather than row-wise Python inserts, incremental processing, idempotent batch handling, observability, measured warehouse sizing, and query-performance monitoring. Clustering should be introduced only when measured workloads justify it.

## 12. Assumptions

1. Source file identifies country for country-specific Excel files; pipe-file country codes are normalized (`AU` to `AUS`).
2. Ingestion timestamp is the available proxy for record recency.
3. Normalized Member Name is the assessment key for latest-target logic.
4. Same-batch duplicate Member Names are excluded from staging and current targets; raw records and DQ findings remain for investigation.
5. `(country, member_id)` is additionally checked as a source-level duplicate key within an ingestion batch.
6. Redemption transaction ID identifies a transaction.
7. Missing optional member attributes are represented as `NULL`.
8. The redemption-to-member join enriches only globally unique member IDs; unmatched or ambiguous transactions are retained with null profile attributes.
