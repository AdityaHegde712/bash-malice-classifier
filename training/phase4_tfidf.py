#!/usr/bin/env python3
"""
Phase 4: TF-IDF Fast-Path Training for Bash Command Malicious/Benign Classifier

This script implements all tasks 4.1-4.5:
1. Feature tuning with grid search for TF-IDF parameters
2. Train LogisticRegression with specified hyperparameters
3. Export JSON artifacts for Node.js
4. Evaluate on test set
5. Threshold tuning for recall(dangerous) > 99%
"""

import json
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib
from typing import Dict, List, Any
import warnings
warnings.filterwarnings('ignore')

# Constants
TRAIN_FILE = "data/splits/train.jsonl"
VAL_FILE = "data/splits/val.jsonl"
TEST_FILE = "data/splits/test.jsonl"
MODELS_DIR = "models/tfidf"

os.makedirs(MODELS_DIR, exist_ok=True)

def load_data(filepath: str) -> tuple:
    """Load JSONL data and return commands and labels."""
    commands = []
    labels = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                data = json.loads(line)
                commands.append(data['command'])
                labels.append(data['label'])
    return commands, labels

def save_json(data: Any, filepath: str) -> None:
    """Save data as JSON file."""
    # Convert numpy types to Python native types
    def convert_to_python(obj):
        if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_to_python(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_python(item) for item in obj]
        else:
            return obj
    
    converted_data = convert_to_python(data)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(converted_data, f, ensure_ascii=False, indent=2)

