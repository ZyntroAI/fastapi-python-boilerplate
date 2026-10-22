import ctypes
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def main():
    if os.name != "nt":
        sys.exit("This script requires Windows.")

    if not ctypes.windll.shell32.IsUserAnAdmin():
        sys.exit(
            "Administrator access is required.
"
            "Open Command Prompt as administrator, then run this script."
        )

    dism = shutil.which("dism.exe")
    if not dism:
        sys.exit("DISM was not found.")

    command = [
        dism,
        "/Online",
        "/Cleanup-Image",
        "/AnalyzeComponentStore",
        "/English",
    ]

    report_dir = Path.home() / "WinSxS_Reports"
    report_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    report_path = report_dir / f"winsxs_analysis_{timestamp}.txt"

    print("Analyzing the component store. No cleanup will be performed.
")

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
    except OSError as error:
        sys.exit(f"Could not start DISM: {error}")

    output = result.stdout or "(No output returned.)"

    report_path.write_text(
        f"Date: {datetime.now().isoformat(timespec='seconds')}
"
        f"Command: {subprocess.list2cmdline(command)}
"
        f"Exit code: {result.returncode}

"
        f"{output}",
        encoding="utf-8",
    )

    print(output)
    print(f"
Report saved to: {report_path}")

    if result.returncode == 0:
        print("Analysis completed successfully.")
    else:
        print(
            f"DISM returned exit code {result.returncode}.
"
            "Review the report. No cleanup was attempted."
        )


if __name__ == "__main__":
    main()