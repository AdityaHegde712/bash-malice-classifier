import type { RegexRule, RegexMatchResult } from './types.js';

// ---- 14 Regex Rules matching common malicious patterns ----
export const REGEX_RULES: RegexRule[] = [
  // ---- Destructive filesystem ----
  { pattern: /rm\s+-rf\s+\/{1,2}\s*(\*)?/i, name: 'rm-rf-root', category: 'destructive', severity: 'critical' },
  { pattern: /dd\s+if=/, name: 'dd-destructive', category: 'destructive', severity: 'critical' },
  { pattern: /mkfs\.\w+\s+\/dev\//i, name: 'mkfs-format', category: 'destructive', severity: 'critical' },
  { pattern: /:\s*\(\s*\)\s*\{/i, name: 'fork-bomb', category: 'destructive', severity: 'critical' },
  { pattern: /\b(shutdown|halt|poweroff|reboot)\s*$/i, name: 'system-shutdown', category: 'destructive', severity: 'high' },
  { pattern: /\/etc\/rc\.local/i, name: 'rc-local-persistence', category: 'destructive', severity: 'critical' },
  { pattern: /\bmv\b.*\s+\/dev\/null/i, name: 'move-to-null', category: 'destructive', severity: 'critical' },

  // ---- Deceptive / dangerous patterns ----
  { pattern: /(curl|wget)\s+[^\|]*\|\s*(bash|sh)\b/i, name: 'curl-pipe-shell', category: 'deceptive', severity: 'critical' },
  { pattern: /chmod\s+(?:-R\s+)?777\s+/i, name: 'chmod-777', category: 'deceptive', severity: 'high' },
  { pattern: /\|\s*(bash|sh)\s*$/i, name: 'pipe-to-shell', category: 'deceptive', severity: 'high' },
  { pattern: /find\s+\/\s+.*-perm\s+-4000/i, name: 'suid-recon', category: 'deceptive', severity: 'medium' },
  { pattern: /kill\s+-\d+\s+\$\$/i, name: 'kill-self', category: 'deceptive', severity: 'high' },
  { pattern: /eval\s*\(/i, name: 'eval-usage', category: 'deceptive', severity: 'medium' },
  { pattern: /base64\s+-d/i, name: 'base64-decode', category: 'deceptive', severity: 'medium' },
];

/**
 * Test a command against all regex rules.
 * Normalizes whitespace before matching (same as locked test spec).
 */
export function matchRule(command: string): RegexMatchResult {
  // Normalize: replace literal \s with space, collapse whitespace, trim
  const normalized = command.replace(/\\s/g, ' ').replace(/\s+/g, ' ').trim();
  for (const rule of REGEX_RULES) {
    if (rule.pattern.test(normalized)) {
      return { matched: true, rule: rule.name };
    }
  }
  return { matched: false, rule: null };
}
