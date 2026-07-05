export type ClassificationVerdict = 'approve' | 'block';

export type TierResult = {
  verdict: ClassificationVerdict;
  tier: 'regex' | 'tfidf' | 'bert';
  confidence: number;
};

export type ClassificationResult = TierResult;

export type TFIDFResult = {
  label: 'safe' | 'dangerous';
  confidence: number;
  probability: number;
};

export type BertOutput = {
  label: 'safe' | 'dangerous';
  confidence: number;
};

export type BertPipeline = (text: string) => Promise<{ label: string; score: number }[]>;

export type RegexRule = {
  pattern: RegExp;
  name: string;
  category: string;
  severity: string;
};

export type RegexMatchResult = {
  matched: boolean;
  rule: string | null;
};
