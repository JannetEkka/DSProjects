// Chithi's page: pick a language, photograph a letter (or pick a sample), read the checked points.

const T = {
  bn: {
    title: "সরকারি চিঠি বুঝুন, নিজের ভাষায়",
    lede: "বিদ্যুতের বিল, ব্যাংক বা করের নোটিশের ছবি তুলুন। চিঠিটি সহজ বাংলায় বুঝিয়ে দেওয়া হবে, আর প্রতিটি তারিখ ও টাকার অঙ্ক চিঠির সঙ্গে মিলিয়ে দেখা হবে।",
    take: "চিঠির ছবি তুলুন", or: "অথবা একটি নমুনা চিঠি বেছে নিন",
    checked: "চিঠির সঙ্গে মিলিয়ে দেখা হয়েছে", checkYourself: "এগুলো নিজে দেখে নিন",
    checkYourselfNote: "এই কথাগুলো চিঠির সঙ্গে মেলেনি, তাই সত্য হিসেবে দেখানো হচ্ছে না। চিঠিতে নিজে মিলিয়ে নিন।",
    askTitle: "চিঠি নিয়ে প্রশ্ন করুন (লিখে বা বলে)", ask: "জিজ্ঞাসা", how: "Chithi কীভাবে যাচাই করল",
    readText: "ছবি থেকে পড়া লেখা", again: "আরেকটি চিঠি", fromLetter: "চিঠিতে লেখা:",
    footer: "Chithi আইনি পরামর্শ দেয় না। সন্দেহ হলে চিঠি যিনি পাঠিয়েছেন তাঁর সঙ্গে যোগাযোগ করুন।",
    steps: ["ছবিতে চিঠি খোঁজা (SAM 3.1)", "গুরুত্বপূর্ণ অংশ খোঁজা (SAM 3.1)", "চিঠি পড়া (Muse Spark)", "আবার পড়া, কাছ থেকে", "বাংলায় বোঝানো", "প্রতিটি তারিখ ও অঙ্ক যাচাই"],
    noneVerified: "কোনো কথা যাচাই করা যায়নি।",
  },
  hi: {
    title: "सरकारी चिट्ठी समझिए, अपनी भाषा में",
    lede: "बिजली का बिल, बैंक या टैक्स नोटिस की फ़ोटो लीजिए। चिट्ठी आसान हिन्दी में समझाई जाएगी, और हर तारीख़ और रकम चिट्ठी से मिलाकर देखी जाएगी।",
    take: "चिट्ठी की फ़ोटो लें", or: "या एक नमूना चिट्ठी चुनें",
    checked: "चिट्ठी से मिलाकर जाँचा गया", checkYourself: "इन्हें ख़ुद जाँच लें",
    checkYourselfNote: "ये बातें चिट्ठी से मेल नहीं खाईं, इसलिए इन्हें सच की तरह नहीं दिखाया जा रहा। चिट्ठी में ख़ुद देख लें।",
    askTitle: "चिट्ठी के बारे में पूछें (लिखकर या बोलकर)", ask: "पूछें", how: "Chithi ने कैसे जाँचा",
    readText: "फ़ोटो से पढ़ा गया लेख", again: "दूसरी चिट्ठी", fromLetter: "चिट्ठी में लिखा है:",
    footer: "Chithi क़ानूनी सलाह नहीं देता। शक हो तो चिट्ठी भेजने वाले से संपर्क करें।",
    steps: ["फ़ोटो में चिट्ठी ढूँढना (SAM 3.1)", "ज़रूरी हिस्से ढूँढना (SAM 3.1)", "चिट्ठी पढ़ना (Muse Spark)", "दोबारा पढ़ना, पास से", "हिन्दी में समझाना", "हर तारीख़ और रकम की जाँच"],
    noneVerified: "कोई बात जाँची नहीं जा सकी।",
  },
  en: {
    title: "Understand an official letter, in your own language",
    lede: "Photograph an electricity bill, a bank or a tax notice. Chithi explains it in plain words, and checks every date and amount against the letter before you see it.",
    take: "Photograph a letter", or: "or pick a sample letter",
    checked: "Checked against the letter", checkYourself: "Check these yourself",
    checkYourselfNote: "These didn't match the letter, so they aren't shown as fact. Look them up in the letter yourself.",
    askTitle: "Ask about the letter (type or speak)", ask: "Ask", how: "How Chithi checked this",
    readText: "Text read from the photo", again: "Another letter", fromLetter: "The letter says:",
    footer: "Chithi doesn't give legal advice. If in doubt, contact whoever sent the letter.",
    steps: ["Finding the letter in the photo (SAM 3.1)", "Finding the parts that matter (SAM 3.1)", "Reading the letter (Muse Spark)", "Reading it again, up close", "Explaining it in English", "Checking every date and amount"],
    noneVerified: "Nothing could be verified.",
  },
};
const KIND = { electricity_bill: "Electricity bill", bank_notice: "Bank notice", tax_notice: "Tax notice", property_tax_notice: "Property tax (Hindi)" };

