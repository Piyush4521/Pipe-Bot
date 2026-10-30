"""Script to scan all backend and documentation files for em dash characters.

Ensures compliance with strict formatting constraints.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

SCAN_DIRS = [
    ROOT / "backend" / "app",
    ROOT / "backend" / "scripts",
    ROOT / "backend" / "tests",
    ROOT / "backend" / "migrations",
    ROOT / "docs" / "database",
]

found = []

for sdir in SCAN_DIRS:
    if not sdir.exists():
        continue
    for root, _, files in os.walk(sdir):
        for fname in files:
            if fname.endswith((".py", ".md", ".json", ".sql")):
                fpath = Path(root) / fname
                try:
                    text = fpath.read_text(encoding="utf-8")
                    if "\u2014" in text:
                        found.append(str(fpath))
                except Exception as exc:
                    print(f"Error reading {fpath}: {exc}")

if found:
    print("Found em dashes in the following files:")
    for f in found:
        print(f" - {f}")
    sys.exit(1)
else:
    print("SUCCESS: Zero em dashes found across all scanned code, tests, and documentation files!")

