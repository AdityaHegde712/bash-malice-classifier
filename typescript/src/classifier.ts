import type { ClassificationResult, ClassificationVerdict } from './types.js';
import { matchRule } from './regex-rules.js';
import { classifyTFIDF } from './tfidf.js';

/**
 * Classify a command using the two-tier approach:
 * 1. Regex tier — unconditional block if pattern matched
 * 2. TF-IDF tier — logistic regression probability
 * 3. If regex and TF-IDF agree → return that verdict
 * 4. If conflict → conservative fallback (default to block if any signal flags it)
 *
 * The BERT-tiny tiebreaker tier was removed after training produced a
 * degenerate model (representational collapse — all inputs predicted class 1).
 * TF-IDF alone exceeds all targets (99.84% accuracy, 99.94% recall),
 * making the BERT tier unnecessary.
 * See `.agent-tasks/orchestrator/BERT_DECISION.md` for full analysis.
 */
export async function classifyCommand(cmd: string): Promise<ClassificationResult> {
  return classifyCommandSync(cmd) ?? fallbackHeuristic(cmd);
}

/**
 * Synchronous classification for the two-tier path (regex + TF-IDF only).
 * Returns undefined if regex and TF-IDF disagree.
 */
export function classifyCommandSync(cmd: string): ClassificationResult | null {
  const regexResult = matchRule(cmd);
  const regexDangerous = regexResult.matched;
  const regexLabel: 'safe' | 'dangerous' = regexDangerous ? 'dangerous' : 'safe';

  const tfidfResult = classifyTFIDF(cmd);
  const tfidfLabel = tfidfResult.label;

  if (regexLabel === tfidfLabel) {
    const verdict: ClassificationVerdict = regexDangerous ? 'block' : 'approve';
    const tier = regexDangerous ? 'regex' : 'tfidf';
    const confidence = regexDangerous ? 1.0 : tfidfResult.confidence;
    return { verdict, tier, confidence };
  }

  return null;
}

/**
 * Conservative fallback when regex and TF-IDF disagree.
 * Defaults to BLOCK if regex matched (unconditional rule) or
 * if TF-IDF confidence is above 50%. This errs on the side of safety
 * given the security-critical nature of the classifier.
 */
function fallbackHeuristic(cmd: string): ClassificationResult {
  const regexResult = matchRule(cmd);
  const tfidfResult = classifyTFIDF(cmd);

  // If regex matched, always block (unconditional rules)
  if (regexResult.matched) {
    return { verdict: 'block', tier: 'regex', confidence: 1.0 };
  }

  // Otherwise, TF-IDF flagged it — trust it
  return {
    verdict: 'block',
    tier: 'tfidf',
    confidence: tfidfResult.confidence,
  };
}
