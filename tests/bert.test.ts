import { describe, it, expect, vi } from 'vitest';

// ===== MOCK @huggingface/transformers pipeline =====
// The implementation in typescript/src/bert-classifier.ts must follow
// the same loading, tokenization, inference, and output parsing contract.

type BertOutput = { label: 'safe' | 'dangerous'; confidence: number };

interface BertPipeline {
  (text: string): Promise<{ label: string; score: number }[]>;
}

// ---- Mock pipeline factory ----
function createMockPipeline(overrides?: {
  label?: string;
  score?: number;
  throwOnModel?: boolean;
  throwOnInference?: boolean;
}): BertPipeline {
  const label = overrides?.label ?? 'SAFE';
  const score = overrides?.score ?? 0.98;

  return async (text: string) => {
    if (overrides?.throwOnInference) {
      throw new Error('Inference failed');
    }
    // Simulate some latency
    await new Promise(resolve => setTimeout(resolve, 1));
    return [{ label, score }];
  };
}

// ---- Mock model loader ----
async function loadModel(modelPath?: string): Promise<BertPipeline> {
  if (modelPath === 'invalid-path') {
    throw new Error('Model not found: invalid-path');
  }
  return createMockPipeline();
}

// ---- Output parser: raw pipeline output → BertOutput ----
function parseOutput(raw: { label: string; score: number }[]): BertOutput {
  if (!raw || raw.length === 0) {
    throw new Error('Empty model output');
  }
  const prediction = raw[0];
  const isDangerous = prediction.label.toUpperCase() === 'DANGEROUS' || prediction.label.toUpperCase() === 'MALICIOUS';
  return {
    label: isDangerous ? 'dangerous' : 'safe',
    confidence: prediction.score,
  };
}

// ---- Tokenization contract check ----
function validateTokenization(text: string): { input_ids: number[]; attention_mask: number[] } {
  // Simulates tokenizer output: for any text, produce a fixed-size ID sequence
  const tokens = text.split(/\s+/).filter(t => t.length > 0);
  const maxLength = 64;
  const ids: number[] = [101]; // [CLS]
  for (const token of tokens) {
    // Simple deterministic hash as mock token ID
    let hash = 0;
    for (let i = 0; i < token.length; i++) {
      hash = (hash * 31 + token.charCodeAt(i)) & 0xffff;
    }
    ids.push(hash % 30000 + 100); // OOV range
  }
  ids.push(102); // [SEP]

  // Pad or truncate to max_length
  while (ids.length < maxLength) ids.push(0);
  if (ids.length > maxLength) ids.length = maxLength;

  const attentionMask = ids.map(id => (id === 0 ? 0 : 1));
  return { input_ids: ids, attention_mask: attentionMask };
}

// ===== MODEL LOADING =====
describe('BERT — Model Loading', () => {
  it('loads model successfully with valid path', async () => {
    const pipeline = await loadModel();
    expect(pipeline).toBeDefined();
    expect(typeof pipeline).toBe('function');
  });

  it('throws on invalid model path', async () => {
    await expect(loadModel('invalid-path')).rejects.toThrow('Model not found');
  });

  it('loadModel returns async function that produces predictions', async () => {
    const pipeline = await loadModel();
    const result = await pipeline('ls -la');
    expect(Array.isArray(result)).toBe(true);
    expect(result.length).toBeGreaterThan(0);
    expect(result[0]).toHaveProperty('label');
    expect(result[0]).toHaveProperty('score');
  });
});

