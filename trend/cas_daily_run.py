import subprocess
import sys
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(r"D:\Nif\trend")

PYTHON = (
    BASE_DIR
    / ".venv"
    / "Scripts"
    / "python.exe"
)

SCRIPTS = [
    BASE_DIR / "nifty_collector.py",
    BASE_DIR / "cas_nifty_v2.py",
    BASE_DIR / "cas_daily_forecast.py",
    BASE_DIR / "cas_decision_engine.py",
]


# ============================================================
# RUN SCRIPT
# ============================================================

def run_script(script):

    print()
    print("=" * 80)
    print(
        f"RUNNING: {script.name}"
    )
    print("=" * 80)
    print()

    result = subprocess.run(
        [
            str(PYTHON),
            str(script),
        ],
        cwd=str(BASE_DIR),
    )

    if result.returncode != 0:

        print()
        print("=" * 80)
        print(
            f"FAILED: {script.name}"
        )
        print(
            f"Exit code: {result.returncode}"
        )
        print("=" * 80)

        return False

    print()
    print(
        f"COMPLETED: {script.name}"
    )

    return True


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 80)
    print("CAS DAILY MASTER RUN")
    print("=" * 80)

    print()
    print(
        "Python:",
        PYTHON
    )

    # --------------------------------------------------------
    # Verify Python
    # --------------------------------------------------------

    if not PYTHON.exists():

        raise FileNotFoundError(
            f"Python environment not found:\n{PYTHON}"
        )

    # --------------------------------------------------------
    # Verify scripts
    # --------------------------------------------------------

    for script in SCRIPTS:

        if not script.exists():

            raise FileNotFoundError(
                f"Script not found:\n{script}"
            )

    # --------------------------------------------------------
    # Run pipeline
    # --------------------------------------------------------

    for script in SCRIPTS:

        success = run_script(
            script
        )

        if not success:

            print()
            print(
                "MASTER RUN STOPPED."
            )

            sys.exit(1)

    # ========================================================
    # COMPLETE
    # ========================================================

    print()
    print("=" * 80)
    print("CAS DAILY MASTER RUN COMPLETE")
    print("=" * 80)

    print()

    print(
        "Training data:"
    )

    print(
        BASE_DIR
        / "data"
        / "nifty_free_training.csv"
    )

    print()

    print(
        "V2 forecast:"
    )

    print(
        BASE_DIR
        / "data"
        / "cas_nifty_v2.csv"
    )

    print()

    print(
        "Daily forecast:"
    )

    print(
        BASE_DIR
        / "data"
        / "cas_daily_forecast.csv"
    )

    print()

    print(
        "Final decision:"
    )

    print(
        BASE_DIR
        / "data"
        / "cas_decision.csv"
    )

    print()
    print("=" * 80)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()