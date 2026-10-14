"""Development entry point for the Electron application."""

import subprocess
import sys
from pathlib import Path


def main():
    folder = Path(__file__).resolve().parent / "electron"
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    subprocess.run([npm, "start"], cwd=folder, check=True)


if __name__ == "__main__":
    main()
