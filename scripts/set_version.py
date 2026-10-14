"""Keep API, Electron, lockfile, footer and README release versions aligned."""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def current_version():
    source = (ROOT / "backend/app/version.py").read_text(encoding="utf-8")
    return re.search(r'VERSION = "(\d+\.\d+\.\d+)"', source).group(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", nargs="?")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    version = args.version or current_version()
    if not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", version):
        parser.error("Expected a release version such as 1.0.0 (without the v prefix).")
    if args.check and args.version:
        parser.error("--check reads the current version; do not supply a new one.")
    changes = {}
    module = ROOT / "backend/app/version.py"
    changes[module] = re.sub(
        r'VERSION = "[^\"]+"', f'VERSION = "{version}"', module.read_text(encoding="utf-8")
    )
    for filename in ["package.json", "package-lock.json"]:
        path = ROOT / "desktop/electron" / filename
        data = json.loads(path.read_text(encoding="utf-8"))
        data["version"] = version
        if filename == "package-lock.json":
            data["packages"][""]["version"] = version
        changes[path] = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    index = ROOT / "backend/app/static/index.html"
    html = index.read_text(encoding="utf-8")
    if not re.search(r'<span id="appVersion">[^<]*</span>', html):
        raise SystemExit("Missing footer version element.")
    changes[index] = re.sub(
        r'<span id="appVersion">[^<]*</span>', f'<span id="appVersion">v{version}</span>', html
    )
    readme = ROOT / "README.md"
    changes[readme] = re.sub(
        r"\*\*Current release: v\d+\.\d+\.\d+\*\*",
        f"**Current release: v{version}**",
        readme.read_text(encoding="utf-8"),
    )
    if args.check:
        stale = [
            str(path.relative_to(ROOT))
            for path, text in changes.items()
            if path.read_text(encoding="utf-8") != text
        ]
        if stale:
            raise SystemExit("Release version metadata needs synchronization: " + ", ".join(stale))
        print(f"Release metadata verified: v{version}")
    else:
        for path, text in changes.items():
            path.write_text(text, encoding="utf-8", newline="\n")
        print(f"Release version set to v{version}")


if __name__ == "__main__":
    main()
