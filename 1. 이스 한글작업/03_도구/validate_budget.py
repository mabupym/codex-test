#!/usr/bin/env python3
"""
Usage: python3 validate_budget.py <input_batch.json> <output_translated.json>

Validates that a translated batch JSON fits the CP949 byte budgets from the
corresponding input batch file (which has *_budget_bytes fields).
Prints per-item pass/fail and a summary. Exit code 0 if all pass.
"""
import json, sys

def main():
    in_path, out_path = sys.argv[1], sys.argv[2]
    inputs = {it["idx"]: it for it in json.load(open(in_path, encoding="utf-8"))}
    outputs = {it["idx"]: it for it in json.load(open(out_path, encoding="utf-8"))}

    missing = [idx for idx in inputs if idx not in outputs]
    if missing:
        print(f"MISSING {len(missing)} idx values in output: {missing[:10]}")

    fails = []
    for idx, inp in inputs.items():
        out = outputs.get(idx)
        if out is None:
            continue
        for key, budget_key in [("name_ko", "name_budget_bytes"),
                                 ("efx_ko", "efx_budget_bytes"),
                                 ("comment_ko", "comment_budget_bytes")]:
            budget = inp[budget_key]
            val = out.get(key, "")
            try:
                nbytes = len(val.encode("cp949"))
            except UnicodeEncodeError as e:
                fails.append((idx, key, "ENCODE_ERROR", str(e)))
                continue
            if nbytes > budget:
                fails.append((idx, key, f"OVER_BUDGET (used {nbytes}, budget {budget})", val))

    print(f"Checked {len(inputs)} items. Failures: {len(fails)}")
    for f in fails[:40]:
        print("  ", f)
    if fails:
        sys.exit(1)
    print("ALL WITHIN BUDGET")
    sys.exit(0)

if __name__ == "__main__":
    main()
