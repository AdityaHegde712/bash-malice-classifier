"""
Local runner for bert_training_colab.py

Strips Colab-specific syntax (! commands), patches AutoTokenizer to use
use_fast=True (Windows compatibility, required for models like prajjwal1/bert-tiny
that lack a slow tokenizer), and fixes an indentation bug
in the original notebook.

Usage: python run_local.py
"""

import os
import sys
import tempfile
import subprocess
import re

# Set UTF-8 encoding for output to avoid cp1252 issues
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
NOTEBOOK_PATH = os.path.join(os.path.dirname(__file__), 'bert_training_colab.py')


def patch_notebook(content: str) -> str:
    """Apply all necessary patches to the Colab notebook content."""

    # --- Content-level replacements (before line loop) ---

    # Replace all Auto* classes for prajjwal1/bert-tiny (missing tokenizer_config.json
    # and model_type in config.json, which breaks Auto* resolution in transformers 5.x).
    # AutoTokenizer call is single-line, so str.replace works.
    content = content.replace(
        "AutoTokenizer.from_pretrained('prajjwal1/bert-tiny'",
        "BertTokenizer.from_pretrained('prajjwal1/bert-tiny'"
    )
    # AutoModelForSequenceClassification call spans multiple lines:
    #   AutoModelForSequenceClassification.from_pretrained(
    #       'prajjwal1/bert-tiny',
    # so use a regex to match across the newline + leading whitespace.
    # Capture group (\s*) preserves the original whitespace/indentation.
    content = re.sub(
        r"AutoModelForSequenceClassification\.from_pretrained\((\s*)'prajjwal1/bert-tiny'",
        r"BertForSequenceClassification.from_pretrained(\1'prajjwal1/bert-tiny'",
        content,
    )

    # Rename evaluation_strategy -> eval_strategy (transformers 5.x breaking change)
    content = content.replace('evaluation_strategy', 'eval_strategy')

    # Fix WeightedTrainer.__init__: torch.tensor() doesn't accept dicts directly.
    # class_weights is passed as {0: np.float64(...), 1: np.float64(...)}.
    # Convert dict values to a list before creating the tensor.
    content = content.replace(
        "self.class_weights = torch.tensor(class_weights, dtype=torch.float32)",
        "self.class_weights = torch.tensor(list(class_weights.values()), dtype=torch.float32)"
    )

    # Fix WeightedTrainer.compute_loss signature to accept **kwargs
    # (transformers 5.x Trainer.training_step passes num_items_in_batch)
    content = content.replace(
        "def compute_loss(self, model, inputs, return_outputs=False):",
        "def compute_loss(self, model, inputs, return_outputs=False, **kwargs):"
    )

    # Fix WeightedTrainer.compute_loss: move class_weights tensor to model device
    # to avoid "weight is on cpu, different from other tensors on cuda:0"
    content = content.replace(
        "loss_fct = torch.nn.CrossEntropyLoss(weight=self.class_weights)",
        "loss_fct = torch.nn.CrossEntropyLoss(weight=self.class_weights.to(model.device))"
    )

    lines = content.splitlines(keepends=True)
    out: list[str] = []

    for i, line in enumerate(lines):
        stripped = line.lstrip()

        # --- Remove Colab shell commands ---
        if stripped.startswith('!'):
            continue

        # --- Remove "Dependencies installed" (Cell 2) ---
        if 'print("Dependencies installed")' in line:
            continue

        # --- Fix relative paths: dataset.zip -> data/dataset.zip,
        #     splits/ -> data/splits/ (Cell 1, Cell 3) ---
        if "'dataset.zip'" in line:
            line = line.replace("'dataset.zip'", "'data/dataset.zip'")
        if '"dataset.zip"' in line:
            line = line.replace('"dataset.zip"', '"data/dataset.zip"')
        if "'splits/" in line:
            line = line.replace("'splits/", "'data/splits/")
        if '"splits/' in line:
            line = line.replace('"splits/', '"data/splits/')

        # --- Replace AutoTokenizer with BertTokenizer for prajjwal1/bert-tiny ---
        # The model on the Hub only has vocab.txt (no tokenizer_config.json),
        # so AutoTokenizer fails in transformers 5.x.
        if 'AutoTokenizer.from_pretrained(\'prajjwal1/bert-tiny\'' in line:
            line = line.replace(
                "AutoTokenizer.from_pretrained('prajjwal1/bert-tiny'",
                "BertTokenizer.from_pretrained('prajjwal1/bert-tiny'"
            )

        # --- Ensure BertTokenizer and BertForSequenceClassification are imported ---
        # Both are needed for prajjwal1/bert-tiny compatibility (no tokenizer_config.json
        # or model_type in config.json, breaking Auto* resolution in transformers 5.x).
        if 'from transformers import AutoTokenizer' in line:
            line = line.replace('AutoTokenizer', 'AutoTokenizer, BertTokenizer, BertForSequenceClassification')

        # --- Patch AutoTokenizer.from_pretrained -> use_fast=True ---
        # Must append use_fast=True AFTER the positional argument(s) since
        # Python requires keyword args after positional args.
        if 'AutoTokenizer.from_pretrained(' in line:
            line = re.sub(
                r'AutoTokenizer\.from_pretrained\(([^)]+)\)',
                r'AutoTokenizer.from_pretrained(\1, use_fast=True)',
                line,
            )

        # --- Fix indentation bug in Cell 4 (lines 170-189, 1-indexed) ---
        # The original file has an accidental 4-space indent on lines 170-189
        # (indices 169-188, 0-indexed).
        # Those lines should be at the top level.
        if 169 <= i <= 188:
            # Remove exactly 4 leading spaces (the accidental indent).
            # Lines inside the if/else block had 8 spaces → become 4 (correct).
            # Lines at the top level had 4 spaces → become 0 (correct).
            if line.startswith('    '):
                line = line[4:]

        # --- Patch checkpoint paths: best/ -> best_final/ ---
        if 'checkpoints/best/' in line:
            line = line.replace("'best/'", "'best_final/'")

        out.append(line)

    return ''.join(out)


