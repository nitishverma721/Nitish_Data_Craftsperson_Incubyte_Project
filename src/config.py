from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSESSMENT_DIR = PROJECT_ROOT / "assessment"

COUNTRY_CODE_ALIASES = {
    "AU": "AUS",
}

SUPPORTED_COUNTRIES = {"AUS", "IND", "USA", "PHIL", "CAN"}

SOURCE_CONFIG = {
    "AUS.xlsx": {
        "country": "AUS",
        "column_mapping": {
            "Unique ID": "member_id",
            "Member Name": "member_name",
            "Tier Type": "tier_code",
            "Date of Birth": "dob_raw",
            "Date of Enrollment": "enrollment_date_raw",
            "Date of Flight": "last_flight_date_raw",
        },
    },
    "IND.xlsx": {
        "country": "IND",
        "column_mapping": {
            "ID": "member_id",
            "Name": "member_name",
            "TierCode": "tier_code",
            "DOB": "dob_raw",
            "EnrollmentDate": "enrollment_date_raw",
            "Individual or Corporate": "individual_or_corporate",
            "Flight Date": "last_flight_date_raw",
        },
    },
    "USA.xlsx": {
        "country": "USA",
        "column_mapping": {
            "ID": "member_id",
            "Name": "member_name",
            "TierCode": "tier_code",
            "EnrollmentDate": "enrollment_date_raw",
            "FlightDate": "last_flight_date_raw",
        },
    },
}
