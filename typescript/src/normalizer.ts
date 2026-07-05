/**
 * Strip backslash escapes: "rm\ -rf\ /" → "rm -rf /"
 * Preserves quotes inside escapes.
 */
export function stripEscapes(cmd: string): string {
  return cmd.replace(/\\(.)/g, '$1');
}

/**
 * Collapse multiple whitespace characters into single space; trim.
 */
export function collapseWhitespace(cmd: string): string {
  return cmd.replace(/\s+/g, ' ').trim();
}

/**
 * Normalize a single command: escapes → whitespace → trim.
 */
export function normalize(cmd: string): string {
  return collapseWhitespace(stripEscapes(cmd));
}

/**
 * Split compound commands on ; && || operators.
 * Returns array of segments, each fully normalized.
 */
export function splitCompounds(cmd: string): string[] {
  if (!cmd || cmd.trim().length === 0) return [];
  // Split on ; , && , ||  (operators surrounded by optional whitespace)
  const segments = cmd.split(/\s*;\s*|\s+&&\s+|\s+\|\|\s+/);
  return segments
    .map(s => normalize(s))
    .filter(s => s.length > 0);
}
