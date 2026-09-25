import pandas as pd


MEMBER_PROFILE_COLUMNS = [
    "member_id",
    "member_name",
    "country",
    "tier_code",
]


def build_member_redemption_join(
    redemptions: pd.DataFrame,
    members: pd.DataFrame,
) -> pd.DataFrame:
    """Enrich only unambiguous member IDs while retaining every redemption."""
    profiles = members[MEMBER_PROFILE_COLUMNS]
    unique_member_ids = profiles["member_id"].value_counts()
    unique_member_ids = unique_member_ids[unique_member_ids == 1].index
    unambiguous_profiles = profiles[
        profiles["member_id"].isin(unique_member_ids)
    ]

    return redemptions.merge(
        unambiguous_profiles,
        on="member_id",
        how="left",
        validate="many_to_one",
    )
