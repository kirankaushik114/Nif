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

    print("=" * 70)
    print("OPTION DATA CHECK")
    print("=" * 70)

    print()
    print("Folder:")
    print(OPTIONS_DIR)

    # --------------------------------------------------------
    # Check folder
    # --------------------------------------------------------

    if not OPTIONS_DIR.exists():

        print()
        print("OPTIONS FOLDER DOES NOT EXIST.")
        print()
        print("Create it with:")
        print(
            r"mkdir D:\Nif\trend\data\options"
        )

        return

    # --------------------------------------------------------
    # Find files
    # --------------------------------------------------------

    files = []

    for path in OPTIONS_DIR.rglob("*"):

        if not path.is_file():
            continue

        if path.suffix.lower() in {
            ".csv",
            ".zip",
            ".xlsx",
            ".xls",
            ".parquet",
        }:

            files.append(path)

    if not files:

        print()
        print("NO OPTION DATA FILES FOUND.")
        print()
        print(
            "Download/extract the Dropbox data into:"
        )
        print(OPTIONS_DIR)

        return

    print()
    print(
        f"FILES FOUND: {len(files)}"
    )

    # --------------------------------------------------------
    # Inspect each file
    # --------------------------------------------------------

    for file in sorted(files):

        print()
        print("=" * 70)
        print("FILE:")
        print(file)
        print("=" * 70)

        size_mb = (
            file.stat().st_size
            / (1024 * 1024)
        )

        print(
            f"Size: {size_mb:.2f} MB"
        )

        # ----------------------------------------------------
        # CSV
        # ----------------------------------------------------

        if file.suffix.lower() == ".csv":

            try:

                df = pd.read_csv(
                    file,
                    nrows=5
                )

                print()
                print("COLUMNS:")
                print()

                for column in df.columns:

                    print(
                        f"  {column}"
                    )

                print()
                print("FIRST 5 ROWS:")
                print()

                print(
                    df.to_string(
                        index=False
                    )
                )

            except Exception as e:

                print()
                print(
                    "CSV READ ERROR:"
                )

                print(e)

        # ----------------------------------------------------
        # Excel
        # ----------------------------------------------------

        elif file.suffix.lower() in {
            ".xlsx",
            ".xls",
        }:

            try:

                df = pd.read_excel(
                    file,
                    nrows=5
                )

                print()
                print("COLUMNS:")
                print()

                for column in df.columns:

                    print(
                        f"  {column}"
                    )

                print()
                print("FIRST 5 ROWS:")
                print()

                print(
                    df.to_string(
                        index=False
                    )
                )

            except Exception as e:

                print()
                print(
                    "EXCEL READ ERROR:"
                )

                print(e)

        # ----------------------------------------------------
        # ZIP
        # ----------------------------------------------------

        elif file.suffix.lower() == ".zip":

            print()
            print(
                "ZIP FILE FOUND."
            )

            print(
                "ZIP will be inspected separately."
            )

        # ----------------------------------------------------
        # PARQUET
        # ----------------------------------------------------

        elif file.suffix.lower() == ".parquet":

            try:

                df = pd.read_parquet(
                    file
                )

                print()
                print(
                    "PARQUET COLUMNS:"
                )

                print()

                for column in df.columns:

                    print(
                        f"  {column}"
                    )

                print()
                print(
                    "FIRST 5 ROWS:"
                )

                print()

                print(
                    df.head().to_string(
                        index=False
                    )
                )

            except Exception as e:

                print()
                print(
                    "PARQUET READ ERROR:"
                )

                print(e)

    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("OPTION DATA CHECK COMPLETE")
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()