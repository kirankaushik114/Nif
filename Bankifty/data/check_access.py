"""
Groww Account Access Test

READ ONLY
No orders.
"""

from growwapi import GrowwAPI

from config.settings import (
    GROWW_API_KEY,
    GROWW_API_SECRET,
)


def main():

    print()
    print("=" * 70)
    print("GROWW ACCOUNT ACCESS TEST")
    print("=" * 70)

    try:

        print("Authenticating with Groww...")

        access_token = GrowwAPI.get_access_token(
            api_key=GROWW_API_KEY,
            secret=GROWW_API_SECRET,
        )

        groww = GrowwAPI(access_token)

        print("Authentication : SUCCESS")

        print()
        print("Requesting user profile...")

        profile = groww.get_user_profile()

        print()
        print("=" * 70)
        print("GROWW USER PROFILE")
        print("=" * 70)

        print(profile)

        print()
        print("=" * 70)

        if isinstance(profile, dict):

            print(
                "NSE Enabled     :",
                profile.get("nse_enabled")
            )

            print(
                "BSE Enabled     :",
                profile.get("bse_enabled")
            )

            print(
                "Active Segments :",
                profile.get("active_segments")
            )

            print(
                "DDPI Enabled    :",
                profile.get("ddpi_enabled")
            )

        print()
        print("ACCOUNT ACCESS TEST : SUCCESS")
        print("=" * 70)

    except Exception as error:

        print()
        print("=" * 70)
        print("ACCOUNT ACCESS TEST : FAILED")
        print("=" * 70)

        print(
            "Error type:",
            type(error).__name__
        )

        print(
            "Error:",
            error
        )

        print("=" * 70)


if __name__ == "__main__":
    main()