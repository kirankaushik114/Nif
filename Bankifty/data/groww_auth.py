"""
Groww Authentication Test

API Key + API Secret authentication.

ALERT ONLY.
No orders are placed.
"""

from growwapi import GrowwAPI

from config.settings import (
    GROWW_API_KEY,
    GROWW_API_SECRET,
)


def create_groww_client():
    """
    Authenticate with Groww using API Key + API Secret.

    Returns:
        GrowwAPI: authenticated Groww client
    """

    if not GROWW_API_KEY:
        raise ValueError(
            "GROWW_API_KEY is missing in .env"
        )

    if not GROWW_API_SECRET:
        raise ValueError(
            "GROWW_API_SECRET is missing in .env"
        )

    print("Creating Groww API client...")

    # Correct Groww authentication parameters:
    # api_key + secret
    access_token = GrowwAPI.get_access_token(
        api_key=GROWW_API_KEY,
        secret=GROWW_API_SECRET,
    )

    print("Access token generated successfully.")

    # Initialize authenticated Groww client
    groww = GrowwAPI(access_token)

    print("Groww API authentication successful.")

    return groww


def main():

    print()
    print("=" * 65)
    print("GROWW AUTHENTICATION TEST")
    print("=" * 65)

    try:

        groww = create_groww_client()

        print()
        # print("Authentication : SUCCESS")
        # print("Groww client   : READY")
        # print("Orders         : DISABLED")
        print()
        print("=" * 65)

    except Exception as error:

        print()
        print("=" * 65)
        print("GROWW AUTHENTICATION FAILED")
        print("=" * 65)

        print("Error type:")
        print(type(error).__name__)

        print()
        print("Error:")
        print(error)

        print()
        print("=" * 65)


if __name__ == "__main__":
    main()