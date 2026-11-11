// Countersign's guardrail service, in the shape Otari's gateway expects
// (docs.otari.ai, "What a guardrails service answers"):
//   POST /validate {"profile": "...", "input_text": "...", "validate_kwargs": {...}}
//   -> {"profile": "...", "result": {"valid": false, "explanation": "...", "score": 1}}
// Otari calls this before it calls the model. With mode "block" and
// valid:false, Otari answers 403 guardrail_violation and the model never runs.
import { findAdvice } from "./_advice.js";

const PROFILE = "no-investment-advice";

export async function onRequestPost({ request }) {
  let body;
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: "body must be JSON" }, { status: 400 });
  }
  const profile = body && body.profile;
  if (profile !== PROFILE) {
    return Response.json({ error: `unknown profile: ${profile}` }, { status: 404 });
  }
  if (typeof body.input_text !== "string") {
    // No text means no verdict; Otari treats null as "could not evaluate".
    return Response.json({ profile, result: { valid: null, explanation: "no input_text", score: null } });
  }
  const hit = findAdvice(body.input_text);
  return Response.json({
    profile,
    result: hit
      ? { valid: false, explanation: `reads as advice: "${hit}"`, score: 1 }
      : { valid: true, explanation: null, score: 0 },
  });
}
