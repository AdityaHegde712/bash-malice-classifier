# %%
# Cell 1: Setup - Unzip dataset and create directories
import zipfile
import os

# Unzip dataset.zip
print("Unzipping dataset.zip...")
zipfile.ZipFile('dataset.zip').extractall('splits/')
print("Extracted files:", os.listdir('splits/'))

# Create models directory structure
os.makedirs('models/bert-tiny/checkpoints/best/', exist_ok=True)
os.makedirs('models/bert-tiny/evaluation/', exist_ok=True)
os.makedirs('models/distilbert/checkpoints/best/', exist_ok=True)
os.makedirs('models/distilbert/evaluation/', exist_ok=True)
print("Created directory structure")

# %%
# Cell 2: Install dependencies
!pip install torch transformers datasets optimum onnxruntime onnx scikit-learn numpy pandas matplotlib -q
print("Dependencies installed")

# %%
# Cell 3: Load and tokenize data
import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer

# Load JSONL files
def load_jsonl(filepath):
    with open(filepath, 'r') as f:
        return [json.loads(line) for line in f]

print("Loading datasets...")
train_data = load_jsonl('splits/train.jsonl')
val_data = load_jsonl('splits/val.jsonl')
test_data = load_jsonl('splits/test.jsonl')

print(f"Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")

# Initialize tokenizer
tokenizer = AutoTokenizer.from_pretrained('prajjwal1/bert-tiny')

# Create dataset class
class CommandDataset(Dataset):
    def __init__(self, data, tokenizer, max_len=64):
        self.data = data
        self.tokenizer = tokenizer
        self.max_len = max_len
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        text = item['command']
        label = item['label']
        
        encoding = self.tokenizer(
            text,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

# Create datasets and dataloaders
train_dataset = CommandDataset(train_data, tokenizer)
val_dataset = CommandDataset(val_data, tokenizer)
test_dataset = CommandDataset(test_data, tokenizer)

batch_size = 16
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size)
test_loader = DataLoader(test_dataset, batch_size=batch_size)

print("Data loaders created")

# %%
# Cell 4: Train BERT-tiny
from transformers import AutoModelForSequenceClassification, Trainer, TrainingArguments, EarlyStoppingCallback
from sklearn.utils.class_weight import compute_class_weight
import numpy as np
import torch

# Compute class weights
all_labels = np.array([item['label'] for item in train_data])
class_weights = compute_class_weight('balanced', classes=np.unique(all_labels), y=all_labels)
class_weights_dict = {i: weight for i, weight in enumerate(class_weights)}
print(f"Class weights: {class_weights_dict}")

# Load model
model = AutoModelForSequenceClassification.from_pretrained(
    'prajjwal1/bert-tiny',
    num_labels=2
)

# Training arguments
training_args = TrainingArguments(
    output_dir='models/bert-tiny/checkpoints/best/',
    num_train_epochs=10,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    learning_rate=2e-5,
    weight_decay=0.01,
    evaluation_strategy='epoch',
    save_strategy='epoch',
    load_best_model_at_end=True,
    metric_for_best_model='eval_loss',
    greater_is_better=False,
    warmup_steps=100,
    logging_steps=50,
    seed=42
)

# Custom trainer to track recall
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
    
    accuracy = accuracy_score(labels, predictions)
    precision = precision_score(labels, predictions, average='binary')
    recall = recall_score(labels, predictions, average='binary')
    f1 = f1_score(labels, predictions, average='binary')
    cm = confusion_matrix(labels, predictions)
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'confusion_matrix': cm.tolist()
    }

# Custom trainer to apply class weights
class WeightedTrainer(Trainer):
    def __init__(self, class_weights, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = torch.tensor(class_weights, dtype=torch.float32)
    
    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        loss_fct = torch.nn.CrossEntropyLoss(weight=self.class_weights)
        loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss

# Initialize trainer with class weights
trainer = WeightedTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
    class_weights=class_weights_dict,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
)

print("Starting BERT-tiny training...")
trainer.train()
print("BERT-tiny training completed")

