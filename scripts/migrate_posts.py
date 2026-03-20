"""Migrate flat _posts/*.md files into _posts/YYYY/MM/ subdirectories.

Run once from the repo root:
    python scripts/migrate_posts.py

Moves all .md files matching YYYY-MM-DD-*.md from _posts/ (flat) into
_posts/YYYY/MM/. Skips files already in a subdirectory.
"""

import re
import sys
from pathlib import Path

POSTS_DIR = Path("_posts")


def main() -> int:
    moved = 0
    skipped = 0
    errors = 0

    flat_posts = [
        p for p in POSTS_DIR.iterdir()
        if p.is_file() and p.suffix == ".md"
    ]

    if not flat_posts:
        print("No flat posts found in _posts/ — nothing to migrate.")
        return 0

    print(f"Found {len(flat_posts)} flat post(s) to migrate...")

    for path in sorted(flat_posts):
        match = re.match(r"^(\d{4})-(\d{2})-\d{2}-", path.name)
        if not match:
            print(f"  SKIP (unrecognised name): {path.name}")
            skipped += 1
            continue

        year, month = match.group(1), match.group(2)
        dest_dir = POSTS_DIR / year / month
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / path.name

        if dest.exists():
            print(f"  SKIP (already exists at dest): {dest}")
            skipped += 1
            continue

        try:
            path.rename(dest)
            moved += 1
        except Exception as exc:
            print(f"  ERROR moving {path.name}: {exc}")
            errors += 1

    print(f"\nDone. Moved: {moved}, Skipped: {skipped}, Errors: {errors}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
