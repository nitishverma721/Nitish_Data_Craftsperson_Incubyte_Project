# Source Data Analysis

## Overview

The assessment provides member profile data from multiple country-specific source files.

The source files do not have an identical structure or representation of fields. The ingestion process therefore needs to preserve the source data and apply standardization during the staging phase.

## Source Files

### AUS.xlsx

Columns:

- Unique ID
- Member Name
- Tier Type
- Date of Birth
- Date of Enrollment
- Date of Flight

Observed data-quality issues:

- Some members have a missing Date of Birth.
- One record contains an invalid enrollment date (`2021-13-13`).
- The member identifier is represented as a numeric value.

### IND.xlsx

Columns:

- ID
- Name
- DOB
- TierCode
- EnrollmentDate
- Individual or Corporate
- Flight Date

Observed characteristics:

- The file contains an additional `Individual or Corporate` attribute.
- Date fields are represented as date values.
- The member identifier is represented as a numeric value.

### USA.xlsx

Columns:

- ID
- Name
- TierCode
- EnrollmentDate
- FlightDate

Observed characteristics:

- Date of Birth is not provided.
- Enrollment and flight dates are represented as numeric values such as `6152022`, `8202022`, and `12282021`.
- The member identifier is represented as a numeric value.

## Source-to-Target Standardization

The source files use different column names for equivalent business attributes.

| Business Attribute | AUS | IND | USA |
|---|---|---|---|
| Member ID | Unique ID | ID | ID |
| Member Name | Member Name | Name | Name |
| Tier | Tier Type | TierCode | TierCode |
| DOB | Date of Birth | DOB | Not available |
| Enrollment Date | Date of Enrollment | EnrollmentDate | EnrollmentDate |
| Flight Date | Date of Flight | Flight Date | FlightDate |
| Individual/Corporate | Not available | Individual or Corporate | Not available |

The staging layer will standardize these fields into a common member schema.

## Data Quality Approach

The raw/landing layer will preserve source data as received.

Validation and standardization will be applied before data is promoted to the trusted staging layer.

The pipeline will identify, rather than silently hide, issues such as:

- Missing mandatory fields
- Invalid dates
- Duplicate member identifiers
- Invalid or unexpected country values
- Invalid business dates
- Missing optional attributes

Invalid records should be traceable back to their source file and ingestion batch.

## Assumptions

1. Member ID is the business identifier used to associate member records across the pipeline.
2. Source-specific column names will be mapped to a common staging schema.
3. Optional attributes that are not provided by a source will be stored as NULL.
4. Invalid source values should be identified through data-quality validation rather than silently corrected.
5. The raw layer should retain the original source representation for auditability and troubleshooting.
6. Country information will be associated with the source/member feed as part of the standardized ingestion process.
7. The latest valid member record will determine the member's current country when multiple records exist for the same member.
