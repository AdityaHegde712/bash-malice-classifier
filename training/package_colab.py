"""
Phase 3 Dataset Packager for Colab
- Zips train.jsonl, val.jsonl, test.jsonl into data/dataset.zip
- Includes README_SPLITS.txt
"""
import os
import zipfile

SPLITS_DIR = os.path.join("data", "splits")
OUTPUT_DIR = "data"
OUTPUT_ZIP = os.path.join(OUTPUT_DIR, "dataset.zip")
README_FILE = os.path.join(SPLITS_DIR, "README_SPLITS.txt")

FILES_TO_ZIP = [
    "train.jsonl",
    "val.jsonl",
    "test.jsonl",
    "adversarial.jsonl",
    "README_SPLITS.txt",
]

README_CONTENT = """\
Bash Command Malicious/Benign Classifier — Dataset Splits
=========================================================

Dataset Structure
-----------------
- train.jsonl:    Training set (70%% stratified split)
- val.jsonl:      Validation set (15%% stratifed split)
- test.jsonl:     Test set (15%% stratified split)
- adversarial.jsonl:  Additional adversarial/obfuscated variants

Fields
------
- command:          The shell command text
- label:            0 = safe/benign, 1 = dangerous/malicious
- severity:         Severity level (null for benign; low/medium/high/critical for dangerous)
- category:         Command category (filesystem, git, npm, pip, docker, sysadmin,
                    deceptive, destructive, exfiltration, privesc, persistence, recon, adversarial)
- source:           Data source (synthetic_benign, synthetic_dangerous, adversarial)
- obfuscation_type: Obfuscation method (none, base64, variable_substitution, comment_injection,
                    heredoc, chaining_safe_prefix, chaining_safe_suffix, wildcard_obfuscation,
                    escape_injection, reverse_string, quoted_arguments, echoed_command, dry_run)

Usage
-----
```python
import json

def load_jsonl(path):
    records = []
    with open(path) as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records

train = load_jsonl("train.jsonl")
val = load_jsonl("val.jsonl")
test = load_jsonl("test.jsonl")

X_train = [r["command"] for r in train]
y_train = [r["label"] for r in train]
```

Notes
-----
- Golden test commands (from tests/test_commands.jsonl) are excluded from all splits.
- Stratified split preserves label proportions across train/val/test.
- Generated for Phase 3 of the Malice Classifier project.
- Date: July 2026
"""


def main():
    print("=" * 60)
    print("DATASET PACKAGER FOR COLAB (Phase 3)")
    print("=" * 60)
    
    # Write README
    with open(README_FILE, "w") as f:
        f.write(README_CONTENT)
    print(f"\n  Written: {README_FILE}")
    
    # Verify all files exist
    missing = []
    for fname in FILES_TO_ZIP:
        fpath = os.path.join(SPLITS_DIR, fname)
        if not os.path.exists(fpath):
            missing.append(fname)
    
    if missing:
        print(f"\n  WARNING: Missing files: {missing}")
        print("  Continuing with available files...")
        files_to_zip = [f for f in FILES_TO_ZIP if f not in missing]
    else:
        files_to_zip = FILES_TO_ZIP
        print(f"\n  All {len(files_to_zip)} files present.")
    
    # Create zip
    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in files_to_zip:
            fpath = os.path.join(SPLITS_DIR, fname)
            if os.path.exists(fpath):
                zf.write(fpath, arcname=fname)
                print(f"  Added: {fname} ({os.path.getsize(fpath)} bytes)")
    
    # Verify zip
    with zipfile.ZipFile(OUTPUT_ZIP, "r") as zf:
        info = zf.infolist()
        total_size = sum(f.file_size for f in info)
        print(f"\n  Created: {OUTPUT_ZIP}")
        print(f"  Entries: {len(info)}")
        print(f"  Total size: {total_size} bytes ({total_size/1024:.1f} KB)")
        for f in info:
            print(f"    {f.filename}: {f.file_size} bytes")
    
    print("\nDone! Dataset ready for Colab upload.")


if __name__ == "__main__":
    main()
