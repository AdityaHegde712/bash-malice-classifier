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
