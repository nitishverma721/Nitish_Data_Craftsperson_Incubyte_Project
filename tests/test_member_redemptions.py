import pandas as pd


def build_member_redemption_join(
    redemptions: pd.DataFrame,
    members: pd.DataFrame,
) -> pd.DataFrame:
    """Enrich redemption records with the current member profile."""
    return redemptions.merge(
        members[
            [
                "member_id",
                "member_name",
                "country",
                "tier_code",
            ]
        ],
        on="member_id",
        how="left",
    )


def test_redemption_is_enriched_with_member_profile():
    redemptions = pd.DataFrame(
        [
            {
                "member_id": "101",
                "transaction_id": "TX1001",
                "miles_redeemed": 5000,
            }
        ]
    )

    members = pd.DataFrame(
        [
            {
                "member_id": "101",
                "member_name": "John Smith",
                "country": "IND",
                "tier_code": "GLD",
            }
        ]
    )

    result = build_member_redemption_join(redemptions, members)

    assert len(result) == 1
    assert result.iloc[0]["member_name"] == "John Smith"
    assert result.iloc[0]["country"] == "IND"
    assert result.iloc[0]["tier_code"] == "GLD"


def test_unmatched_redemption_is_not_dropped():
    redemptions = pd.DataFrame(
        [
            {
                "member_id": "999",
                "transaction_id": "TX1002",
                "miles_redeemed": 3000,
            }
        ]
    )

    members = pd.DataFrame(
        [
            {
                "member_id": "101",
                "member_name": "John Smith",
                "country": "IND",
                "tier_code": "GLD",
            }
        ]
    )

    result = build_member_redemption_join(redemptions, members)

    assert len(result) == 1
    assert result.iloc[0]["member_id"] == "999"
    assert pd.isna(result.iloc[0]["member_name"])
