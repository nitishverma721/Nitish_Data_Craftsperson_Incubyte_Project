# Source Data Analysis

## Overview

The assessment PDF describes a generic header/detail member feed plus a daily nested redemption JSON feed. The workspace also includes three country-specific Excel samples. These sources differ in columns, country coding, and date representation, so the ingestion path preserves source values and standardizes them explicitly.

## Assessment Member Feed

The PDF describes pipe-delimited `H` header and `D` detail records. Its profile attributes are Member Name, Member ID, Enrollment Date, Last Flight Date, Tier Code, Agent Name, State, Country, Post Code, Date of Birth, and Active Member. It specifies Member Name as the key and Member ID as mandatory but not a key. Its examples include dates in `YYYYMMDD` and DOB in `MMDDYYYY` form. Post Code is optional and specified as an integer.

The sample header/detail example omits Post Code despite listing it in the field specification. The parser therefore accepts Post Code when present and represents it as NULL when absent.

## Workspace Excel Samples

### AUS.xlsx

Columns are `Unique ID`, `Member Name`, `Tier Type`, `Date of Birth`, `Date of Enrollment`, and `Date of Flight`.

- Some DOB values are missing.
- Jonnathan has an invalid enrollment value (`2021-13-13`).
- IDs are represented numerically by Excel.
- Date cells can be date/timestamp values.

### IND.xlsx

Columns are `ID`, `Name`, `DOB`, `TierCode`, `EnrollmentDate`, `Individual or Corporate`, and `Flight Date`.

- This source includes `Individual or Corporate`.
- Date values are represented as Excel dates.
- IDs are represented numerically by Excel.

### USA.xlsx

Columns are `ID`, `Name`, `TierCode`, `EnrollmentDate`, and `FlightDate`.

- DOB is not provided.
- Enrollment and flight dates are numeric-looking values such as `6152022`, `8202022`, and `12282021`.
- IDs are represented numerically by Excel.

The Excel sample also has the name `Mike` in AUS and USA with different member IDs. This conflicts with the PDF's Member Name key declaration and is reported as a duplicate-name DQ finding rather than silently merged.

## Source-to-Canonical Mapping

| Canonical field | AUS.xlsx | IND.xlsx | USA.xlsx | Assessment pipe feed |
|---|---|---|---|---|
| member_id | Unique ID | ID | ID | Member_Id |
| member_name | Member Name | Name | Name | Member_Name |
| enrollment_date_raw | Date of Enrollment | EnrollmentDate | EnrollmentDate | Enrollment_Date |
| last_flight_date_raw | Date of Flight | Flight Date | FlightDate | Last_Flight_Date |
| tier_code | Tier Type | TierCode | TierCode | Tier_Code |
| agent_name | Not available | Not available | Not available | Agent_Name |
| state | Not available | Not available | Not available | State |
| post_code_raw | Not available | Not available | Not available | Post_Code, optional |
| dob_raw | Date of Birth | DOB | Not available | DOB |
| active_member | Not available | Not available | Not available | Is_Active |
| country | Source configuration: AUS | Source configuration: IND | Source configuration: USA | Country; AU normalized to AUS |
| individual_or_corporate | Not available | Individual or Corporate | Not available | Not available |

The staging layer parses ISO, timestamp-like, `YYYYMMDD`, and `MMDDYYYY` dates. Optional source-specific fields not provided by a feed remain NULL.

## Data Quality Findings and Assumptions

- Missing member ID or name and missing/invalid enrollment date are errors.
- Invalid flight dates, invalid/future DOB, enrollment after flight, unsupported country values, and duplicate key values are checked.
- DQ validation runs on raw rows by ingestion batch so rejected values remain traceable.
- The assessment declares Member Name as the key, and the Excel samples repeat `Mike` across AUS and USA. Both rows are reported by DQ and excluded from staging/current targets. If they are separate people, an immutable source key is needed to distinguish them safely. The resulting workbook staging sample has 6 rows: AUS 1, IND 3, USA 2.
- Redemption input supplies only member ID. Ambiguous IDs are retained as unmatched rather than assigned to an arbitrary profile.
- Raw values, source file, batch ID, and ingestion timestamp are retained for audit and troubleshooting.