# %%
# Cell 5: Evaluate BERT-tiny
import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# Load best model
model = AutoModelForSequenceClassification.from_pretrained('models/bert-tiny/checkpoints/best/')

# Evaluation
model.eval()
all_preds = []
all_labels = []

with torch.no_grad():
    for batch in test_loader:
        inputs = {
            'input_ids': batch['input_ids'],
            'attention_mask': batch['attention_mask']
        }
        labels = batch['labels']
        
        outputs = model(**inputs)
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=-1)
        
        all_preds.extend(predictions.numpy())
        all_labels.extend(labels.numpy())

# Calculate metrics
accuracy = accuracy_score(all_labels, all_preds)
precision = precision_score(all_labels, all_preds, average='binary')
recall = recall_score(all_labels, all_preds, average='binary')
f1 = f1_score(all_labels, all_preds, average='binary')
cm = confusion_matrix(all_labels, all_preds)

print(f"BERT-tiny Test Results:")
print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall (dangerous): {recall:.4f}")
print(f"F1: {f1:.4f}")
print(f"Confusion Matrix:\n{cm}")

# Save evaluation results
eval_results = {
    'accuracy': accuracy,
    'precision': precision,
    'recall': recall,
    'f1': f1,
    'confusion_matrix': cm.tolist(),
    'test_size': len(test_data)
}

with open('models/bert-tiny/evaluation/evaluation.json', 'w') as f:
    json.dump(eval_results, f, indent=2)

print("BERT-tiny evaluation saved")

# %%
# Cell 6: Conditional DistilBERT fallback (only if recall < 99.5%)
# This cell is pre-written but will only run if needed

# Check if recall is below threshold
recall_threshold = 0.995
if recall < recall_threshold:
    print(f"Recall ({recall:.4f}) < {recall_threshold}, running DistilBERT fallback...")
    
    # Load DistilBERT
    from transformers import AutoModelForSequenceClassification, Trainer, TrainingArguments, EarlyStoppingCallback
    from sklearn.utils.class_weight import compute_class_weight
    import numpy as np
    import torch
    
    # Compute class weights for DistilBERT
    class_weights = compute_class_weight('balanced', classes=np.unique(all_labels), y=all_labels)
    class_weights_dict = {i: weight for i, weight in enumerate(class_weights)}
    print(f"DistilBERT class weights: {class_weights_dict}")
    
    # Load DistilBERT model
    model = AutoModelForSequenceClassification.from_pretrained(
        'distilbert-base-uncased',
        num_labels=2
    )
    
    # Training arguments (same as BERT)
    training_args = TrainingArguments(
        output_dir='models/distilbert/checkpoints/best/',
        num_train_epochs=10,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        learning_rate=2e-5,
        weight_decay=0.01,
        evaluation_strategy='epoch',
        save_strategy='epoch',
        load_best_model_at_end=True,
        metric_for_best_model='eval_loss',
        greater_is_better=False,
        warmup_steps=100,
        logging_steps=50,
        seed=42
    )
    
    # Custom trainer to apply class weights
    class WeightedTrainer(Trainer):
        def __init__(self, class_weights, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.class_weights = torch.tensor(class_weights, dtype=torch.float32)
        
        def compute_loss(self, model, inputs, return_outputs=False):
            labels = inputs.pop("labels")
            outputs = model(**inputs)
            logits = outputs.logits
            loss_fct = torch.nn.CrossEntropyLoss(weight=self.class_weights)
            loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
            return (loss, outputs) if return_outputs else loss

    # Initialize trainer with class weights
    trainer = WeightedTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        class_weights=class_weights_dict,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
    )
    
    print("Starting DistilBERT training...")
    trainer.train()
    print("DistilBERT training completed")
    
    # Evaluate DistilBERT
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for batch in test_loader:
            inputs = {
                'input_ids': batch['input_ids'],
                'attention_mask': batch['attention_mask']
            }
            labels = batch['labels']
            
            outputs = model(**inputs)
            logits = outputs.logits
            predictions = torch.argmax(logits, dim=-1)
            
            all_preds.extend(predictions.numpy())
            all_labels.extend(labels.numpy())
    
    # Calculate metrics
    accuracy = accuracy_score(all_labels, all_preds)
    precision = precision_score(all_labels, all_preds, average='binary')
    recall = recall_score(all_labels, all_preds, average='binary')
    f1 = f1_score(all_labels, all_preds, average='binary')
    cm = confusion_matrix(all_labels, all_preds)
    
    print(f"DistilBERT Test Results:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall (dangerous): {recall:.4f}")
    print(f"F1: {f1:.4f}")
    print(f"Confusion Matrix:\n{cm}")
    
    # Save evaluation results
    eval_results = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'confusion_matrix': cm.tolist(),
        'test_size': len(test_data)
    }
    
    with open('models/distilbert/evaluation/evaluation.json', 'w') as f:
        json.dump(eval_results, f, indent=2)
    
    print("DistilBERT evaluation saved")