def main():
    print("=" * 60)
    print("Malice Classifier – Local Training Runner")
    print("=" * 60)
    print(f"Project root : {PROJECT_ROOT}")
    print(f"Notebook     : {NOTEBOOK_PATH}")
    print(f"Python       : {sys.executable}")
    print(f"CUDA avail   : {_check_cuda()}")
    print()

    # --- 1. Read and patch ---
    print("[1/4] Reading and patching notebook…")
    with open(NOTEBOOK_PATH, 'r', encoding='utf-8') as f:
        original = f.read()

    patched = patch_notebook(original)

    # --- 2. Write to a temporary file ---
    print("[2/4] Writing patched script to temp file…")
    tmp = tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False,
        encoding='utf-8',
        dir=os.path.dirname(__file__),
    )
    try:
        tmp.write(patched)
        tmp_path = tmp.name
    finally:
        tmp.close()

    print(f"      → {tmp_path}")

    # --- 3. Execute ---
    print("[3/4] Starting training (this may take 1-2 hours)…")
    print()

    env = os.environ.copy()
    # Ensure the process runs from the project root (required for relative paths)
    env['PYTHONUNBUFFERED'] = '1'

    proc = subprocess.Popen(
        [sys.executable, tmp_path],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        text=True,
        bufsize=1,
    )

    # Stream output in real-time
    full_output: list[str] = []
    try:
        for line in proc.stdout:  # type: ignore[attr-defined]
            print(line, end='', flush=True)
            full_output.append(line)
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user. Terminating training…")
        proc.terminate()
        proc.wait(timeout=30)
        print("[!] Training terminated.")
        sys.exit(1)

    proc.wait()
    returncode = proc.returncode
    print()
    print(f"[4/4] Process finished with return code {returncode}")

    # --- 4. Cleanup temp file ---
    try:
        os.unlink(tmp_path)
    except OSError:
        pass

    # --- 5. Verify outputs ---
    print()
    print("=" * 60)
    if returncode == 0:
        print("✅ TRAINING SUCCEEDED")
        print("=" * 60)
        _verify_outputs()
    else:
        print("❌ TRAINING FAILED")
        print("=" * 60)
        # Print last 50 lines of output for debugging
        tail = full_output[-50:] if len(full_output) >= 50 else full_output
        print("\nLast output lines:")
        print("".join(tail))

    return returncode


def _check_cuda() -> str:
    try:
        import torch
        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            return f"YES ({name})"
        return "NO (using CPU)"
    except Exception:
        return "ERROR checking"


def _verify_outputs():
    """Check for expected output files after successful training."""
    checks = [
        ("BERT-tiny best checkpoint",
         os.path.join(PROJECT_ROOT, 'models', 'bert-tiny', 'checkpoints', 'best_final')),
        ("BERT-tiny evaluation",
         os.path.join(PROJECT_ROOT, 'models', 'bert-tiny', 'evaluation', 'evaluation.json')),
        ("BERT-tiny ONNX",
         os.path.join(PROJECT_ROOT, 'models', 'bert-tiny', 'onnx_quantized')),
    ]

    all_ok = True
    for label, path in checks:
        exists = os.path.exists(path)
        status = "✅" if exists else "❌ MISSING"
        print(f"  {status}  {label}: {path}")
        if not exists:
            all_ok = False

    # If evaluation.json exists, print metrics
    eval_path = os.path.join(PROJECT_ROOT, 'models', 'bert-tiny', 'evaluation', 'evaluation.json')
    if os.path.exists(eval_path):
        import json
        with open(eval_path, 'r') as f:
            metrics = json.load(f)
        print()
        print("  Final Metrics:")
        for key in ['accuracy', 'precision', 'recall', 'f1']:
            if key in metrics:
                print(f"    {key}: {metrics[key]:.4f}")
        if 'confusion_matrix' in metrics:
            print(f"    confusion_matrix: {metrics['confusion_matrix']}")

    print()
    if all_ok:
        print("  ✅ All expected outputs present.")
    else:
        print("  ⚠️  Some expected outputs are missing (may be expected if training was interrupted).")


if __name__ == '__main__':
    sys.exit(main())
