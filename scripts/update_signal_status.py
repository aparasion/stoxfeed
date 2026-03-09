"""
Derives current_status for each signal in _data/signals.yml
by tallying weighted stances from all linked posts.

Weighting:  high=3, medium=2, low=1
Rules:
  - supported  : supports_score > 0 and supports_score >= 2 * contradicts_score
  - challenged : contradicts_score > supports_score
  - mixed      : both sides present but neither dominates
  - emerging   : no supporting/contradicting evidence yet
"""

import re
import sys
from pathlib import Path

SIGNALS_FILE = Path("_data/signals.yml")
POSTS_DIR = Path("_posts")

CONFIDENCE_WEIGHT = {"high": 3, "medium": 2, "low": 1}


def parse_front_matter(text: str) -> dict:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    fm = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fm[key.strip()] = value.strip()
    return fm


def parse_inline_list(value: str) -> list[str]:
    cleaned = (value or "").strip()
    if not cleaned.startswith("[") or not cleaned.endswith("]"):
        return []
    return [item.strip().strip('"').strip("'") for item in cleaned[1:-1].split(",") if item.strip()]


def load_signal_ids() -> list[str]:
    ids = []
    for line in SIGNALS_FILE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- id:"):
            ids.append(stripped.split(":", 1)[1].strip().strip('"').strip("'"))
    return ids


def tally_stances(signal_ids: list[str]) -> dict[str, dict]:
    """Returns {signal_id: {supports, contradicts, mixed, mentions}} weighted scores."""
    tallies: dict[str, dict] = {sid: {"supports": 0, "contradicts": 0, "mixed": 0, "mentions": 0} for sid in signal_ids}

    for path in POSTS_DIR.glob("*.md"):
        fm = parse_front_matter(path.read_text(encoding="utf-8"))
        ids = parse_inline_list(fm.get("signal_ids", ""))
        if not ids:
            continue
        stance = fm.get("signal_stance", "mentions").strip().strip('"').strip("'")
        confidence = fm.get("signal_confidence", "low").strip().strip('"').strip("'")
        weight = CONFIDENCE_WEIGHT.get(confidence, 1)

        for sid in ids:
            if sid in tallies and stance in tallies[sid]:
                tallies[sid][stance] += weight

    return tallies


def derive_status(tally: dict) -> str:
    s = tally["supports"]
    c = tally["contradicts"]

    if s == 0 and c == 0:
        return "emerging"
    if c > s:
        return "challenged"
    if s >= 2 * c:
        return "supported"
    return "mixed"


def update_signals_yml(new_statuses: dict[str, str]) -> bool:
    """Update current_status lines in signals.yml in-place. Returns True if any change was made."""
    text = SIGNALS_FILE.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    current_signal_id = None
    changed = False
    updated_lines = []

    for line in lines:
        id_match = re.match(r"^- id:\s*(\S+)", line)
        if id_match:
            current_signal_id = id_match.group(1).strip('"\'')

        status_match = re.match(r"^(\s*current_status:\s*)(\S+)", line)
        if status_match and current_signal_id in new_statuses:
            new_status = new_statuses[current_signal_id]
            old_status = status_match.group(2)
            if old_status != new_status:
                line = f"{status_match.group(1)}{new_status}\n"
                changed = True
                print(f"  {current_signal_id}: {old_status} → {new_status}")

        updated_lines.append(line)

    if changed:
        SIGNALS_FILE.write_text("".join(updated_lines), encoding="utf-8")

    return changed


def main() -> int:
    signal_ids = load_signal_ids()
    tallies = tally_stances(signal_ids)

    new_statuses = {}
    for sid in signal_ids:
        new_statuses[sid] = derive_status(tallies[sid])

    print("Derived statuses:")
    for sid, status in new_statuses.items():
        t = tallies[sid]
        print(f"  {sid}: {status}  (supports={t['supports']}, contradicts={t['contradicts']}, mixed={t['mixed']}, mentions={t['mentions']})")

    changed = update_signals_yml(new_statuses)
    if changed:
        print("signals.yml updated.")
    else:
        print("No status changes needed.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