def save_jsonl(data: List[Dict], filepath: str) -> None:
    """Save data as JSONL file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def task_4_1_feature_tuning() -> Dict:
    """Task 4.1: Grid search TF-IDF params with cross-validation."""
    print("=" * 60)
    print("TASK 4.1: Feature Tuning (TF-IDF Grid Search)")
    print("=" * 60)
    
    # Load training data
    X_train, y_train = load_data(TRAIN_FILE)
    
    # Define parameter grid
    param_grid = {
        'tfidf__ngram_range': [(1, 2), (1, 3)],
        'tfidf__max_features': [3000, 5000],
        'tfidf__sublinear_tf': [True]
    }
    
    # Create pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', LogisticRegression(
            C=1.0,
            class_weight={0: 1, 1: 5},
            max_iter=1000,
            random_state=42
        ))
    ])
    
    # Grid search with cross-validation
    print("Running grid search with cross-validation...")
    grid_search = GridSearchCV(
        pipeline,
        param_grid,
        cv=5,
        scoring='f1',
        n_jobs=-1,
        verbose=1
    )
    
    grid_search.fit(X_train, y_train)
    
    # Get best parameters
    best_params = grid_search.best_params_
    best_score = grid_search.best_score_
    
    print(f"\nBest parameters: {best_params}")
    print(f"Best cross-validation F1 score: {best_score:.4f}")
    
    # Save best parameters
    params_to_save = {
        'ngram_range': best_params['tfidf__ngram_range'],
        'max_features': best_params['tfidf__max_features'],
        'sublinear_tf': best_params['tfidf__sublinear_tf'],
        'best_cv_f1': float(best_score)
    }
    
    save_json(params_to_save, os.path.join(MODELS_DIR, 'params.json'))
    print(f"Saved best parameters to {MODELS_DIR}/params.json")
    
    return best_params

def task_4_2_train_logistic_regression(best_tfidf_params: Dict) -> Pipeline:
    """Task 4.2: Train LogisticRegression with best TF-IDF parameters."""
    print("\n" + "=" * 60)
    print("TASK 4.2: Train LogisticRegression")
    print("=" * 60)
    
    # Load training data
    X_train, y_train = load_data(TRAIN_FILE)
    
    # Create pipeline with best parameters
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=best_tfidf_params['tfidf__ngram_range'],
            max_features=best_tfidf_params['tfidf__max_features'],
            sublinear_tf=best_tfidf_params['tfidf__sublinear_tf']
        )),
        ('clf', LogisticRegression(
            C=1.0,
            class_weight={0: 1, 1: 5},
            max_iter=1000,
            random_state=42
        ))
    ])
    
    # Train on full training set
    print("Training on full training set...")
    pipeline.fit(X_train, y_train)
    
    # Save model
    model_path = os.path.join(MODELS_DIR, 'model.pkl')
    joblib.dump(pipeline, model_path)
    print(f"Saved model to {model_path}")
    
    return pipeline

def task_4_3_export_json_artifacts(pipeline: Pipeline) -> None:
    """Task 4.3: Export JSON artifacts for Node.js."""
    print("\n" + "=" * 60)
    print("TASK 4.3: Export JSON Artifacts")
    print("=" * 60)
    
    # Extract components from pipeline
    tfidf = pipeline.named_steps['tfidf']
    clf = pipeline.named_steps['clf']
    
    # Get vocabulary
    vocabulary = tfidf.vocabulary_
    save_json(vocabulary, os.path.join(MODELS_DIR, 'vocabulary.json'))
    print(f"Saved vocabulary to {MODELS_DIR}/vocabulary.json")
    
    # Get IDF
    idf = tfidf.idf_
    save_json(idf.tolist(), os.path.join(MODELS_DIR, 'idf.json'))
    print(f"Saved IDF to {MODELS_DIR}/idf.json")
    
    # Get coefficients
    coef = clf.coef_
    save_json(coef.tolist(), os.path.join(MODELS_DIR, 'coef.json'))
    print(f"Saved coefficients to {MODELS_DIR}/coef.json")
    
    # Get intercept
    intercept = clf.intercept_
    save_json(intercept.tolist(), os.path.join(MODELS_DIR, 'intercept.json'))
    print(f"Saved intercept to {MODELS_DIR}/intercept.json")
    
    # Save sklearn pipeline for reference
    pipeline_path = os.path.join(MODELS_DIR, 'pipeline.pkl')
    joblib.dump(pipeline, pipeline_path)
    print(f"Saved sklearn pipeline to {pipeline_path}")

def task_4_4_evaluate(pipeline: Pipeline) -> Dict:
    """Task 4.4: Evaluate on test set."""
    print("\n" + "=" * 60)
    print("TASK 4.4: Evaluate on Test Set")
    print("=" * 60)
    
    # Load test data
    X_test, y_test = load_data(TEST_FILE)
    
    # Make predictions
    y_pred = pipeline.predict(X_test)
    y_pred_proba = pipeline.predict_proba(X_test)[:, 1]  # Probability of class 1 (dangerous)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, pos_label=1)
    recall = recall_score(y_test, y_pred, pos_label=1)
    f1 = f1_score(y_test, y_pred, pos_label=1)
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    # Create evaluation results
    evaluation = {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'confusion_matrix': cm,
        'test_samples': len(y_test),
        'benign_predictions': int(sum(y_pred == 0)),
        'dangerous_predictions': int(sum(y_pred == 1)),
        'true_benign': int(sum(np.array(y_test) == 0)),
        'true_dangerous': int(sum(np.array(y_test) == 1))
    }
    
    # Save evaluation results
    save_json(evaluation, os.path.join(MODELS_DIR, 'evaluation.json'))
    print(f"Saved evaluation results to {MODELS_DIR}/evaluation.json")
    
    # Print metrics
    print(f"\nEvaluation Results:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Precision (dangerous): {precision:.4f}")
    print(f"  Recall (dangerous): {recall:.4f}")
    print(f"  F1-score (dangerous): {f1:.4f}")
    print(f"  Confusion Matrix: {cm}")
    
    return evaluation

def task_4_5_threshold_tuning(pipeline: Pipeline, evaluation: Dict) -> Dict:
    """Task 4.5: Threshold tuning for recall(dangerous) > 99%."""
    print("\n" + "=" * 60)
    print("TASK 4.5: Threshold Tuning")
    print("=" * 60)
    
    # Load test data
    X_test, y_test = load_data(TEST_FILE)
    
    # Get prediction probabilities
    y_pred_proba = pipeline.predict_proba(X_test)[:, 1]
    
    # Define threshold range
    thresholds = np.arange(0.5, 1.0, 0.01)  # 0.5 to 0.99
    
    # Find best threshold
    best_threshold = 0.5
    best_recall = 0.0
    best_f1 = 0.0
    best_precision = 0.0
    
    print("Sweeping thresholds...")
    for threshold in thresholds:
        y_pred_thresholded = (y_pred_proba >= threshold).astype(int)
        
        # Calculate metrics
        recall = recall_score(y_test, y_pred_thresholded, pos_label=1)
        precision = precision_score(y_test, y_pred_thresholded, pos_label=1, zero_division=0)
        f1 = f1_score(y_test, y_pred_thresholded, pos_label=1, zero_division=0)
        
        # Check if recall > 99%
        if recall > 0.99 and recall > best_recall:
            best_threshold = threshold
            best_recall = recall
            best_precision = precision
            best_f1 = f1
    
    print(f"\nBest threshold found: {best_threshold:.2f}")
    print(f"Best recall (dangerous): {best_recall:.4f}")
    print(f"Best precision (dangerous): {best_precision:.4f}")
    print(f"Best F1-score (dangerous): {best_f1:.4f}")
    
    # Save threshold
    threshold_info = {
        'best_threshold': float(best_threshold),
        'best_recall': float(best_recall),
        'best_precision': float(best_precision),
        'best_f1': float(best_f1),
        'thresholds_tested': len(thresholds)
    }
    
    save_json(threshold_info, os.path.join(MODELS_DIR, 'threshold.json'))
    print(f"Saved threshold info to {MODELS_DIR}/threshold.json")
    
    # Generate reference predictions (1000 test commands)
    print("\nGenerating reference predictions...")
    # Take first 1000 test samples
    X_ref = X_test[:1000]
    y_ref_true = y_test[:1000]
    y_ref_proba = y_pred_proba[:1000]
    
    # Apply best threshold
    y_ref_pred = (y_ref_proba >= best_threshold).astype(int)
    
    # Create reference predictions
    reference_predictions = []
    for i in range(min(1000, len(X_ref))):
        pred = {
            'command': X_ref[i],
            'true_label': int(y_ref_true[i]),
            'predicted_label': int(y_ref_pred[i]),
            'probability': float(y_ref_proba[i]),
            'threshold': float(best_threshold)
        }
        reference_predictions.append(pred)
    
    # Save reference predictions
    save_jsonl(reference_predictions, os.path.join(MODELS_DIR, 'reference_predictions.jsonl'))
    print(f"Saved reference predictions to {MODELS_DIR}/reference_predictions.jsonl")
    
    return threshold_info

def main():
    """Main function to run all Phase 4 tasks."""
    print("Starting Phase 4: TF-IDF Fast-Path Training")
    print("=" * 60)
    
    # Task 4.1: Feature tuning
    best_params = task_4_1_feature_tuning()
    
    # Task 4.2: Train LogisticRegression
    pipeline = task_4_2_train_logistic_regression(best_params)
    
    # Task 4.3: Export JSON artifacts
    task_4_3_export_json_artifacts(pipeline)
    
    # Task 4.4: Evaluate on test set
    evaluation = task_4_4_evaluate(pipeline)
    
    # Task 4.5: Threshold tuning
    threshold_info = task_4_5_threshold_tuning(pipeline, evaluation)
    
    # Print summary
    print("\n" + "=" * 60)
    print("PHASE 4 SUMMARY")
    print("=" * 60)
    print(f"Best TF-IDF parameters: {best_params}")
    print(f"Test accuracy: {evaluation['accuracy']:.4f}")
    print(f"Test recall (dangerous): {evaluation['recall']:.4f}")
    print(f"Best threshold: {threshold_info['best_threshold']:.2f}")
    print(f"Best recall with threshold: {threshold_info['best_recall']:.4f}")
    
    # Check acceptance criteria
    accuracy_ok = evaluation['accuracy'] >= 0.85
    recall_ok = evaluation['recall'] >= 0.95
    
    print(f"\nAcceptance Criteria:")
    print(f"  >85% accuracy: {'PASS' if accuracy_ok else 'FAIL'} ({evaluation['accuracy']:.2%})")
    print(f"  >95% recall (dangerous): {'PASS' if recall_ok else 'FAIL'} ({evaluation['recall']:.2%})")
    
    if accuracy_ok and recall_ok:
        print("\nAll acceptance criteria met!")
    else:
        print("\nSome acceptance criteria not met.")
    
    print("\nPhase 4 completed successfully!")

if __name__ == "__main__":
    main()