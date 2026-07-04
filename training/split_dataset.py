"""
Phase 3 Dataset Splitter
- Loads full dataset from data/processed/full_dataset.jsonl
- Loads golden commands from tests/test_commands.jsonl
- Excludes any command matching a golden command by exact text match
- Stratified 70/15/15 split by label
- Saves to data/splits/train.jsonl, val.jsonl, test.jsonl
- Adversarial set → data/splits/adversarial.jsonl
"""
import json
import os
import random

SEED = 42
random.seed(SEED)

FULL_DATASET = os.path.join("data", "processed", "full_dataset.jsonl")
GOLDEN_COMMANDS = os.path.join("tests", "test_commands.jsonl")
SPLITS_DIR = os.path.join("data", "splits")
TRAIN_FILE = os.path.join(SPLITS_DIR, "train.jsonl")
VAL_FILE = os.path.join(SPLITS_DIR, "val.jsonl")
TEST_FILE = os.path.join(SPLITS_DIR, "test.jsonl")
ADVERSARIAL_FILE = os.path.join(SPLITS_DIR, "adversarial.jsonl")

os.makedirs(SPLITS_DIR, exist_ok=True)


def load_jsonl(filepath):
    """Load a JSONL file, returning a list of dicts."""
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def save_jsonl(records, filepath):
    """Save a list of dicts as JSONL."""
    with open(filepath, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"  Saved {len(records)} records to {filepath}")


def main():
    print("=" * 60)
    print("DATASET SPLITTER (Phase 3)")
    print("=" * 60)
    
    # Load full dataset
    print("\n[1] Loading full dataset...")
    full_dataset = load_jsonl(FULL_DATASET)
    print(f"  Loaded {len(full_dataset)} records from {FULL_DATASET}")
    
    # Load golden commands
    print("\n[2] Loading golden commands...")
    golden_records = load_jsonl(GOLDEN_COMMANDS)
    golden_commands = set(rec["command"] for rec in golden_records)
    print(f"  Loaded {len(golden_commands)} golden commands from {GOLDEN_COMMANDS}")
    
    # Filter out golden commands from the dataset
    print("\n[3] Filtering out golden commands...")
    filtered = []
    excluded = []
    for rec in full_dataset:
        if rec["command"] in golden_commands:
            excluded.append(rec)
        else:
            filtered.append(rec)
    print(f"  Excluded {len(excluded)} commands matching golden set")
    print(f"  Remaining: {len(filtered)} commands")
    
    # Show which golden commands were found in the dataset
    found_golden = set(rec["command"] for rec in excluded)
    for cmd in golden_commands:
        status = "EXCLUDED" if cmd in found_golden else "NOT FOUND in dataset"
        print(f"    {status}: {cmd}")
    
    # Separate by label
    benign = [rec for rec in filtered if rec["label"] == 0]
    dangerous = [rec for rec in filtered if rec["label"] == 1]
    adversarial = [rec for rec in filtered if rec["source"] == "adversarial"]
    print(f"\n  Benign (label=0): {len(benign)}")
    print(f"  Dangerous (label=1): {len(dangerous)}")
    print(f"  Adversarial source: {len(adversarial)}")
    
    if len(benign) == 0 or len(dangerous) == 0:
        print("ERROR: One or both label groups are empty!")
        return
    
    # Stratified split: shuffle each group, then split 70/15/15
    print("\n[4] Performing stratified 70/15/15 split...")
    random.shuffle(benign)
    random.shuffle(dangerous)
    
    def split_group(group):
        n = len(group)
        train_end = int(n * 0.70)
        val_end = train_end + int(n * 0.15)
        train = group[:train_end]
        val = group[train_end:val_end]
        test = group[val_end:]
        return train, val, test
    
    b_train, b_val, b_test = split_group(benign)
    d_train, d_val, d_test = split_group(dangerous)
    
    print(f"  Benign: train={len(b_train)}, val={len(b_val)}, test={len(b_test)}")
    print(f"  Dangerous: train={len(d_train)}, val={len(d_val)}, test={len(d_test)}")
    
    # Merge stratified splits
    train = b_train + d_train
    val = b_val + d_val
    test = b_test + d_test
    
    random.shuffle(train)
    random.shuffle(val)
    random.shuffle(test)
    
    print(f"\n  Train: {len(train)} ({len(b_train)} benign + {len(d_train)} dangerous)")
    print(f"  Val:   {len(val)} ({len(b_val)} benign + {len(d_val)} dangerous)")
    print(f"  Test:  {len(test)} ({len(b_test)} benign + {len(d_test)} dangerous)")
    
    # Save splits
    print("\n[5] Saving splits...")
    save_jsonl(train, TRAIN_FILE)
    save_jsonl(val, VAL_FILE)
    save_jsonl(test, TEST_FILE)
    save_jsonl(adversarial, ADVERSARIAL_FILE)
    
    # Verify no golden commands leaked into splits
    print("\n[6] Verifying golden command exclusion...")
    for split_name, split_records in [("train", train), ("val", val), ("test", test), ("adversarial", adversarial)]:
        count = sum(1 for rec in split_records if rec["command"] in golden_commands)
        if count > 0:
            print(f"  ERROR: {count} golden commands found in {split_name}!")
        else:
            print(f"  OK: No golden commands in {split_name}")
    
    print("\nDone! Dataset split successfully.")


if __name__ == "__main__":
    main()
