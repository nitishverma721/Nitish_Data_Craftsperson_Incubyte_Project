import os
from contextlib import contextmanager

import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

REQUIRED_ENV_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_SCHEMA",
]


def _validate_environment() -> None:
    """Fail fast when required Snowflake configuration is missing."""
    missing = [
        variable
        for variable in REQUIRED_ENV_VARS
        if not os.getenv(variable)
    ]

    if missing:
        raise RuntimeError(
            "Missing required Snowflake environment variables: "
            + ", ".join(missing)
        )


@contextmanager
def get_snowflake_connection():
    """Create and safely close a Snowflake connection."""
    _validate_environment()

    connection = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
    )

    try:
        yield connection
    finally:
        connection.close()
