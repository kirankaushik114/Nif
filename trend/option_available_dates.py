import zipfile
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIG
# ============================================================

OPTIONS_DIR = Path(
    r"D:\Nif\trend\data\options"
)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 75)
    print("OPTION DATA ACTUAL DATE RANGE")
    print("=" * 75)

    zip_files = sorted(
        OPTIONS_DIR.glob("*.zip")
    )

    if not zip_files:

        print()
        print("No ZIP files found.")
        return

    all_dates = []

    # --------------------------------------------------------
    # IMPORTANT:
    # Only inspect the most recent few ZIPs first.
    # The ZIP filename is expiry date, not necessarily
    # trading date.
    # --------------------------------------------------------

    recent_zips = zip_files[-8:]

    print()
    print(
        "Inspecting latest ZIP files:"
    )

    for zip_file in recent_zips:

        print(
            " ",
            zip_file.name
        )

    # --------------------------------------------------------
    # Read actual Date column
    # --------------------------------------------------------

    for zip_file in recent_zips:

        print()
        print(
            "Reading:",
            zip_file.name
        )

        try:

            with zipfile.ZipFile(
                zip_file,
                "r"
            ) as z:

                csv_files = [
                    name
                    for name in z.namelist()
                    if name.lower().endswith(
                        ".csv"
                    )
                ]

                for csv_file in csv_files:

                    # We only need Date.
                    df = pd.read_csv(
                        z.open(csv_file),
                        usecols=[
                            "Date"
                        ]
                    )

                    dates = pd.to_datetime(
                        df["Date"],
                        errors="coerce"
                    ).dt.date.dropna()

                    if len(dates):

                        min_date = min(dates)
                        max_date = max(dates)

                        all_dates.extend(
                            dates.tolist()
                        )

                        print(
                            f"  {csv_file}"
                        )

                        print(
                            f"    "
                            f"{min_date} "
                            f"-> "
                            f"{max_date}"
                        )

        except Exception as e:

            print(
                "  ERROR:",
                e
            )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    if not all_dates:

        print()
        print(
            "No trading dates found."
        )

        return

    unique_dates = sorted(
        set(all_dates)
    )

    print()
    print("=" * 75)
    print("ACTUAL OPTION DATA RANGE")
    print("=" * 75)

    print()
    print(
        "First trading date:",
        unique_dates[0]
    )

    print(
        "Last trading date :",
        unique_dates[-1]
    )

    print(
        "Trading days found:",
        len(unique_dates)
    )

    print()
    print(
        "Latest 20 trading dates:"
    )

    for date in unique_dates[-20:]:

        print(
            " ",
            date
        )

    print()
    print("=" * 75)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()