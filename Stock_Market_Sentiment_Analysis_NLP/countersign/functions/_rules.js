// The decision rule for the "Check a brief" app, the same idea as decide.py:
// the checker model describes, this code decides.
export const CHECKER = "alibaba/qwen3-235b-a22b-instruct-2507";
export const MAX_SENTENCES = 8, MAX_TEXT = 1600, MAX_SOURCES = 8000;

export function sentences(text) {
  // Split after . ! ? only when a space and a new sentence follow, so "9.9%" stays whole.
  return String(text).replace(/\s+/g, " ").trim().split(/(?<=[.!?])\s+(?=[A-Z0-9"'“$])/)
    .map(s => s.trim()).filter(s => s.length > 8);
}
const norm = s => String(s).toLowerCase().replace(/[^a-z0-9%$.]+/g, " ").trim();

// Every figure in the sentence must appear in the sources (commas ignored).
export function numbersNotInSources(sentence, sources) {
  const src = String(sources).replace(/,/g, "");
  const found = String(sentence).replace(/,/g, "").match(/\d+(?:\.\d+)?/g) || [];
  return found.filter(n => !new RegExp(`(^|[^\\d.])${n.replace(".", "\\.")}(?![\\d])`).test(src));
}
export function quoteInSources(quote, sources) {
  const src = norm(sources);
  const parts = String(quote).split(/\.{3,}|…/).map(p => norm(p).replace(/^[. ]+|[. ]+$/g, "")).filter(Boolean);
  if (!parts.length || Math.max(...parts.map(p => p.length)) < 12) return false;
  return parts.every(p => src.includes(p));
}
// A checker reply is used only if it is exactly this shape.
export function parseVerdict(text) {
  const m = String(text || "").match(/\{[\s\S]*\}/);
  if (!m) return null;
  let o; try { o = JSON.parse(m[0]); } catch { return null; }
  if (o.verdict !== "supported" && o.verdict !== "not_supported") return null;
  if (typeof (o.quote ?? "") !== "string" || typeof (o.reason ?? "") !== "string") return null;
  return { verdict: o.verdict, quote: (o.quote || "").trim(), reason: (o.reason || "").trim().slice(0, 300) };
}
export function decide(sentence, sources, verdict, adviceHit) {
  if (adviceHit) return { keep: false, reason: "guardrail", detail: `Blocked by the guardrail: reads as buy or sell advice ("${adviceHit}").` };
  const missing = numbersNotInSources(sentence, sources);
  if (missing.length) return { keep: false, reason: "number_not_in_sources", detail: `These figures are not in the sources: ${missing.join(", ")}.` };
  if (!verdict) return { keep: false, reason: "no_verdict", detail: "The checker gave no usable verdict, so nothing confirms it." };
  if (verdict.verdict !== "supported") return { keep: false, reason: "not_supported", detail: verdict.reason || "The sources do not support it." };
  if (!quoteInSources(verdict.quote, sources)) return { keep: false, reason: "quote_not_found", detail: "The checker's supporting quote is not in the sources." };
  return { keep: true, reason: null, detail: "" };
}
