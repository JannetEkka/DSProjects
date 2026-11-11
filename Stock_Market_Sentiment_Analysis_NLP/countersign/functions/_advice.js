// The rule the guardrail applies: does this text tell the reader to buy,
// sell or hold? Reporting what an analyst did ("Jefferies upgraded Apple to
// buy") is news, not advice, and passes. Fixed patterns, no model.
const PATTERNS = [
  /\b(you|investors|readers|traders|shareholders|everyone|anyone)\s+(should|must|ought to|need to|would be wise to|are advised to)\s+(now\s+)?(buy|sell|hold|short|avoid|dump|accumulate|trim|exit|load up|add to|stay away)/i,
  /\b(we|i)\s+(strongly\s+)?(recommend|advise|suggest|urge)\b/i,
  /\b(our|my)\s+(recommendation|advice)\b/i,
  /\b(buy|sell|short|dump)\s+(now|today|immediately|the dip|before it|while you|this stock|the stock|apple (shares|stock)|aapl)\b/i,
  /\b(good|great|best|right|perfect)\s+time\s+to\s+(buy|sell|invest|get in|get out)\b/i,
  /\btime\s+to\s+(buy|sell|get in|get out|load up)\b/i,
  /(^|[.!?]\s+)(buy|sell|hold|short|accumulate)\s+(apple|aapl|the stock|shares|now)\b/i,
  /\bshould\s+(buy|sell|short|dump|accumulate)\b/i,
  /\bdon'?t\s+miss\s+(out|this)\b/i,
  /\bguaranteed\s+(return|profit|gain)s?\b/i,
];

export function findAdvice(text) {
  const t = String(text || "");
  for (const p of PATTERNS) {
    const m = t.match(p);
    if (m) return m[0].trim();
  }
  return null;
}
