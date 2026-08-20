from pathlib import Path
import zipfile
import csv
import io


# ============================================================
# CONFIG
# ============================================================

OPTIONS_DIR = Path(
    r"D:\Nif\trend\data\options"
)

TEST_ZIP = (
    OPTIONS_DIR
    / "20260505.zip"
)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 75)
    print("NIFTY OPTION ZIP INSPECTOR")
    print("=" * 75)

    print()
    print("ZIP:")
    print(TEST_ZIP)

    if not TEST_ZIP.exists():

        print()
        print("ZIP FILE NOT FOUND.")
        return

    print()
    print(
        f"ZIP SIZE: "
        f"{TEST_ZIP.stat().st_size / (1024 * 1024):.2f} MB"
    )

    # --------------------------------------------------------
    # Open ZIP
    # --------------------------------------------------------

    with zipfile.ZipFile(
        TEST_ZIP,
        "r"
    ) as z:

        names = z.namelist()

        print()
        print("=" * 75)
        print("FILES INSIDE ZIP")
        print("=" * 75)

        print()

        for name in names:

            print(name)

        print()

        print(
            f"TOTAL FILES: {len(names)}"
        )

        # ----------------------------------------------------
        # Find likely data files
        # ----------------------------------------------------

        data_files = []

        for name in names:

            lower = name.lower()

            if lower.endswith(
                (
                    ".csv",
                    ".txt",
                    ".json",
                    ".parquet",
                )
            ):

                data_files.append(name)

        print()
        print("=" * 75)
        print("LIKELY DATA FILES")
        print("=" * 75)

        print()

        if not data_files:

            print(
                "No CSV/TXT/JSON/Parquet files found."
            )

            return

        for name in data_files:

            print(name)

        # ----------------------------------------------------
        # Inspect first data file
        # ----------------------------------------------------

        first_file = data_files[0]

        print()
        print("=" * 75)
        print("INSPECTING")
        print("=" * 75)

        print()
        print(first_file)

        with z.open(
            first_file
        ) as f:

            raw = f.read(
                10000
            )

        # ----------------------------------------------------
        # Decode
        # ----------------------------------------------------

        text = raw.decode(
            "utf-8",
            errors="replace"
        )

        print()
        print("=" * 75)
        print("FIRST DATA")
        print("=" * 75)

        print()

        print(
            text[:5000]
        )

        # ----------------------------------------------------
        # Try CSV detection
        # ----------------------------------------------------

        print()
        print("=" * 75)
        print("CSV ANALYSIS")
        print("=" * 75)

        print()

        try:

            sample = text[:10000]

            dialect = csv.Sniffer().sniff(
                sample
            )

            print(
                "Detected delimiter:",
                repr(
                    dialect.delimiter
                )
            )

            reader = csv.reader(
                io.StringIO(text),
                dialect
            )

            rows = []

            for i, row in enumerate(reader):

                rows.append(row)

                if i >= 4:
                    break

            print()
            print("FIRST 5 ROWS:")

            for row in rows:

                print(row)

        except Exception as e:

            print(
                "CSV detection failed:"
            )

            print(e)

    print()
    print("=" * 75)
    print("INSPECTION COMPLETE")
    print("=" * 75)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()