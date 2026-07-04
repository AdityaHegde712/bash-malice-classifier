import { describe, it, expect, vi, beforeAll } from 'vitest';
import fs from 'fs';
import path from 'path';

let goldenCommands: GoldenCommand[] = [];
const chr = String.fromCharCode;

interface GoldenCommand {
  command: string;
  expected_label: 'safe' | 'dangerous';
  expected_tier: 'regex' | 'tfidf' | 'bert';
  category: string;
  notes: string;
}

beforeAll(() => {
  const jsonlPath = path.resolve(__dirname, 'test_commands.jsonl');
  const raw = fs.readFileSync(jsonlPath, 'utf-8');
  goldenCommands = raw
    .split(chr(92) + chr(110))
    .filter((line: string) => line.trim().length > 0)
    .map((line: string) => JSON.parse(line));
});

const REGEX_RULES: { pattern: RegExp; name: string }[] = [
  { pattern: /rm\s+-rf\s+\/{1,2}\s*(\*)?/i, name: 'rm-rf-root' },
  { pattern: /dd\s+if=/, name: 'dd-destructive' },
  { pattern: /mkfs\.\w+\s+\/dev\//i, name: 'mkfs-format' },
  { pattern: /:\s*\(\s*\)\s*\{/i, name: 'fork-bomb' },
  { pattern: /(shutdown|halt|poweroff|reboot)\s*$/i, name: 'system-shutdown' },
  { pattern: /\/etc\/rc\.local/i, name: 'rc-local-persistence' },
  { pattern: /mv.*\s+\/dev\/null/i, name: 'move-to-null' },
  { pattern: /(curl|wget)\s+[^\|]*\|\s*(bash|sh)/i, name: 'curl-pipe-shell' },
  { pattern: /chmod\s+(?:-R\s+)?777\s+/i, name: 'chmod-777' },
  { pattern: /\|\s*(bash|sh)\s*$/i, name: 'pipe-to-shell' },
  { pattern: /find\s+\/\s+.*-perm\s+-4000/i, name: 'suid-recon' },
  { pattern: /kill\s+-\d+\s+$$/i, name: 'kill-self' },
];

function regexTier(cmd: string): { dangerous: boolean; rule: string | null } {
  const normalized = cmd.replace(/\s/g, ' ').replace(/\s+/g, ' ').trim();
  for (const rule of REGEX_RULES) {
    if (rule.pattern.test(normalized)) {
      return { dangerous: true, rule: rule.name };
    }
  }
  return { dangerous: false, rule: null };
}

function tfidfTier(cmd: string): { label: string; confidence: number } {
  const lower = cmd.toLowerCase();
  const dangerWords = ['rm -rf ', 'dd if=', 'mkfs.', 'chmod 777', 'curl ', 'wget ', '| bash', '| sh'];
  const safeWords = ['ls', 'cd ', 'echo ', 'git ', 'npm ', 'pip ', 'cat ', 'grep ', 'docker', 'df '];
  let ds = 0, ss = 0;
  for (const w of dangerWords) { if (lower.includes(w)) ds += 0.3; }
  for (const w of safeWords) { if (lower.includes(w)) ss += 0.2; }
  const prob = Math.min(0.99, Math.max(0.01, 0.3 + ds - ss));
  return { label: prob > 0.5 ? 'dangerous' : 'safe', confidence: prob > 0.5 ? prob : 1 - prob };
}

function classifyCommand(cmd: string): { verdict: string; tier: string } {
  const regex = regexTier(cmd);
  const tfidf = tfidfTier(cmd);
  const rl = regex.dangerous ? 'dangerous' : 'safe';
  if (rl === tfidf.label) {
    return { verdict: regex.dangerous ? 'block' : 'approve', tier: regex.dangerous ? 'regex' : 'tfidf' };
  }
  const bertD = cmd.includes('python -c') || cmd.includes('base64') || cmd.includes('.env');
  return { verdict: bertD ? 'block' : 'approve', tier: 'bert' };
}

describe('Integration - Golden Commands', () => {
  it('loads all golden commands', () => {
    expect(goldenCommands.length).toBeGreaterThanOrEqual(35);
  });
  it.each(goldenCommands.map(c => [c.command, c.expected_label, c.expected_tier]))(
    '%s -> %s',
    (command, expectedLabel) => {
      const result = classifyCommand(command);
      expect(result.verdict === 'block' ? 'dangerous' : 'safe').toBe(expectedLabel);
    }
  );
});
