# Colab Runbook for BERT-tiny Training

## Prerequisites
- Google account with web browser access
- Access to the project files

## Step 1: Download dataset.zip
1. Navigate to the project root directory
2. Locate `data/dataset.zip` (generated in Phase 3)
3. Download the zip file to your local machine

## Step 2: Open Google Colab
1. Go to [Google Colab](https://colab.research.google.com/)
2. Create a new notebook

## Step 3: Upload the notebook
1. Click "Upload" in the left sidebar
2. Select `training/bert_training_colab.py` (the jupytext percent-format notebook)
3. Wait for the notebook to load completely

## Step 4: Upload dataset.zip
1. In the notebook, click the folder icon in the left sidebar (Files)
2. Click "Upload" button
3. Select `dataset.zip` from your local machine
4. Wait for upload to complete

## Step 5: Configure runtime
1. Click "Runtime" in the top menu
2. Select "Change runtime type"
3. Choose **T4 GPU** (free tier)
4. Confirm the change (this may take a few minutes)

## Step 6: Run all cells
1. Click "Runtime" → "Run all" (or press Ctrl+Enter)
2. Monitor the progress - this will take approximately:
   - **BERT-tiny**: ~2 hours (if recall >= 99.5%)
   - **DistilBERT**: ~3 hours (if recall < 99.5%)
3. The notebook is designed to be idempotent - if interrupted, you can resume from Cell 4

## Step 7: Download artifacts
1. After all cells complete successfully:
   - Click the folder icon (Files) in the left sidebar
   - Look for the `models/` directory
   - Click the download icon (⬇) next to the `models/` folder
   - Save to your local machine

## Step 8: Place artifacts in local project
1. Unzip the downloaded folder
2. Move the contents to the local project root:
   - `models/bert-tiny/checkpoints/best_final/` (or `models/distilbert/checkpoints/best_final/`)
   - `models/bert-tiny/onnx_quantized/` (or `models/distilbert/`)
   - Ensure the directory structure is preserved

**Note:** The best model is saved to `best_final/` (not a symlink) to ensure portability across platforms

## Troubleshooting

### Colab disconnects during training
- Check if checkpoints were saved in `models/{model}/checkpoints/best/`
- Re-run from Cell 4 (training) to resume
- The notebook is designed to load existing checkpoints if available

### Runtime insufficient
- If you encounter runtime errors or slow performance:
  - Upgrade to Colab Pro for better GPU resources
  - Try running with DistilBERT (fallback) if BERT-tiny is too slow

### File upload issues
- Ensure `dataset.zip` is not corrupted
- Try uploading files one at a time
- Check file sizes - Colab has limits for free accounts

### ONNX export/quantization errors
- If Cells 7-10 fail, check that Cells 1-6 completed successfully
- Verify that the model checkpoint was saved properly
- Try running Cells 7-10 individually if needed

## Expected Output
After successful completion, you should see:
1. `models/{model}/checkpoints/best_final/` - Best model checkpoint (non-symlink)
2. `models/{model}/onnx_quantized/model.onnx` - Quantized ONNX model
3. `models/{model}/onnx_quantized/tokenizer.json` - Tokenizer configuration
4. `models/{model}/onnx_quantized/config.json` - Model configuration
5. `models/{model}/onnx_quantized/verification.json` - ONNX-PyTorch comparison results
6. `models/{model}/onnx_quantized/latency_benchmark.json` - Performance metrics
7. `models/{model}/evaluation/evaluation.json` - Model evaluation results

## Verification
After downloading artifacts:
1. Check that all expected files exist
2. Verify file sizes are reasonable (BERT-tiny < 30MB, DistilBERT < 70MB)
3. Run the verification script if provided in the project
4. Check that the model selection decision was documented in `models/model_selection.md`

## Notes
- The notebook uses BERT-tiny by default
- DistilBERT is only trained if BERT-tiny recall < 99.5%
- All models are quantized to INT8 for size reduction
- The notebook includes comprehensive logging and error handling
- Expected total runtime: 2-3 hours for BERT-tiny, 3-4 hours for DistilBERT