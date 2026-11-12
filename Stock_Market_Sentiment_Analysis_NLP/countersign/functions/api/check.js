// POST /api/check {"text": "...", "sources": "..."}
// Checks each sentence of a model-written text against the sources, live,
// through the Otari gateway. The key is a Cloudflare secret (OTARI_API_KEY),
// capped in Otari's dashboard, so the cap is the most this endpoint can spend.
import { findAdvice } from "../_advice.js";
import { CHECKER, MAX_SENTENCES, MAX_TEXT, MAX_SOURCES, sentences, parseVerdict, decide } from "../_rules.js";

const OTARI = "https://api.otari.ai/api/v1/chat/completions";
const SYSTEM =
  "You are a strict fact checker. You get one claim and the source text. You did not write the claim.\n" +
  "Look for anything in the claim that the sources do not state: a wrong name, number, date, cause or direction, " +
  "or a detail that is simply not there. Outside knowledge does not count as support.\n" +
  'If every part of the claim is stated in the sources, the verdict is "supported"; otherwise "not_supported".\n' +
  "Reply with only this JSON:\n" +
  '{"verdict": "supported" or "not_supported", "quote": "for supported, a passage copied word for word from the sources", ' +
  '"reason": "for not_supported, what is missing or wrong, in one sentence"}';

const json = (o, status = 200) => Response.json(o, { status });

export async function onRequestPost({ request, env }) {
  if (!env.OTARI_API_KEY) return json({ error: "not_configured", message: "The live checker has no Otari key yet." }, 503);
  let body;
  try { body = await request.json(); } catch { return json({ error: "bad_request", message: "Send JSON." }, 400); }
  const text = typeof body.text === "string" ? body.text.trim() : "";
  const sources = typeof body.sources === "string" ? body.sources.trim() : "";
  if (!text || !sources) return json({ error: "bad_request", message: "Both the text and its sources are needed." }, 400);
  if (text.length > MAX_TEXT || sources.length > MAX_SOURCES)
    return json({ error: "too_long", message: `Limits: ${MAX_TEXT} characters of text, ${MAX_SOURCES} of sources.` }, 400);
  const list = sentences(text);
  if (!list.length) return json({ error: "bad_request", message: "No sentence found in the text." }, 400);
  if (list.length > MAX_SENTENCES) return json({ error: "too_long", message: `At most ${MAX_SENTENCES} sentences per check.` }, 400);

  const guardUrl = new URL(request.url).origin;
  let cost = 0, budgetStop = null, keyRejected = false;

  async function checkOne(sentence) {
    // The guardrail sees the sentence alone, through Otari, before the checker model runs.
    const ask = async (messages, guard) => {
      const r = await fetch(OTARI, {
        method: "POST",
        headers: { Authorization: `Bearer ${env.OTARI_API_KEY}`, "Content-Type": "application/json" },
        body: JSON.stringify({ model: CHECKER, messages, max_tokens: 300, temperature: 0,
          ...(guard ? { guardrails: [{ profile: "no-investment-advice", mode: "block", url: guardUrl }] } : {}) }),
      });
      const data = await r.json().catch(() => ({}));
      return { status: r.status, code: r.headers.get("Otari-Error-Code") || data.code || (data.detail && data.detail.code) || "",
               detail: data.detail, data, served: r.headers.get("Otari-Model"), provider: r.headers.get("Otari-Provider") };
    };
    const user = `Claim: ${sentence}\n\nSources:\n${sources}`;
    let adviceHit = null, verdict = null, served = null, rejected = 0;
    // 1. guardrail, on the sentence only (a tiny call; a block means the model never ran)
    const g = await ask([{ role: "system", content: "Reply with the single word ok." }, { role: "user", content: sentence }], true);
    if (g.status === 403 && g.code === "budget_exceeded") { budgetStop = String(g.detail); return { sentence, keep: null }; }
    if (g.status === 401) { keyRejected = true; return { sentence, keep: null }; }
    if (g.status === 403) adviceHit = findAdvice(sentence) || "advice";
    else if (g.status !== 200) return { sentence, ...decide(sentence, sources, null, null), note: `guardrail call failed (${g.status})` };
    else cost += Number(g.data.usage?.cost_usd || 0);
    // 2. checker, validated, retried once
    if (!adviceHit) {
      for (let attempt = 0; attempt < 2 && !verdict; attempt++) {
        const c = await ask([{ role: "system", content: SYSTEM }, { role: "user", content: user }], false);
        if (c.status === 403 && c.code === "budget_exceeded") { budgetStop = String(c.detail); return { sentence, keep: null }; }
        if (c.status !== 200) { rejected++; continue; }
        cost += Number(c.data.usage?.cost_usd || 0);
        served = `${c.served} via ${c.provider}`;
        verdict = parseVerdict(c.data.choices?.[0]?.message?.content);
        if (!verdict) rejected++;
      }
    }
    return { sentence, ...decide(sentence, sources, verdict, adviceHit), quote: verdict?.quote || "", served, replies_rejected: rejected };
  }

  const results = await Promise.all(list.map(checkOne));
  if (keyRejected)
    return json({ error: "key_rejected", message: "Otari rejected the stored key. Nothing was checked, so nothing is shown as confirmed." }, 502);
  if (budgetStop)
    return json({ error: "budget", message: "Otari refused the request: the key's spending cap is reached. Nothing was checked, so nothing is shown as confirmed.", detail: budgetStop }, 402);
  return json({
    checker: CHECKER, gateway: "api.otari.ai", cost_usd: Number(cost.toFixed(6)),
    written: results.length, removed: results.filter(r => !r.keep).length, results,
  });
}
