#!/usr/bin/env python3
"""Apply a row/field translation batch to a Switch quest.tbb file."""
import json
import sys
from pathlib import Path

from tbb_parser import parse_tbb, rebuild_tbb


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: rebuild_quest_translation.py <source.tbb> <translations.json> <output.tbb>")
    source_path, translation_path, output_path = map(Path, sys.argv[1:])
    parsed = parse_tbb(source_path)
    translations = json.loads(translation_path.read_text(encoding="utf-8"))
    changes = translations["translations"]

    for change in changes:
        row = int(change["row"])
        field = int(change["field"])
        value = change["translated"]
        if row < 0 or row >= len(parsed["records"]):
            raise ValueError(f"row out of range: {row}")
        if field < 0 or field >= parsed["num_fields"]:
            raise ValueError(f"field out of range: {field}")
        encoded = value.encode("cp949")
        budget = int(change["budget_cp949_bytes"])
        if len(encoded) > budget:
            raise ValueError(f"over budget at row {row}, field {field}: {len(encoded)} > {budget}")
        parsed["records"][row][field] = encoded + b" " * (budget - len(encoded))

    result = rebuild_tbb(parsed)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(result)
    if parse_tbb(output_path)["num_records"] != parsed["num_records"]:
        raise ValueError("round-trip record count mismatch")
    print(f"Applied {len(changes)} translations to {output_path}")


if __name__ == "__main__":
    main()
