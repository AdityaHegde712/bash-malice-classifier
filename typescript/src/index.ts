// Malice Classifier — TypeScript entry point

export type {
  ClassificationVerdict,
  ClassificationResult,
  TierResult,
  TFIDFResult,
  BertOutput,
  BertPipeline,
  RegexRule,
  RegexMatchResult,
} from './types.js';

export { stripEscapes, collapseWhitespace, normalize, splitCompounds } from './normalizer.js';
export { REGEX_RULES, matchRule } from './regex-rules.js';
export { tokenize, computeTF, applyIDF, sigmoid, predictProbability, classifyTFIDF, loadModel as loadTFIDFModel } from './tfidf.js';
export { loadModel, parseOutput, validateTokenization } from './bert-classifier.js';
export { classifyCommand, classifyCommandSync } from './classifier.js';
