# Design Decisions

## 1. Preserve Raw Source Data

Member and redemption data are first written to raw tables. This retains original values and source/batch metadata for audit, investigation, and replay. Member date strings remain strings in `RAW_MEMBER`; the JSON payload remains a Snowflake `VARIANT` in `RAW_REDEMPTION`.

## 2. Parse Dates After Landing

The Excel sources use different representations, including ISO dates, timestamp-like values, and compact `MMDDYYYY` values. The member raw table therefore stores date values as strings. Staging and validation attempt explicit supported formats. Invalid values, such as `2021-13-13`, are not guessed or silently corrected.

## 3. Map Country from Source Configuration

The sample country files do not provide a common country field. The ingestion configuration associates `AUS.xlsx`, `IND.xlsx`, and `USA.xlsx` with their respective country codes. Country mapping is kept in configuration rather than repeated in each ingestion path.

## 4. Member Identity and Key Assumptions

Sample files reuse numeric IDs for different people across countries. Latest-record selection currently identifies a member by `(member_id, member_name)`, while DQ checks source-level uniqueness using `(country, member_id)`. These are assessment assumptions; production identity rules should be confirmed with the source owner and based on an immutable cross-source identifier.

Redemption data contains only `member_id`. The current profile join uses that field, so reused IDs across country targets can be ambiguous and may multiply redemption rows. Production integration should supply a globally unique key or additional matching attributes such as country.

## 5. Latest Record Wins

No authoritative source update timestamp is supplied. `ingestion_timestamp` is used to choose the latest member record, with enrollment date and source filename as deterministic tie-breakers. If the source later supplies an effective/update timestamp, it should replace ingestion time as the business recency field.

## 6. Invalid Records and Data Quality

The raw layer is the source of truth for values requiring investigation. DQ rules run against `RAW_MEMBER` so that a record filtered from `STG_MEMBER` can still be reported. Staging currently requires member ID, member name, and a parseable enrollment date.

The implemented DQ SQL checks mandatory ID/name, enrollment validity, flight-date validity, DOB validity/future DOB, enrollment/flight order, and duplicate country/member keys. An allowed-country list is not yet enforced. Validation is scoped to the latest batch, but repeated runs for one batch can append duplicate findings; a production validator should replace or merge that batch's results idempotently.

## 7. Left Join for Redemption Enrichment

The redemption-to-profile operation is a `LEFT JOIN` so missing member profiles do not cause transactions to be dropped. Unmatched member attributes remain `NULL` for later monitoring or reconciliation.

## 8. Python and Snowflake Roles

Python handles source-file access, configuration, batch metadata, logging, and SQL orchestration. Snowflake performs set-based transformations, windowing, JSON flattening, and joins. This keeps large transformations close to stored data.

## 9. Repeatability and Idempotency

Country member targets, redemption staging, and the member/redemption target are cleared and rebuilt by their current scripts. This makes those outputs repeatable for a full refresh. Raw loaders append new batches, and the DQ insert can append duplicate findings if rerun for the same batch. These sample-oriented behaviors need batch-keyed `MERGE` or controlled batch replacement before unattended production scheduling.

## 10. Testing and Verification

Unit tests cover business behavior using local data and do not require Snowflake execution for their assertions. Snowflake verification queries are used separately to confirm actual table counts, contents, and uniqueness. Local tests alone do not validate SQL behavior against Snowflake.

## 11. Scale Limitations and Future Production Changes

The assessment describes millions or billions of records per day, while the supplied implementation processes small Excel and JSON samples. Production scaling would require bulk staged file loads rather than row-wise Python inserts, incremental processing, idempotent batch handling, observability, measured warehouse sizing, and query-performance monitoring. Clustering should be introduced only when measured workloads justify it.

## 12. Assumptions

1. Source file identifies the country when the source row does not contain country.
2. Ingestion timestamp is the available proxy for record recency.
3. `(member_id, member_name)` distinguishes sample members for latest-record logic.
4. `(country, member_id)` is the source-level duplicate key within an ingestion batch.
5. Redemption transaction ID identifies a transaction.
6. Missing optional member attributes are represented as `NULL`.
7. The redemption-to-member join is performed on member ID for the assessment sample, subject to the ambiguity limitation above.
