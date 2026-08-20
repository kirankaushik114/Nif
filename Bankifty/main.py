import subprocess
import sys
from pathlib import Path

from monitor.continuous_monitor import (
    ContinuousBankNiftyMonitor
)


# ============================================================
# START DASHBOARD
# ============================================================

def start_dashboard():

    dashboard_file = (
        Path(__file__).resolve()
        .parent
        / "dashboard"
        / "app.py"
    )

    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(dashboard_file),
            "--server.headless",
            "true",
            "--server.port",
            "8501",
        ]
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Start Streamlit dashboard automatically
    # --------------------------------------------------------

    dashboard_process = (
        start_dashboard()
    )

    # --------------------------------------------------------
    # Start Bank Nifty monitor
    # --------------------------------------------------------

    monitor = (
        ContinuousBankNiftyMonitor()
    )

    try:

        monitor.run()

    finally:

        # ----------------------------------------------------
        # Stop dashboard when main.py is stopped
        # ----------------------------------------------------

        if (
            dashboard_process
            and
            dashboard_process.poll()
            is None
        ):

            dashboard_process.terminate()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()