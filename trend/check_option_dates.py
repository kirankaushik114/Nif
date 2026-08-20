from pathlib import Path
from datetime import datetime


# ============================================================
# CONFIG
# ============================================================

OPTIONS_DIR = Path(
    r"D:\Nif\trend\data\options"
)


# ============================================================
# GET ZIP DATE
# ============================================================

def get_zip_date(filename):

    name = filename.lower()

    if not name.endswith(".zip"):
        return None

    name = name[:-4]

    try:
        return datetime.strptime(
            name,
            "%Y%m%d"
        ).date()

    except ValueError:
        return None


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 75)
    print("NIFTY OPTION ZIP DATE CHECK")
    print("=" * 75)

    print()
    print("Folder:")
    print(OPTIONS_DIR)

    if not OPTIONS_DIR.exists():

        print()
        print("ERROR:")
        print("Options folder does not exist.")

        print()
        print(
            r"Create it with:"
        )

        print(
            r"mkdir D:\Nif\trend\data\options"
        )

        return

    # --------------------------------------------------------
    # Find ZIP files
    # --------------------------------------------------------

    records = []

    for file in OPTIONS_DIR.glob("*.zip"):

        zip_date = get_zip_date(
            file.name
        )

        if zip_date is None:
            continue

        records.append(
            (
                zip_date,
                file
            )
        )

    records.sort(
        key=lambda x: x[0]
    )

    # --------------------------------------------------------
    # No files
    # --------------------------------------------------------

    if not records:

        print()
        print("NO OPTION ZIP FILES FOUND.")

        return

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print()
    print("=" * 75)
    print("OPTION ZIP FILES")
    print("=" * 75)

    print()

    for zip_date, file in records:

        size_mb = (
            file.stat().st_size
            / (1024 * 1024)
        )

        print(
            f"{zip_date}    "
            f"{file.name:20}    "
            f"{size_mb:8.2f} MB"
        )

    # --------------------------------------------------------
    # Range
    # --------------------------------------------------------

    first_date = records[0][0]

    last_date = records[-1][0]

    print()
    print("=" * 75)
    print("SUMMARY")
    print("=" * 75)

    print()
    print(
        "Number of ZIP files:",
        len(records)
    )

    print(
        "First ZIP date:",
        first_date
    )

    print(
        "Last ZIP date :",
        last_date
    )

    # --------------------------------------------------------
    # August check
    # --------------------------------------------------------

    august_files = [
        (date, file)
        for date, file in records
        if date.year == 2026
        and date.month == 8
    ]

    print()

    if august_files:

        print(
            "AUGUST 2026 DATA: FOUND"
        )

        print()

        for date, file in august_files:

            print(
                f"  {date} -> {file.name}"
            )

    else:

        print(
            "AUGUST 2026 DATA: NOT FOUND"
        )

    # --------------------------------------------------------
    # June / July / August
    # --------------------------------------------------------

    print()
    print(
        "Recent 2026 files:"
    )

    recent = [
        (date, file)
        for date, file in records
        if date >= datetime(
            2026,
            6,
            1
        ).date()
    ]

    if recent:

        for date, file in recent:

            print(
                f"  {date} -> {file.name}"
            )

    else:

        print(
            "  None"
        )

    print()
    print("=" * 75)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()