import zipfile
from pathlib import Path
import re


OPTIONS_DIR = Path(
    r"D:\Nif\trend\data\options"
)

# Latest ZIP only
zip_files = sorted(
    OPTIONS_DIR.glob("*.zip")
)

if not zip_files:
    print("No ZIP files found.")
    raise SystemExit(1)

latest_zip = zip_files[-1]

print("=" * 75)
print("OPTION ZIP STRUCTURE CHECK")
print("=" * 75)

print()
print("Latest ZIP:")
print(latest_zip)

with zipfile.ZipFile(
    latest_zip,
    "r"
) as z:

    names = z.namelist()

print()
print("Files inside ZIP:", len(names))

# ------------------------------------------------------------
# Find option contract files
# ------------------------------------------------------------

contracts = []

for name in names:

    filename = Path(name).name

    match = re.match(
        r"^(\d+)(CE|PE)_(\d{8})\.csv$",
        filename,
        re.IGNORECASE
    )

    if match:

        strike = int(
            match.group(1)
        )

        option_type = (
            match.group(2).upper()
        )

        expiry = match.group(3)

        contracts.append(
            (
                strike,
                option_type,
                expiry,
                name
            )
        )

# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

print()
print("=" * 75)
print("CONTRACT SUMMARY")
print("=" * 75)

print()

if not contracts:

    print(
        "No option contract files found."
    )

else:

    strikes = sorted(
        set(
            x[0]
            for x in contracts
        )
    )

    print(
        "Contracts:",
        len(contracts)
    )

    print(
        "Strikes:",
        len(strikes)
    )

    print()

    print(
        "Minimum strike:",
        min(strikes)
    )

    print(
        "Maximum strike:",
        max(strikes)
    )

    print()

    print(
        "First 30 contracts:"
    )

    for item in contracts[:30]:

        print(
            " ",
            item
        )

# ------------------------------------------------------------
# NIFTY spot
# ------------------------------------------------------------

print()
print("=" * 75)
print("NIFTY SPOT FILE")
print("=" * 75)

spot_files = [
    name
    for name in names
    if Path(name).name.lower()
    == "nifty_spot.csv"
]

if spot_files:

    print(
        "FOUND:",
        spot_files[0]
    )

else:

    print(
        "NIFTY SPOT NOT FOUND"
    )

print()
print("=" * 75)
print("COMPLETE")
print("=" * 75)