// ===== TOKENIZATION =====
describe('BERT — Tokenization (Mock)', () => {
  it('produces input_ids array of correct shape', () => {
    const result = validateTokenization('rm -rf /');
    expect(result.input_ids).toBeDefined();
    expect(result.attention_mask).toBeDefined();
    expect(result.input_ids.length).toBe(64); // max_length
    expect(result.attention_mask.length).toBe(64);
  });

  it('first token is [CLS] (101)', () => {
    const result = validateTokenization('hello');
    expect(result.input_ids[0]).toBe(101);
  });

  it('has [SEP] token (102) after content', () => {
    const result = validateTokenization('hello');
    // Find the last non-pad token position
    const nonZeroIndices = result.input_ids.map((id, i) => id !== 0 ? i : -1).filter(i => i >= 0);
    const lastContentIdx = Math.max(...nonZeroIndices);
    expect(result.input_ids[lastContentIdx]).toBe(102);
  });

  it('attention_mask is 1 for real tokens, 0 for padding', () => {
    const result = validateTokenization('test');
    const nonZeroCount = result.input_ids.filter(id => id !== 0).length;
    const onesCount = result.attention_mask.filter(m => m === 1).length;
    expect(onesCount).toBe(nonZeroCount);
  });

  it('empty text still produces [CLS][SEP] template', () => {
    const result = validateTokenization('');
    expect(result.input_ids[0]).toBe(101); // [CLS]
    expect(result.input_ids[1]).toBe(102); // [SEP]
  });
});

// ===== OUTPUT PARSING =====
describe('BERT — Output Parsing', () => {
  it('parses SAFE output correctly', () => {
    const result = parseOutput([{ label: 'SAFE', score: 0.95 }]);
    expect(result.label).toBe('safe');
    expect(result.confidence).toBeCloseTo(0.95, 5);
  });

  it('parses DANGEROUS output correctly', () => {
    const result = parseOutput([{ label: 'DANGEROUS', score: 0.99 }]);
    expect(result.label).toBe('dangerous');
    expect(result.confidence).toBeCloseTo(0.99, 5);
  });

  it('parses MALICIOUS as dangerous', () => {
    const result = parseOutput([{ label: 'MALICIOUS', score: 0.87 }]);
    expect(result.label).toBe('dangerous');
  });

  it('rejects empty output array', () => {
    expect(() => parseOutput([])).toThrow('Empty model output');
  });

  it('preserves confidence score from model', () => {
    const result = parseOutput([{ label: 'SAFE', score: 0.75 }]);
    expect(result.confidence).toBeCloseTo(0.75, 5);
  });

  it('handles case-insensitive labels', () => {
    expect(parseOutput([{ label: 'dangerous', score: 0.9 }]).label).toBe('dangerous');
    expect(parseOutput([{ label: 'safe', score: 0.9 }]).label).toBe('safe');
  });
});

// ===== ERROR HANDLING =====
describe('BERT — Error Handling', () => {
  it('throws when pipeline inference fails', async () => {
    const pipeline = createMockPipeline({ throwOnInference: true });
    await expect(pipeline('test')).rejects.toThrow('Inference failed');
  });

  it('handles undefined model output gracefully', () => {
    expect(() => parseOutput(undefined as unknown as [])).toThrow();
  });

  it('handles null model output gracefully', () => {
    expect(() => parseOutput(null as unknown as [])).toThrow();
  });
});

// ===== INTEGRATION (Mock) =====
describe('BERT — End-to-End Inference (Mock)', () => {
  it('classifies safe command as safe', async () => {
    const pipeline = createMockPipeline({ label: 'SAFE', score: 0.98 });
    const raw = await pipeline('ls -la');
    const result = parseOutput(raw);
    expect(result.label).toBe('safe');
    expect(result.confidence).toBeGreaterThan(0.9);
  });

  it('classifies dangerous command as dangerous', async () => {
    const pipeline = createMockPipeline({ label: 'DANGEROUS', score: 0.99 });
    const raw = await pipeline('rm -rf /');
    const result = parseOutput(raw);
    expect(result.label).toBe('dangerous');
    expect(result.confidence).toBeGreaterThan(0.9);
  });

  it('supports low confidence predictions', async () => {
    const pipeline = createMockPipeline({ label: 'SAFE', score: 0.55 });
    const raw = await pipeline('ambiguous command');
    const result = parseOutput(raw);
    expect(result.confidence).toBeCloseTo(0.55, 5);
  });
});
