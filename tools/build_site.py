#!/usr/bin/env python3
"""Check the La Guinguette supporter list and copy it into the folder GitHub Pages publishes.

    python tools/build_site.py

Reads   supporters.json   the Ko-fi supporters named on the About page of the world's menu
Writes  _site/            supporters.json, cleaned (spaces collapsed, empty names left out)

If the file is not valid, the build fails, nothing is published and the live list stays as it was.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IN_ACTIONS = os.environ.get("GITHUB_ACTIONS") == "true"


def warn(message: str, file: str | None = None) -> None:
    """Print a warning; on GitHub Actions it also shows on the workflow run."""
    if IN_ACTIONS:
        print(f"::warning{' file=' + file if file else ''}::{message}")
    else:
        print(f"warning: {message}")


def fail(message: str, file: str | None = None, line: int | None = None) -> None:
    if IN_ACTIONS:
        location = (f" file={file}" if file else "") + (f",line={line}" if file and line else "")
        print(f"::error{location}::{message}")
    sys.exit(f"error: {message}")


def load_supporters(path: Path) -> list[str]:
    """The supporter names in file order, with runs of spaces collapsed and empty names left out."""
    if not path.exists():
        fail(f"{path.name} is missing", path.name)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        fail(f"{path.name} is not valid JSON: {error.msg} (line {error.lineno}, column {error.colno})", path.name, error.lineno)
    names = data.get("supporters") if isinstance(data, dict) else None
    if not isinstance(names, list):
        fail(f'{path.name} must contain {{"supporters": ["name", ...]}}', path.name)
    cleaned = []
    for name in names:
        if not isinstance(name, str):
            warn(f"{name!r} is not a text value: left out", path.name)
            continue
        name = re.sub(r"\s+", " ", name).strip()
        if name:
            cleaned.append(name)
    return cleaned


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the La Guinguette supporter list and copy it into _site/.")
    parser.add_argument("--supporters", type=Path, default=ROOT / "supporters.json", help="Ko-fi supporter names (default: supporters.json)")
    parser.add_argument("--out", type=Path, default=ROOT / "_site", help="output folder (default: _site/)")
    args = parser.parse_args()
    supporters = load_supporters(args.supporters)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "supporters.json").write_text(json.dumps({"supporters": supporters}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(supporters)} supporter(s)")


if __name__ == "__main__":
    main()