else:
    print(f"Recall ({recall:.4f}) >= {recall_threshold}, skipping DistilBERT fallback")

# %%
# Cell 7: ONNX export
from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer

# Determine which model to export
if recall >= recall_threshold:
    model_name = 'bert-tiny'
    checkpoint_path = 'models/bert-tiny/checkpoints/best/'
else:
    model_name = 'distilbert'
    checkpoint_path = 'models/distilbert/checkpoints/best/'

print(f"Exporting {model_name} to ONNX...")

# Export to ONNX
ort_model = ORTModelForSequenceClassification.from_pretrained(
    checkpoint_path,
    export=True
)

# Save model and tokenizer
ort_model.save_pretrained(f'models/{model_name}/onnx/')
tokenizer.save_pretrained(f'models/{model_name}/onnx/')

print(f"ONNX model saved to models/{model_name}/onnx/")

# %%
# Cell 8: INT8 quantization
from onnxruntime.quantization import quantize_dynamic, QuantType

# Determine which model to quantize
if recall >= recall_threshold:
    model_name = 'bert-tiny'
else:
    model_name = 'distilbert'

input_path = f'models/{model_name}/onnx/model.onnx'
output_path = f'models/{model_name}/onnx_quantized/model.onnx'

print(f"Quantizing {model_name} to INT8...")

# Quantize
quantize_dynamic(
    input_path,
    output_path,
    weight_type=QuantType.QInt8
)

# Calculate size reduction
original_size = os.path.getsize(input_path)
quantized_size = os.path.getsize(output_path)
size_reduction = (1 - quantized_size / original_size) * 100

print(f"Original size: {original_size / (1024*1024):.2f} MB")
print(f"Quantized size: {quantized_size / (1024*1024):.2f} MB")
print(f"Size reduction: {size_reduction:.2f}%")

# %%
# Cell 9: Verify ONNX vs PyTorch logits
import onnxruntime as ort
import numpy as np

# Determine which model to verify
if recall >= recall_threshold:
    model_name = 'bert-tiny'
    checkpoint_path = 'models/bert-tiny/checkpoints/best/'
else:
    model_name = 'distilbert'
    checkpoint_path = 'models/distilbert/checkpoints/best/'

# Load PyTorch model
from transformers import AutoModelForSequenceClassification
pytorch_model = AutoModelForSequenceClassification.from_pretrained(checkpoint_path)
pytorch_model.eval()

# Load ONNX model
ort_session = ort.InferenceSession(f'models/{model_name}/onnx_quantized/model.onnx')

# Get tokenizer
tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)

# Test on 100 samples
print("Verifying ONNX vs PyTorch logits...")

# Take first 100 test samples
test_samples = test_data[:100]

max_diff = 0
accuracy_drop = 0

