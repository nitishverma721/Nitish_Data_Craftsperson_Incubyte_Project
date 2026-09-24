# Incubyte Data Craftsperson Assessment

This repository contains my solution for the Incubyte Data Craftsperson technical assessment.

## Problem Overview

The assessment involves processing member profile data and airline redemption transactions.

The solution covers:

- Raw/landing data ingestion
- Staging and data standardization
- Derived member attributes
- Data quality validations
- Latest-record-wins processing
- Country-specific member tables
- JSON redemption feed flattening
- Joining redemption transactions with member data
- Automated tests
- Scalability and production design considerations

## Repository Structure

```text
assessment/     Source assessment and sample input files
sql/            Snowflake DDL and transformation SQL
src/            Python implementation
tests/          Automated tests
docs/           Architecture and design documentation
```

Technology
Python
SQL
Snowflake
Pandas
Pytest
Design Approach

The implementation follows a layered data processing approach:

Source Files
|
v
Raw / Landing
|
v
Staging
|
v
Validation & Transformation
|
v
Country-specific Targets

The redemption JSON feed is processed separately and flattened into a queryable transaction structure.

Data Quality

The pipeline validates:

Mandatory fields
Key uniqueness
Date validity
Invalid or inconsistent source values
Duplicate records
Business-rule inconsistencies
Transformation results
Testing

Automated tests are included for the core transformation and validation logic.

Scalability

The design considers large-scale processing, including incremental processing, efficient transformations, data quality handling, and minimizing unnecessary full-table scans.


We'll improve this README substantially later. **Don't try to make it perfect now.**
