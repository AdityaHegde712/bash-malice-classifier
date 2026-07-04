"""
Phase 3 Dataset Validator
- Checks: no duplicates across splits
- Label counts and percentages
- Golden exclusion: verify no golden command is in any split
- Sample 50 records for manual review
- Output data/reports/dataset_summary.txt
"""
import json
import os
import random

SEED = 42
random.seed(SEED)

SPLITS_DIR = os.path.join("data", "splits")
REPORTS_DIR = os.path.join("data", "reports")
GOLDEN_COMMANDS = os.path.join("tests", "test_commands.jsonl")
SUMMARY_FILE = os.path.join(REPORTS_DIR, "dataset_summary.txt")

SPLIT_FILES = {
    "train": os.path.join(SPLITS_DIR, "train.jsonl"),
    "val": os.path.join(SPLITS_DIR, "val.jsonl"),
    "test": os.path.join(SPLITS_DIR, "test.jsonl"),
    "adversarial": os.path.join(SPLITS_DIR, "adversarial.jsonl"),
}

os.makedirs(REPORTS_DIR, exist_ok=True)


def load_jsonl(filepath):
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def main():
    print("=" * 60)
    print("DATASET VALIDATOR (Phase 3)")
    print("=" * 60)

    summary_lines = []
    summary_lines.append("=" * 60)
    summary_lines.append("DATASET VALIDATION REPORT")
    summary_lines.append("=" * 60)
    summary_lines.append("")

    # Load golden commands
    golden_records = load_jsonl(GOLDEN_COMMANDS)
    golden_commands = set(rec["command"] for rec in golden_records)
    print(f"\nGolden commands loaded: {len(golden_commands)}")
    summary_lines.append(f"Golden commands: {len(golden_commands)}")
    summary_lines.append("")

    # Load all splits
    all_splits = {}
    total_all = 0
    for name, path in SPLIT_FILES.items():
        if os.path.exists(path):
            records = load_jsonl(path)
            all_splits[name] = records
            total_all += len(records)
            print(f"  {name}: {len(records)} records")
        else:
            all_splits[name] = []
            print(f"  {name}: FILE NOT FOUND")

    summary_lines.append("SPLIT SIZES")
    summary_lines.append("-" * 40)
    for name, records in all_splits.items():
        benign = sum(1 for r in records if r.get("label") == 0)
        dangerous = sum(1 for r in records if r.get("label") == 1)
        other = len(records) - benign - dangerous
        pct = benign / len(records) * 100 if len(records) > 0 else 0
        summary_lines.append(
            f"  {name:15s}: {len(records):6d} total  |  "
            f"safe={benign:6d} ({pct:5.1f}%)  |  dangerous={dangerous:6d}"
        )
        print(
            f"  {name:15s}: {len(records):6d} total  |  "
            f"safe={benign:6d} ({pct:5.1f}%)  |  dangerous={dangerous:6d}"
        )
    summary_lines.append("")
    summary_lines.append(f"  TOTAL       : {total_all:6d} records")
    summary_lines.append("")

    # Check for duplicates within each split
    print("\n[1] Checking for duplicates within splits...")
    summary_lines.append("DUPLICATE CHECKS")
    summary_lines.append("-" * 40)
    total_duplicates = 0
    for name, records in all_splits.items():
        seen = set()
        dups = 0
        for rec in records:
            cmd = rec.get("command", "")
            if cmd in seen:
                dups += 1
            seen.add(cmd)
        total_duplicates += dups
        if dups > 0:
            print(f"  WARNING: {name} has {dups} duplicate commands")
            summary_lines.append(f"  {name}: {dups} duplicates FOUND")
        else:
            print(f"  OK: {name}: No duplicates")
            summary_lines.append(f"  {name}: 0 duplicates (OK)")

    # Check for duplicates across splits
    print("\n[2] Checking for duplicates across splits...")
    summary_lines.append("")
    summary_lines.append("CROSS-SPLIT DUPLICATES")
    summary_lines.append("-" * 40)
    split_names = list(all_splits.keys())
    cross_dups = 0
    for i in range(len(split_names)):
        for j in range(i + 1, len(split_names)):
            name_a = split_names[i]
            name_b = split_names[j]
            set_a = set(rec.get("command", "") for rec in all_splits[name_a])
            set_b = set(rec.get("command", "") for rec in all_splits[name_b])
            overlap = set_a & set_b
            if overlap:
                cross_dups += len(overlap)
                print(
                    f"  WARNING: {name_a} <-> {name_b}: "
                    f"{len(overlap)} overlapping commands"
                )
                summary_lines.append(
                    f"  {name_a} <-> {name_b}: {len(overlap)} overlaps FOUND"
                )
            else:
                print(f"  OK: {name_a} <-> {name_b}: No overlap")
                summary_lines.append(
                    f"  {name_a} <-> {name_b}: 0 overlaps (OK)"
                )

    if cross_dups == 0 and total_duplicates == 0:
        print("  OK: No duplicates found anywhere!")
        summary_lines.append("  OVERALL: No duplicates found")

    # Check golden command exclusion
    print("\n[3] Checking golden command exclusion...")
    summary_lines.append("")
    summary_lines.append("GOLDEN COMMAND EXCLUSION")
    summary_lines.append("-" * 40)
    golden_found_total = 0
    for name, records in all_splits.items():
        found = []
        for rec in records:
            if rec.get("command", "") in golden_commands:
                found.append(rec.get("command", ""))
        if found:
            golden_found_total += len(found)
            print(f"  FAIL: {len(found)} golden commands found in {name}!")
            for cmd in found:
                print(f"    -> {cmd}")
            summary_lines.append(
                f"  {name}: {len(found)} golden commands LEAKED (FAIL)"
            )
        else:
            print(f"  OK: {name}: No golden commands")
            summary_lines.append(f"  {name}: 0 (PASS)")

    if golden_found_total == 0:
        print("  OK: All golden commands properly excluded!")
        summary_lines.append("  OVERALL: All golden commands excluded (PASS)")

    # Label balance
    print("\n[4] Label balance (excluding adversarial)...")
    summary_lines.append("")
    summary_lines.append("LABEL BALANCE (non-adversarial splits only)")
    summary_lines.append("-" * 40)

    total_benign = 0
    total_dangerous = 0
    for name in ["train", "val", "test"]:
        records = all_splits.get(name, [])
        b = sum(1 for r in records if r.get("label") == 0)
        d = sum(1 for r in records if r.get("label") == 1)
        total_benign += b
        total_dangerous += d

    grand_total = total_benign + total_dangerous
    if grand_total > 0:
        print(
            f"  Benign:    {total_benign:6d} "
            f"({total_benign / grand_total * 100:.1f}%)"
        )
        print(
            f"  Dangerous: {total_dangerous:6d} "
            f"({total_dangerous / grand_total * 100:.1f}%)"
        )
        print(
            f"  Ratio:     1:{total_dangerous / total_benign:.2f} "
            f"(dangerous:benign)"
        )
        summary_lines.append(
            f"  Benign:    {total_benign:6d} "
            f"({total_benign / grand_total * 100:.1f}%)"
        )
        summary_lines.append(
            f"  Dangerous: {total_dangerous:6d} "
            f"({total_dangerous / grand_total * 100:.1f}%)"
        )

    # Severity distribution
    print("\n[5] Severity distribution (dangerous commands only)...")
    summary_lines.append("")
    summary_lines.append("SEVERITY DISTRIBUTION (dangerous commands)")
    summary_lines.append("-" * 40)
    sev_counts = {}
    for name in ["train", "val", "test", "adversarial"]:
        for rec in all_splits.get(name, []):
            if rec.get("label") == 1:
                sev = rec.get("severity", "unspecified")
                sev_counts[sev] = sev_counts.get(sev, 0) + 1

    for sev in ["low", "medium", "high", "critical"]:
        count = sev_counts.get(sev, 0)
        total_d = sum(sev_counts.values())
        pct = count / total_d * 100 if total_d > 0 else 0
        print(f"  {sev:10s}: {count:6d} ({pct:5.1f}%)")
        summary_lines.append(f"  {sev:10s}: {count:6d} ({pct:5.1f}%)")
    summary_lines.append(
        f"  {'unspecified':10s}: {sev_counts.get('unspecified', 0)}"
    )

    # Sample 50 records for manual review
    print("\n[6] Sample 50 records for manual review:")
    summary_lines.append("")
    summary_lines.append("SAMPLE RECORDS (50 random for manual review)")
    summary_lines.append("-" * 40)

    all_records = []
    for name in ["train", "val", "test"]:
        all_records.extend(all_splits.get(name, []))

    sample = random.sample(all_records, min(50, len(all_records)))
    for i, rec in enumerate(sample, 1):
        cmd = rec.get("command", "") or "?"
        label = rec.get("label", "?")
        if label is None:
            label = "?"
        cat = rec.get("category", "?") or "?"
        sev = rec.get("severity") or "?"
        source = rec.get("source", "?") or "?"
        obf = rec.get("obfuscation_type", "?") or "?"
        line = (
            f"  {i:2d}. [{label}] [{cat:15s}] [{sev:10s}] "
            f"[{source:20s}] [{obf:15s}] {cmd[:80]}"
        )
        print(line)
        summary_lines.append(line)

    # Write summary file
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines) + "\n")

    print(f"\nSummary saved to {SUMMARY_FILE}")
    print("\nValidation complete!")


if __name__ == "__main__":
    main()
