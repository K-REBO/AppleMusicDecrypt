#!/usr/bin/env python3
"""
Remove pronunciation (romaji) lines from LRC files.
Pronunciation lines have the same timestamp as the previous line and contain only ASCII characters.

Usage:
    python tools/remove_pronunciation.py [directory]
    # default directory: downloads/
"""

import re
import sys
from pathlib import Path

TIMESTAMP_RE = re.compile(r"^\[(\d{2}:\d{2}\.\d{2})\](.*)$")


def remove_pronunciation(text: str) -> tuple[str, int]:
    lines = text.splitlines()
    result = []
    removed = 0
    prev_timestamp = None

    for line in lines:
        m = TIMESTAMP_RE.match(line)
        if m:
            timestamp, content = m.group(1), m.group(2)
            if timestamp == prev_timestamp and content.isascii():
                removed += 1
                continue
            prev_timestamp = timestamp
        else:
            prev_timestamp = None
        result.append(line)

    return "\n".join(result), removed


def process_directory(root: Path):
    lrc_files = list(root.rglob("*.lrc"))
    if not lrc_files:
        print(f"No LRC files found in {root}")
        return

    total_removed = 0
    for path in lrc_files:
        original = path.read_text(encoding="utf-8")
        fixed, removed = remove_pronunciation(original)
        if removed > 0:
            path.write_text(fixed, encoding="utf-8")
            print(f"[{removed:3d} lines removed] {path}")
            total_removed += removed

    print(f"\nDone. {total_removed} pronunciation lines removed from {len(lrc_files)} files.")


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("downloads")
    if not root.exists():
        print(f"Directory not found: {root}")
        sys.exit(1)
    process_directory(root)
