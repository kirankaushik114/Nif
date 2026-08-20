import requests
import re
from urllib.parse import urljoin


URL = "https://www.nseix.com/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/142.0 Safari/537.36"
    )
}


def main():

    print("=" * 80)
    print("NSE IX API DISCOVERY")
    print("=" * 80)

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )

    print()
    print("Status :", response.status_code)
    print("Length :", len(response.text))

    html = response.text

    # --------------------------------------------------------
    # Find JavaScript files
    # --------------------------------------------------------

    scripts = re.findall(
        r'<script[^>]+src=["\']([^"\']+)["\']',
        html,
        re.IGNORECASE
    )

    print()
    print("JavaScript files:", len(scripts))

    api_keywords = [
        "api",
        "market",
        "quote",
        "ticker",
        "future",
        "gift",
        "price",
        "historical",
        "ohlc",
        "index"
    ]

    found = set()

    # --------------------------------------------------------
    # Download JS files
    # --------------------------------------------------------

    for script in scripts:

        script_url = urljoin(
            URL,
            script
        )

        print()
        print("Checking:")
        print(script_url)

        try:

            js_response = requests.get(
                script_url,
                headers=HEADERS,
                timeout=30
            )

            if js_response.status_code != 200:
                print(
                    "Status:",
                    js_response.status_code
                )
                continue

            js = js_response.text

            # ------------------------------------------------
            # Find URL-like strings
            # ------------------------------------------------

            urls = re.findall(
                r'https?://[^"\']+',
                js
            )

            for item in urls:

                lower = item.lower()

                if any(
                    keyword in lower
                    for keyword in api_keywords
                ):

                    found.add(item)

            # ------------------------------------------------
            # Find relative API paths
            # ------------------------------------------------

            paths = re.findall(
                r'["\']([^"\']*(?:api|market|quote|ticker|'
                r'gift|future|historical|ohlc|price)'
                r'[^"\']*)["\']',
                js,
                re.IGNORECASE
            )

            for item in paths:

                if len(item) < 300:

                    found.add(
                        urljoin(
                            URL,
                            item
                        )
                    )

        except Exception as error:

            print(
                "Error:",
                error
            )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("POSSIBLE NSE IX DATA ENDPOINTS")
    print("=" * 80)

    if not found:

        print()
        print(
            "No obvious API endpoints found."
        )

    else:

        for item in sorted(found):

            print(item)

    print()
    print("=" * 80)
    print("COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()