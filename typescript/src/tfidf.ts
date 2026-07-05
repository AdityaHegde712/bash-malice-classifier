import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';
import type { TFIDFResult } from './types.js';
import { normalize } from './normalizer.js';

// ---- Module-level state for loaded model ----
let _vocabulary: Record<string, number> | null = null;
let _idf: number[] | null = null;
let _coefficients: number[] | null = null;
let _intercept: number | null = null;
let _vocabSize: number = 0;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const MODELS_DIR = path.resolve(__dirname, '..', '..', 'models', 'tfidf');

/**
 * Load TF-IDF model data from JSON files.
 * Called automatically on first classify; can be called explicitly.
 */
export function loadModel(modelDir?: string): void {
  const dir = modelDir ?? MODELS_DIR;

  const vocabRaw = JSON.parse(fs.readFileSync(path.join(dir, 'vocabulary.json'), 'utf-8')) as Record<string, number>;
  const idfRaw = JSON.parse(fs.readFileSync(path.join(dir, 'idf.json'), 'utf-8')) as number[];
  const coefRaw = JSON.parse(fs.readFileSync(path.join(dir, 'coef.json'), 'utf-8')) as number[][];
  const interceptRaw = JSON.parse(fs.readFileSync(path.join(dir, 'intercept.json'), 'utf-8')) as number[];

  _vocabulary = vocabRaw;
  _idf = idfRaw;
  // coef.json is [[c0, c1, ...]] — nested array with one row
  _coefficients = coefRaw[0];
  // intercept.json is [value]
  _intercept = interceptRaw[0];
  _vocabSize = Object.keys(_vocabulary).length;
}

function ensureModelLoaded(): void {
  if (!_vocabulary || !_idf || !_coefficients || _intercept === null) {
    loadModel();
  }
}

/**
 * Tokenize text into unigrams + bigrams (matching ngram_range [1,2]).
 */
export function tokenize(text: string): string[] {
  const words = text.toLowerCase().split(/\s+/).filter(t => t.length > 0);
  const tokens: string[] = [];
  for (let i = 0; i < words.length; i++) {
    tokens.push(words[i]); // unigram
    if (i + 1 < words.length) {
      tokens.push(`${words[i]} ${words[i + 1]}`); // bigram
    }
  }
  return tokens;
}

/**
 * Compute term frequency with sublinear scaling (1 + log(count)).
 */
export function computeTF(tokens: string[]): number[] {
  ensureModelLoaded();
  const tf = new Array(_vocabSize).fill(0);
  if (tokens.length === 0) return tf;

  for (const token of tokens) {
    const idx = _vocabulary![token];
    if (idx !== undefined) {
      tf[idx] += 1;
    }
  }

  // Apply sublinear TF scaling: 1 + log(count)
  for (let i = 0; i < _vocabSize; i++) {
    if (tf[i] > 0) {
      tf[i] = 1 + Math.log(tf[i]);
    }
  }

  return tf;
}

/**
 * Multiply TF by IDF for each dimension.
 */
export function applyIDF(tf: number[]): number[] {
  ensureModelLoaded();
  return tf.map((val, i) => val * _idf![i]);
}

/**
 * Sigmoid function for logistic regression.
 */
export function sigmoid(z: number): number {
  return 1 / (1 + Math.exp(-z));
}

/**
 * Predict probability of being dangerous using logistic regression.
 */
export function predictProbability(tfidfVector: number[]): number {
  ensureModelLoaded();
  let dot = 0;
  for (let i = 0; i < _vocabSize; i++) {
    dot += tfidfVector[i] * _coefficients![i];
  }
  dot += _intercept!;
  return sigmoid(dot);
}

/**
 * Classify a command using TF-IDF + Logistic Regression.
 * Normalizes the command first, then computes TF → IDF → probability.
 */
export function classifyTFIDF(command: string): TFIDFResult {
  const normalized = normalize(command);
  const tokens = tokenize(normalized);
  const tf = computeTF(tokens);
  const tfidf = applyIDF(tf);
  const prob = predictProbability(tfidf);
  return {
    label: prob >= 0.5 ? 'dangerous' : 'safe',
    confidence: prob >= 0.5 ? prob : 1 - prob,
    probability: prob,
  };
}
