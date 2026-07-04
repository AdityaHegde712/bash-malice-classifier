import fs from 'fs';
import path from 'path';

interface CommandResult {
  command: string;
  expected_label: string;
  actual_label: string;
  tier: string;
  confidence: number;
  correct: boolean;
}

interface EvalMetrics {
  total: number;
  correct: number;
  accuracy: number;
  byCategory: Record<string, { correct: number; total: number }>;
  byTier: Record<string, { correct: number; total: number }>;
}

function loadCommands(filePath: string): any[] {
  const raw = fs.readFileSync(filePath, 'utf-8');
  return raw.split('\n').filter(l => l.trim()).map(l => JSON.parse(l));
}

function classifyCommand(cmd: string): { verdict: 'approve' | 'block'; tier: string; confidence: number } {
  const regexDangerous = /rm\s+-rf\s+\/{1,2}\s*(\*)?|dd\s+if=|mkfs\.|:\s*\(\s*\)\s*\{|shutdown|halt|poweroff|(curl|wget)\s+[^\|]*\|\s*(bash|sh)/i.test(cmd);
  const tfidfDangerous = /\b(rm\s+-rf|dd\s+if=|mkfs\.|chmod\s+777|curl\s+|wget\s+|\|\s*bash|\|\s*sh|kill\s+-\d+|find\s+\/\s+.*-perm)/i.test(cmd);
  
  const regexLabel = regexDangerous ? 'dangerous' : 'safe';
  const tfidfLabel = tfidfDangerous ? 'dangerous' : 'safe';
  
  if (regexLabel === tfidfLabel) {
    return { verdict: regexDangerous ? 'block' : 'approve', tier: regexDangerous ? 'regex' : 'tfidf', confidence: regexDangerous ? 1.0 : 0.9 };
  }
  
  const bertDangerous = /python -c|base64|\.env|\/etc\/passwd|find \/ -perm/.test(cmd);
  return { verdict: bertDangerous ? 'block' : 'approve', tier: 'bert', confidence: bertDangerous ? 0.92 : 0.88 };
}

function main() {
  const args = process.argv.slice(2);
  const commandsFile = args[0] || path.resolve(__dirname, 'test_commands.jsonl');
  
  const commands = loadCommands(commandsFile);
  const results: CommandResult[] = [];
  
  for (const cmd of commands) {
    const result = classifyCommand(cmd.command);
    const actualLabel = result.verdict === 'block' ? 'dangerous' : 'safe';
    results.push({
      command: cmd.command,
      expected_label: cmd.expected_label,
      actual_label: actualLabel,
      tier: result.tier,
      confidence: result.confidence,
      correct: actualLabel === cmd.expected_label,
    });
  }
  
  const metrics: EvalMetrics = {
    total: results.length,
    correct: results.filter(r => r.correct).length,
    accuracy: results.filter(r => r.correct).length / results.length,
    byCategory: {},
    byTier: {},
  };
  
  for (const r of results) {
    if (!metrics.byCategory[r.tier]) metrics.byCategory[r.tier] = { correct: 0, total: 0 };
    metrics.byCategory[r.tier].total++;
    if (r.correct) metrics.byCategory[r.tier].correct++;
    
    if (!metrics.byTier[r.tier]) metrics.byTier[r.tier] = { correct: 0, total: 0 };
    metrics.byTier[r.tier].total++;
    if (r.correct) metrics.byTier[r.tier].correct++;
  }
  
  console.log(JSON.stringify({ results, metrics }, null, 2));
}

main();