for i, sample in enumerate(test_samples):
    text = sample['command']
    label = sample['label']
    
    # PyTorch inference
    encoding = tokenizer(
        text,
        max_length=64,
        padding='max_length',
        truncation=True,
        return_tensors='pt'
    )
    
    with torch.no_grad():
        pt_outputs = pytorch_model(**encoding)
        pt_logits = pt_outputs.logits.numpy().flatten()
    
    # ONNX inference
    ort_inputs = {
        'input_ids': encoding['input_ids'].numpy(),
        'attention_mask': encoding['attention_mask'].numpy()
    }
    ort_outputs = ort_session.run(None, ort_inputs)
    onnx_logits = ort_outputs[0].flatten()
    
    # Compare logits
    diff = np.abs(pt_logits - onnx_logits).max()
    max_diff = max(max_diff, diff)
    
    # Compare predictions
    pt_pred = np.argmax(pt_logits)
    onnx_pred = np.argmax(onnx_logits)
    if pt_pred != onnx_pred:
        accuracy_drop += 1
    
    if i % 20 == 0:
        print(f"Sample {i}: max diff = {diff:.6f}")

print(f"Max logit difference: {max_diff:.6f}")
print(f"Accuracy drop: {accuracy_drop}/100 ({accuracy_drop}%) samples")

# Save verification results
verification_results = {
    'max_logit_difference': max_diff,
    'accuracy_drop_count': accuracy_drop,
    'accuracy_drop_percentage': accuracy_drop / 100 * 100,
    'samples_tested': 100,
    'tolerance_met': max_diff < 0.001
}

with open(f'models/{model_name}/onnx_quantized/verification.json', 'w') as f:
    json.dump(verification_results, f, indent=2)

print("Verification results saved")

# %%
# Cell 10: Latency benchmark
import time
import numpy as np

# Determine which model to benchmark
if recall >= recall_threshold:
    model_name = 'bert-tiny'
    checkpoint_path = 'models/bert-tiny/checkpoints/best/'
else:
    model_name = 'distilbert'
    checkpoint_path = 'models/distilbert/checkpoints/best/'

# Load ONNX model
ort_session = ort.InferenceSession(f'models/{model_name}/onnx_quantized/model.onnx')

# Get tokenizer
tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)

# Take first 1000 test samples for benchmarking
benchmark_samples = test_data[:1000]

print("Running latency benchmark (1000 inferences)...")

# Warm-up
for sample in benchmark_samples[:10]:
    encoding = tokenizer(
        sample['command'],
        max_length=64,
        padding='max_length',
        truncation=True,
        return_tensors='pt'
    )
    ort_inputs = {
        'input_ids': encoding['input_ids'].numpy(),
        'attention_mask': encoding['attention_mask'].numpy()
    }
    ort_session.run(None, ort_inputs)

# Benchmark
latencies = []
for sample in benchmark_samples:
    start_time = time.time()
    
    encoding = tokenizer(
        sample['command'],
        max_length=64,
        padding='max_length',
        truncation=True,
        return_tensors='pt'
    )
    
    ort_inputs = {
        'input_ids': encoding['input_ids'].numpy(),
        'attention_mask': encoding['attention_mask'].numpy()
    }
    ort_session.run(None, ort_inputs)
    
    end_time = time.time()
    latencies.append(end_time - start_time)

# Calculate percentiles
latencies = np.array(latencies) * 1000  # Convert to milliseconds
p50 = np.percentile(latencies, 50)
p95 = np.percentile(latencies, 95)
p99 = np.percentile(latencies, 99)
mean_latency = np.mean(latencies)
std_latency = np.std(latencies)

print(f"Latency Benchmark Results (1000 inferences):")
print(f"Mean: {mean_latency:.2f} ± {std_latency:.2f} ms")
print(f"P50: {p50:.2f} ms")
print(f"P95: {p95:.2f} ms")
print(f"P99: {p99:.2f} ms")

# Save benchmark results
benchmark_results = {
    'mean_latency_ms': mean_latency,
    'std_latency_ms': std_latency,
    'p50_ms': p50,
    'p95_ms': p95,
    'p99_ms': p99,
    'num_inferences': 1000,
    'model_name': model_name
}

with open(f'models/{model_name}/onnx_quantized/latency_benchmark.json', 'w') as f:
    json.dump(benchmark_results, f, indent=2)

print("Latency benchmark results saved")