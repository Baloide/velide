"""Format the project's JavaScript consistently; use --check for a read-only gate."""

import argparse
from pathlib import Path

import jsbeautifier

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    options = jsbeautifier.default_options()
    options.indent_size = 2
    # Avoid the beautifier's repeated soft-wrap drift; preserve deliberate breaks.
    options.wrap_line_length = 0
    options.max_preserve_newlines = 2
    paths = sorted((ROOT / "backend/app/static").glob("*.js"))
    paths += sorted((ROOT / "scripts").glob("*.cjs"))
    paths += sorted((ROOT / "desktop/electron").glob("*.cjs"))
    changed = []
    for path in paths:
        original = path.read_text(encoding="utf-8-sig")
        formatted = jsbeautifier.beautify(original, options).rstrip() + "\n"
        if original != formatted:
            changed.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.write_text(formatted, encoding="utf-8", newline="\n")
    if args.check and changed:
        raise SystemExit("Formatting required: " + ", ".join(changed))
    print(
        "JavaScript formatting verified."
        if args.check
        else f"Formatted {len(changed)} JavaScript files."
    )


if __name__ == "__main__":
    main()