let lang = "bn";
let current = null; // the last result
const $ = (id) => document.getElementById(id);

function applyLang() {
  document.documentElement.lang = lang;
  document.body.className = lang;
  document.querySelectorAll("[data-t]").forEach((el) => { el.textContent = T[lang][el.dataset.t]; });
  document.querySelectorAll(".langs button").forEach((b) => b.classList.toggle("on", b.dataset.lang === lang));
  $("question").placeholder = { bn: "যেমন: না দিলে কী হবে?", hi: "जैसे: न भरूँ तो क्या होगा?", en: "e.g. What happens if I don't pay?" }[lang];
}

document.querySelectorAll(".langs button").forEach((b) => b.addEventListener("click", () => {
  lang = b.dataset.lang;
  try { localStorage.setItem("chithi-lang", lang); } catch (e) {}
  applyLang();
}));
try { lang = localStorage.getItem("chithi-lang") || "bn"; } catch (e) {}

function show(id) {
  for (const s of ["start", "working", "result"]) $(s).hidden = s !== id;
  window.scrollTo(0, 0);
}

let stepTimer = null;
function startSteps(photoUrl) {
  $("workingPhoto").src = photoUrl;
  const ol = $("steps");
  ol.innerHTML = T[lang].steps.map((s) => `<li>${s}</li>`).join("");
  let i = 0;
  const tick = () => {
    [...ol.children].forEach((li, j) => { li.className = j < i ? "done" : j === i ? "now" : ""; });
    if (i < ol.children.length - 1) i++;
  };
  tick();
  stepTimer = setInterval(tick, 2500);
  show("working");
}

async function explain(form, photoUrl) {
  form.append("language", lang);
  startSteps(photoUrl);
  try {
    const r = await fetch("/api/explain", { method: "POST", body: form });
    const data = await r.json();
    if (!r.ok) throw new Error(data.detail || r.statusText);
    current = data;
    render(data, photoUrl);
  } catch (e) {
    show("start");
    $("mode").hidden = false;
    $("mode").className = "error";
    $("mode").textContent = e.message;
  } finally {
    clearInterval(stepTimer);
  }
}

