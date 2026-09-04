#!/usr/bin/env python3
"""Extract quest.tbb text fields with their source positions and byte budgets."""
import json
import re
import sys
from pathlib import Path

from tbb_parser import parse_tbb

JP_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]")


def decode(value: bytes) -> str:
    return value.decode("shift_jis", errors="replace")


def budget(value: str) -> tuple[int, bool]:
    try:
        return len(value.encode("cp949")), True
    except UnicodeEncodeError:
        return len(value.encode("cp949", errors="replace")), False


def extract(path: Path) -> list[dict]:
    parsed = parse_tbb(path)
    rows = [[decode(value) for value in row] for row in parsed["records"]]
    quests = []
    current = None
    pending_header = False

    for row_index, row in enumerate(rows):
        marker_index = row.index("[QUEST]") if "[QUEST]" in row else None
        quest_id = ""
        if marker_index is not None:
            quest_id = next((value for value in row[marker_index + 1:] if value), "")
            pending_header = not bool(re.fullmatch(r"GF_QUEST_\d+", quest_id))
        elif pending_header:
            quest_id = next((value for value in row if re.fullmatch(r"GF_QUEST_\d+", value)), "")
            pending_header = False
        if quest_id:
            current = {
                "quest_index": len(quests),
                "header_row": row_index,
                "quest_id": quest_id,
                "fields": [],
            }
            quests.append(current)
        if current is None:
            continue
        for field_index, value in enumerate(row):
            if not value or not JP_RE.search(value):
                continue
            budget_bytes, encodable = budget(value)
            try:
                source_sjis_bytes = len(value.encode("shift_jis"))
                source_sjis_encodable = True
            except UnicodeEncodeError:
                source_sjis_bytes = len(value.encode("shift_jis", errors="replace"))
                source_sjis_encodable = False
            current["fields"].append(
                {
                    "row": row_index,
                    "field": field_index,
                    "source": value,
                    "source_sjis_bytes": source_sjis_bytes,
                    "source_sjis_encodable": source_sjis_encodable,
                    "budget_cp949_bytes": budget_bytes,
                    "cp949_encodable": encodable,
                }
            )
        if "[QUESTEND]" in row:
            current = None

    return {
        "source": str(path),
        "num_fields": parsed["num_fields"],
        "num_records": parsed["num_records"],
        "quest_count": len(quests),
        "quests": quests,
    }


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: extract_quest_budget.py <quest.tbb> <output.json>")
    source = Path(sys.argv[1])
    output = Path(sys.argv[2])
    result = extract(source)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    field_count = sum(len(quest["fields"]) for quest in result["quests"])
    print(f"Extracted {result['quest_count']} quests and {field_count} Japanese text fields")


if __name__ == "__main__":
    main()