function esc(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

function card(p, cy) {
  const evidence = p.evidence || p.quote;
  const quote = esc(evidence).replace(/(₹\s?|Rs\.?\s?|INR\s?)?[\d০-৯०-९][\d০-৯०-९,./\-]*(\s?\/-)?/g, (m) => `<b>${m}</b>`);
  const why = cy && p.reasons_text?.length ? `<p class="why">${p.reasons_text.map(esc).join(" ")}</p>` : "";
  return `<div class="card ${cy ? "cy" : ""}"><p class="say">${esc(p.say)}</p>
    <p class="quote">${T[lang].fromLetter} “${quote}”</p>${why}</div>`;
}

function render(d, photoUrl) {
  $("resultPhoto").src = photoUrl;
  const [w, h] = d.image_size;
  const svg = $("overlay");
  svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
  svg.setAttribute("preserveAspectRatio", "none");
  const rect = (b, cls) => `<rect class="${cls}" x="${b[0]}" y="${b[1]}" width="${b[2] - b[0]}" height="${b[3] - b[1]}" rx="6"/>`;
  svg.innerHTML = (d.page_box ? rect(d.page_box, "page") : "") + d.regions.map((r) => rect(r.box, "region")).join("");

  $("kind").textContent = d.kind;
  $("summary").textContent = d.summary;
  $("verified").innerHTML = d.verified.length ? d.verified.map((p) => card(p, false)).join("") : `<p class="note">${T[lang].noneVerified}</p>`;
  $("cyWrap").hidden = !d.check_yourself.length;
  $("checkYourself").innerHTML = d.check_yourself.map((p) => card(p, true)).join("");
  $("trace").innerHTML = d.trace.map((s) =>
    `<li><b>${esc(s.step)}</b> <code>${esc(s.model)}</code> ${esc(s.detail)} <span class="ms">${(s.ms / 1000).toFixed(1)} s</span></li>`).join("");
  $("cost").textContent = d.backend === "mock"
    ? "Demo mode: sample letter, no model was called. The check is the real one."
    : `Model cost for this letter: $${d.cost_usd.toFixed(3)}`;
  $("letterText").textContent = d.letter_text;
  $("answers").innerHTML = "";
  $("askBox").hidden = d.backend === "mock";
  show("result");
}

$("photo").addEventListener("change", (e) => {
  const f = e.target.files[0];
  if (!f) return;
  const form = new FormData();
  form.append("photo", f);
  explain(form, URL.createObjectURL(f));
  e.target.value = "";
});

$("again").addEventListener("click", () => show("start"));

async function loadSamples() {
  const [health, samples] = await Promise.all([fetch("/api/health").then((r) => r.json()), fetch("/api/samples").then((r) => r.json())]);
  if (!health.live) {
    $("mode").hidden = false;
    $("mode").textContent = "Demo mode: Meta's models aren't connected yet, so only the sample letters work, with a stand-in explainer. The check is the real one.";
  }
  $("samples").innerHTML = samples.map((s) =>
    `<button class="sample" data-id="${esc(s.id)}" data-photo="${esc(s.photo)}"><img src="${esc(s.photo)}" alt="" loading="lazy"><span>${esc(KIND[s.kind] || s.kind)}</span></button>`).join("");
  document.querySelectorAll(".sample").forEach((b) => b.addEventListener("click", () => {
    const form = new FormData();
    form.append("sample_id", b.dataset.id);
    explain(form, b.dataset.photo);
  }));
}

// --- questions, typed or spoken ---------------------------------------------

async function ask(form) {
  form.append("language", lang);
  form.append("letter_text", current.letter_text);
  form.append("second_reading", current.second_reading || "");
  const box = document.createElement("div");
  box.innerHTML = `<p class="heard">…</p>`;
  $("answers").prepend(box);
  try {
    const r = await fetch("/api/ask", { method: "POST", body: form });
    const d = await r.json();
    if (!r.ok) throw new Error(d.detail || r.statusText);
    box.innerHTML = `<p class="heard">“${esc(d.question)}”</p>` + d.verified.map((p) => card(p, false)).join("") + d.check_yourself.map((p) => card(p, true)).join("");
  } catch (e) {
    box.innerHTML = `<p class="error">${esc(e.message)}</p>`;
  }
}

$("askBtn").addEventListener("click", () => {
  const q = $("question").value.trim();
  if (!q) return;
  const form = new FormData();
  form.append("question", q);
  $("question").value = "";
  ask(form);
});
$("question").addEventListener("keydown", (e) => { if (e.key === "Enter") $("askBtn").click(); });

// Muse Voice Transcribe wants 16 kHz mono 16-bit WAV, so record raw samples and encode them here.
let rec = null;
$("mic").addEventListener("click", async () => {
  if (rec) return stopRecording();
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const ctx = new AudioContext();
    const src = ctx.createMediaStreamSource(stream);
    const node = ctx.createScriptProcessor(4096, 1, 1);
    const chunks = [];
    node.onaudioprocess = (e) => chunks.push(new Float32Array(e.inputBuffer.getChannelData(0)));
    src.connect(node);
    node.connect(ctx.destination);
    rec = { stream, ctx, node, chunks };
    $("mic").classList.add("rec");
  } catch (e) {
    alert(e.message);
  }
});

function stopRecording() {
  const { stream, ctx, node, chunks } = rec;
  rec = null;
  $("mic").classList.remove("rec");
  node.disconnect();
  stream.getTracks().forEach((t) => t.stop());
  const rate = ctx.sampleRate;
  ctx.close();
  const all = new Float32Array(chunks.reduce((n, c) => n + c.length, 0));
  let o = 0;
  for (const c of chunks) { all.set(c, o); o += c.length; }
  const form = new FormData();
  form.append("audio", new Blob([wav16k(all, rate)], { type: "audio/wav" }), "question.wav");
  ask(form);
}

function wav16k(samples, rate) {
  const ratio = rate / 16000;
  const n = Math.floor(samples.length / ratio);
  const buf = new ArrayBuffer(44 + n * 2);
  const v = new DataView(buf);
  const str = (off, s) => [...s].forEach((c, i) => v.setUint8(off + i, c.charCodeAt(0)));
  str(0, "RIFF"); v.setUint32(4, 36 + n * 2, true); str(8, "WAVE"); str(12, "fmt ");
  v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
  v.setUint32(24, 16000, true); v.setUint32(28, 32000, true); v.setUint16(32, 2, true); v.setUint16(34, 16, true);
  str(36, "data"); v.setUint32(40, n * 2, true);
  for (let i = 0; i < n; i++) {
    // Average the source samples that fall into this output sample.
    const a = Math.floor(i * ratio), b = Math.min(samples.length, Math.floor((i + 1) * ratio));
    let s = 0;
    for (let j = a; j < b; j++) s += samples[j];
    s = Math.max(-1, Math.min(1, s / Math.max(1, b - a)));
    v.setInt16(44 + i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  return buf;
}

applyLang();
loadSamples();
