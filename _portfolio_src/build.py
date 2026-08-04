#!/usr/bin/env python3
"""Builds the animated portfolio index.html from data.py."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from data import FLAGSHIP, PROJECTS, CATS, CONTACT, CREDENTIALS, PROFILES

ICON = {
    "live": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>',
    "code": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 18 6-6-6-6"/><path d="m8 6-6 6 6 6"/></svg>',
    "doc":  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-4 0v-3h4"/><path d="M18 14h-8M15 18h-5M10 6h8v4h-8z"/></svg>',
}

def links_html(links, small=False):
    if not links:
        return ""
    cls = "lnk sm" if small else "lnk"
    out = []
    for label, url, kind in links:
        out.append(
            f'<a class="{cls} {kind}" href="{url}" target="_blank" rel="noopener noreferrer">'
            f'<span class="ico">{ICON[kind]}</span>{label}</a>'
        )
    return f'<div class="lnks">{"".join(out)}</div>'


GRANT_CHIP = ('<a class="grant-chip" href="#backing">'
              '<span class="gdot"></span>Seeking grants &amp; partners</a>')


def shots_html(shots):
    if not shots:
        return ""
    items = "".join(
        f'<a class="shot" href="{src}" data-cap="{cap}" target="_blank" rel="noopener noreferrer">'
        f'<img src="{src}" alt="{cap}" loading="lazy" onerror="this.closest(\'.shot\').remove()">'
        f'<span class="shot-cap">{cap}</span></a>'
        for src, cap in shots)
    return f'<div class="shots">{items}</div>'


def tags_html(tags):
    return '<div class="tags">' + "".join(f'<span class="tag">{t}</span>' for t in tags) + "</div>"


def flagship_html(f):
    stats = "".join(
        f'<div class="fstat"><span class="fnum" data-count="{n}">{n}</span><span class="flab">{l}</span></div>'
        for n, l in f["stats"])
    return f'''
    <article class="feature reveal" data-cat="{f['cat']}">
      <div class="feature-glow" aria-hidden="true"></div>
      <div class="feature-inner">
        <div class="feature-head">
          <span class="pill pill-flag">Flagship</span>
          <span class="pill pill-patent">{f['badge']}</span>
          {GRANT_CHIP if f.get('grants') else ''}
        </div>
        <h3 class="feature-title">{f['title']}</h3>
        <p class="feature-sub">{f['sub']}</p>
        <p class="feature-meta">{f['meta']}</p>
        <p class="feature-desc">{f['desc']}</p>
        <div class="fstats">{stats}</div>
        {tags_html(f['tags'])}
        {links_html(f['links'])}
        <p class="feature-note">{f['note']}</p>
      </div>
    </article>'''


def card_html(p, i):
    award = f'<span class="pill pill-award">🏆 {p["award"]}</span>' if p.get("award") else ""
    return f'''
      <article class="card reveal{' wide' if p.get('wide') else ''}" data-cat="{p['cat']}" style="--i:{i}">
        <div class="card-spot" aria-hidden="true"></div>
        <div class="card-body">
          <div class="card-top">
            <h3 class="card-title">{p['title']}</h3>
            {award}
          </div>
          <p class="card-sub">{p['sub']}</p>
          <p class="card-meta">{p['meta']}</p>
          <p class="card-desc">{p['desc']}</p>
          {shots_html(p.get('shots'))}
          {tags_html(p['tags'])}
          {links_html(p['links'], small=True)}
          {GRANT_CHIP if p.get('grants') else ''}
        </div>
      </article>'''


SOCIAL_ICON = {
 "discord": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M19.3 5.3A16.9 16.9 0 0 0 15.1 4l-.2.4a12.6 12.6 0 0 1 3.7 1.9 15.7 15.7 0 0 0-13.3 0A12.7 12.7 0 0 1 9 4.4L8.8 4a16.9 16.9 0 0 0-4.2 1.3C2 9.3 1.3 13.2 1.6 17a17 17 0 0 0 5.2 2.6l1-1.7c-.6-.2-1.2-.5-1.7-.8l.4-.3a12.1 12.1 0 0 0 10.9 0l.4.3c-.5.3-1.1.6-1.7.8l1 1.7a17 17 0 0 0 5.2-2.6c.4-4.4-.7-8.3-2.9-11.7ZM8.5 14.7c-1 0-1.9-.9-1.9-2.1s.8-2.1 1.9-2.1 1.9 1 1.9 2.1-.8 2.1-1.9 2.1Zm7 0c-1 0-1.9-.9-1.9-2.1s.8-2.1 1.9-2.1 1.9 1 1.9 2.1-.8 2.1-1.9 2.1Z"/></svg>',
 "linkedin": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5ZM3 9h4v12H3V9Zm7 0h3.8v1.7h.1a4.2 4.2 0 0 1 3.8-2c4 0 4.8 2.6 4.8 6.1V21h-4v-5.5c0-1.3 0-3-1.9-3s-2.1 1.4-2.1 2.9V21h-4V9Z"/></svg>',
 "whatsapp": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15L2 22l5.2-1.4A10 10 0 1 0 12 2Zm5.8 14.2c-.2.7-1.4 1.3-2 1.4-.5.1-1.2.1-1.9-.1a13.6 13.6 0 0 1-6.2-5.4c-.5-.7-.8-1.6-.8-2.4 0-.9.5-1.4.7-1.6.2-.2.5-.3.6-.3h.5c.2 0 .4 0 .6.5l.8 1.9c.1.1.1.3 0 .5l-.3.4-.3.3c-.1.1-.2.3 0 .5a9.6 9.6 0 0 0 4.2 3.6c.3.1.4.1.6-.1l.9-1c.1-.2.3-.2.5-.1l2 .9c.2.1.4.2.4.3v.7Z"/></svg>',
 "email": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/></svg>',
}

def connect_html():
    rows = [("email", "Email", "mailto:" + CONTACT["email"]),
            ("linkedin", "LinkedIn", CONTACT.get("linkedin", "")),
            ("whatsapp", "WhatsApp", CONTACT.get("whatsapp", "")),
            ("discord", "Discord", CONTACT.get("discord", ""))]
    out = []
    for key, label, url in rows:
        if not url:
            continue          # unset channel renders nothing rather than a dead link
        ext = '' if url.startswith("mailto:") else ' target="_blank" rel="noopener noreferrer"'
        out.append(f'<a class="cbtn"{ext} href="{url}">{SOCIAL_ICON[key]}{label}</a>')
    return '<div class="connect">' + "".join(out) + "</div>"


KIND_EM = {"degree":"🎓", "google":"☁️", "hack":"🏆", "work":"📜"}

def creds_html():
    rows = []
    for c in CREDENTIALS:
        links = "".join(
            f'<a class="cred-link" href="{u}"'
            + (' target="_blank" rel="noopener noreferrer"' if u.startswith("http") else ' target="_blank" rel="noopener noreferrer"')
            + f'>{lbl}</a>' for lbl, u in c["files"])
        cid = f'<span class="cred-id">ID {c["cid"]}</span>' if c.get("cid") else ""
        note = f'<p class="cred-note">{c["note"]}</p>' if c.get("note") else ""
        rows.append(f'''
        <div class="cred">
          <span class="cred-em">{KIND_EM.get(c["kind"], "📜")}</span>
          <div class="cred-body">
            <h4>{c["title"]}</h4>
            <p class="cred-meta">{c["issuer"]} · {c["date"]}</p>
            {note}
            <div class="cred-links">{links}{cid}</div>
          </div>
        </div>''')
    return "".join(rows)


def profiles_html():
    return "".join(
        f'<a class="cbtn" href="{u}" target="_blank" rel="noopener noreferrer">{lbl}</a>'
        for lbl, u in PROFILES)


filters = "".join(
    f'<button class="filter{" is-on" if k=="all" else ""}" data-filter="{k}">{label}</button>'
    for k, label in CATS)

cards = "".join(card_html(p, i) for i, p in enumerate(PROJECTS))

HTML = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Jannet Akanksha Ekka — AI/ML Engineer</title>
<meta name="description" content="AI/ML engineer building production agentic systems. Patent-pending multi-agent trading AI, Google Cloud GenAI, and 20+ shipped projects.">
<meta property="og:title" content="Jannet Akanksha Ekka — AI/ML Engineer">
<meta property="og:description" content="Building production agentic AI systems. Patent-pending multi-agent trading AI on Google Cloud.">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
<script>document.documentElement.className+=' js';</script>
<style>
:root{{
  --bg:#08080c; --bg2:#0d0d14; --surf:rgba(255,255,255,.028); --surf2:rgba(255,255,255,.045);
  --line:rgba(255,255,255,.09); --line2:rgba(255,255,255,.16);
  --tx:#ecedf3; --mut:#9b9cae; --dim:#6f7084;
  --a1:#7c5cff; --a2:#22d3ee; --a3:#fbbf24;
  --max:1180px; --ease:cubic-bezier(.22,1,.36,1);
}}
*{{margin:0;padding:0;box-sizing:border-box}}
html{{scroll-behavior:smooth;-webkit-text-size-adjust:100%}}
body{{
  background:var(--bg); color:var(--tx);
  font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  font-size:16px; line-height:1.65; -webkit-font-smoothing:antialiased;
  overflow-x:hidden;
}}
a{{color:inherit;text-decoration:none}}
img{{max-width:100%;display:block}}
::selection{{background:var(--a1);color:#fff}}

/* ---------- ambient background ---------- */
.bgfx{{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}}
.orb{{position:absolute;border-radius:50%;filter:blur(90px);opacity:.30}}
.orb1{{width:44vw;height:44vw;background:#5b3df5;top:-14vw;left:-10vw}}
.orb2{{width:38vw;height:38vw;background:#0e7490;top:34vh;right:-12vw;opacity:.24}}
.orb3{{width:32vw;height:32vw;background:#7c2d9e;bottom:-12vw;left:22vw;opacity:.20}}
.js .orb1{{animation:drift1 26s ease-in-out infinite}}
.js .orb2{{animation:drift2 32s ease-in-out infinite}}
.js .orb3{{animation:drift3 38s ease-in-out infinite}}
@keyframes drift1{{50%{{transform:translate(9vw,7vh) scale(1.12)}}}}
@keyframes drift2{{50%{{transform:translate(-8vw,-6vh) scale(1.08)}}}}
@keyframes drift3{{50%{{transform:translate(6vw,-8vh) scale(1.14)}}}}
.grain{{position:fixed;inset:0;z-index:1;pointer-events:none;opacity:.16;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.5'/%3E%3C/svg%3E")}}
.wrap{{position:relative;z-index:2}}
.shell{{max-width:var(--max);margin:0 auto;padding:0 28px}}

/* ---------- nav ---------- */
nav{{position:fixed;top:0;left:0;right:0;z-index:60;transition:all .4s var(--ease)}}
nav .shell{{display:flex;align-items:center;justify-content:space-between;height:70px}}
nav.stuck{{background:rgba(8,8,12,.72);backdrop-filter:blur(16px);border-bottom:1px solid var(--line)}}
.brand{{font-weight:700;letter-spacing:-.02em;font-size:15px;display:flex;align-items:center;gap:9px}}
.brand i{{width:8px;height:8px;border-radius:50%;background:var(--a2);box-shadow:0 0 12px var(--a2)}}
.js .brand i{{animation:pulse 2.6s ease-in-out infinite}}
@keyframes pulse{{50%{{opacity:.35;transform:scale(.8)}}}}
.navlinks{{display:flex;gap:30px;align-items:center}}
.navlinks a{{font-size:13.5px;color:var(--mut);font-weight:500;position:relative;transition:color .25s}}
.navlinks a::after{{content:'';position:absolute;left:0;bottom:-5px;width:0;height:1.5px;background:var(--a2);transition:width .3s var(--ease)}}
.navlinks a:hover{{color:var(--tx)}} .navlinks a:hover::after{{width:100%}}
.navcta{{border:1px solid var(--line2);padding:8px 16px;border-radius:999px;font-size:13px;font-weight:600;transition:all .28s var(--ease)}}
.navcta:hover{{background:var(--tx);color:var(--bg);border-color:var(--tx)}}
@media(max-width:760px){{.navlinks a:not(.navcta){{display:none}}}}

/* ---------- hero ---------- */
header.hero{{min-height:100svh;display:flex;align-items:center;padding:110px 0 70px}}
.eyebrow{{display:inline-flex;align-items:center;gap:9px;font-size:12.5px;font-weight:600;letter-spacing:.10em;
  text-transform:uppercase;color:var(--a2);border:1px solid rgba(34,211,238,.28);
  background:rgba(34,211,238,.06);padding:7px 15px;border-radius:999px;margin-bottom:26px}}
.eyebrow b{{width:6px;height:6px;border-radius:50%;background:var(--a2)}}
h1.big{{
  font-size:clamp(2.9rem,8.2vw,6.4rem); line-height:.96; font-weight:800;
  letter-spacing:-.045em; margin-bottom:22px;
}}
h1.big .serif{{font-family:'Instrument Serif',Georgia,serif;font-style:italic;font-weight:400;letter-spacing:-.02em;
  background:linear-gradient(100deg,var(--a2),var(--a1) 65%);-webkit-background-clip:text;background-clip:text;color:transparent}}
.rotor{{display:inline-block;position:relative;height:1.05em;overflow:hidden;vertical-align:bottom}}
.rotor span{{display:block;color:var(--a2)}}
.js .rotor{{--n:4}}
.js .rotor .rotor-in{{animation:roll 9s steps(1) infinite}}
@keyframes roll{{0%,22%{{transform:translateY(0)}}25%,47%{{transform:translateY(-25%)}}50%,72%{{transform:translateY(-50%)}}75%,97%{{transform:translateY(-75%)}}100%{{transform:translateY(0)}}}}
.lede{{font-size:clamp(1.02rem,1.55vw,1.2rem);color:var(--mut);max-width:660px;margin-bottom:34px}}
.lede strong{{color:var(--tx);font-weight:600}}
.cta{{display:flex;gap:13px;flex-wrap:wrap;margin-bottom:52px}}
.btn{{display:inline-flex;align-items:center;gap:9px;padding:13px 25px;border-radius:999px;
  font-size:14.5px;font-weight:600;transition:all .3s var(--ease);border:1px solid transparent}}
.btn-p{{background:var(--tx);color:#0a0a0f}}
.btn-p:hover{{transform:translateY(-2px);box-shadow:0 12px 34px rgba(255,255,255,.18)}}
.btn-g{{border-color:var(--line2);color:var(--tx)}}
.btn-g:hover{{background:var(--surf2);border-color:var(--tx);transform:translateY(-2px)}}
.btn svg{{width:16px;height:16px}}
.chips{{display:flex;gap:9px;flex-wrap:wrap}}
.chip{{font-size:12.5px;color:var(--mut);border:1px solid var(--line);background:var(--surf);
  padding:7px 14px;border-radius:999px;transition:all .3s var(--ease)}}
.chip:hover{{border-color:var(--line2);color:var(--tx);transform:translateY(-2px)}}

/* ---------- avatar ---------- */
.idrow{{display:flex;align-items:center;gap:16px;margin-bottom:26px;flex-wrap:wrap}}
.avatar{{position:relative;width:96px;height:96px;border-radius:50%;flex-shrink:0;padding:2.5px;
  background:linear-gradient(140deg,var(--a2),var(--a1) 60%,transparent)}}
.avatar img{{width:100%;height:100%;border-radius:50%;object-fit:cover;object-position:center 22%;
  border:2.5px solid var(--bg);background:var(--bg2)}}
.js .avatar::after{{content:'';position:absolute;inset:-5px;border-radius:50%;
  background:radial-gradient(circle,rgba(124,92,255,.30),transparent 68%);z-index:-1;animation:halo 4.5s ease-in-out infinite}}
@keyframes halo{{50%{{transform:scale(1.14);opacity:.6}}}}
.idrow .eyebrow{{margin-bottom:0}}

/* ---------- screenshot gallery ---------- */
.shots:empty{{display:none}}
.shots{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:11px;margin-top:17px}}
.shot{{display:block;border:1px solid var(--line);border-radius:11px;overflow:hidden;
  background:#000;transition:all .3s var(--ease)}}
.shot:hover{{border-color:var(--a1);transform:translateY(-3px);box-shadow:0 10px 28px rgba(0,0,0,.45)}}
.shot img{{width:100%;aspect-ratio:16/9;object-fit:cover;object-position:top center;display:block}}
.shot-cap{{display:block;font-size:11.5px;color:var(--mut);padding:8px 11px;border-top:1px solid var(--line)}}

/* ---------- lightbox ---------- */
.lb{{position:fixed;inset:0;z-index:200;background:rgba(4,4,8,.93);backdrop-filter:blur(9px);
  display:flex;align-items:center;justify-content:center;flex-direction:column;gap:15px;padding:36px;
  opacity:0;pointer-events:none;transition:opacity .3s var(--ease)}}
.lb.on{{opacity:1;pointer-events:auto}}
.lb img{{max-width:min(1180px,94vw);max-height:80vh;object-fit:contain;
  border:1px solid var(--line2);border-radius:12px;box-shadow:0 26px 80px rgba(0,0,0,.7)}}
.lb-cap{{font-size:14px;color:var(--mut);text-align:center}}
.lb-x{{position:absolute;top:22px;right:26px;width:40px;height:40px;border-radius:50%;cursor:pointer;
  border:1px solid var(--line2);background:var(--surf2);color:var(--tx);font-size:20px;line-height:1;
  font-family:inherit;transition:all .25s}}
.lb-x:hover{{background:var(--tx);color:var(--bg)}}

/* ---------- stats ---------- */
.statbar{{border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:44px 0;background:rgba(255,255,255,.012)}}
.statgrid{{display:grid;grid-template-columns:repeat(4,1fr);gap:26px}}
@media(max-width:720px){{.statgrid{{grid-template-columns:repeat(2,1fr);gap:30px}}}}
.stat .n{{font-size:clamp(1.9rem,4.2vw,2.9rem);font-weight:800;letter-spacing:-.035em;line-height:1;
  background:linear-gradient(150deg,#fff,#9ea0b8);-webkit-background-clip:text;background-clip:text;color:transparent}}
.stat .l{{font-size:12.5px;color:var(--dim);margin-top:9px;letter-spacing:.02em}}

/* ---------- sections ---------- */
section{{padding:104px 0}}
.shead{{margin-bottom:52px;max-width:640px}}
.skicker{{font-size:12px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--a1);margin-bottom:14px}}
.stitle{{font-size:clamp(1.85rem,4.1vw,2.85rem);font-weight:700;letter-spacing:-.035em;line-height:1.08;margin-bottom:15px}}
.ssub{{color:var(--mut);font-size:15.5px}}

/* ---------- flagship ---------- */
.feature{{position:relative;border:1px solid var(--line);border-radius:22px;overflow:hidden;
  background:linear-gradient(165deg,rgba(124,92,255,.10),rgba(34,211,238,.045) 55%,transparent);margin-bottom:34px}}
.feature-glow{{position:absolute;top:-55%;left:15%;width:70%;height:150%;
  background:radial-gradient(ellipse at center,rgba(124,92,255,.20),transparent 68%);pointer-events:none}}
.feature-inner{{position:relative;padding:44px}}
@media(max-width:640px){{.feature-inner{{padding:28px 22px}}}}
.feature-head{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px}}
.pill{{font-size:11.5px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;padding:6px 13px;border-radius:999px}}
.pill-flag{{background:var(--a1);color:#fff}}
.pill-patent{{background:rgba(251,191,36,.13);color:var(--a3);border:1px solid rgba(251,191,36,.3);text-transform:none;letter-spacing:.01em}}
.pill-award{{background:rgba(251,191,36,.13);color:var(--a3);border:1px solid rgba(251,191,36,.3);text-transform:none;letter-spacing:.01em;font-size:11px;white-space:nowrap}}
.feature-title{{font-size:clamp(1.7rem,3.6vw,2.5rem);font-weight:700;letter-spacing:-.035em;line-height:1.1}}
.feature-sub{{font-size:clamp(1rem,1.9vw,1.22rem);color:var(--a2);font-weight:500;margin-top:7px}}
.feature-meta{{font-size:13px;color:var(--dim);margin-top:11px}}
.feature-desc{{color:var(--mut);margin-top:20px;max-width:790px;font-size:15.5px}}
.feature-desc em{{color:var(--tx);font-style:normal;font-weight:600}}
.fstats{{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin:30px 0;padding:24px 0;
  border-top:1px solid var(--line);border-bottom:1px solid var(--line)}}
@media(max-width:620px){{.fstats{{grid-template-columns:repeat(2,1fr);gap:22px}}}}
.fnum{{display:block;font-size:1.65rem;font-weight:800;letter-spacing:-.03em;color:var(--tx)}}
.flab{{display:block;font-size:11.5px;color:var(--dim);margin-top:4px}}
.feature-note{{font-size:12.5px;color:var(--dim);margin-top:18px;font-style:italic}}

/* ---------- filters ---------- */
.filters{{display:flex;gap:9px;flex-wrap:wrap;margin-bottom:34px}}
.filter{{font-family:inherit;font-size:13.5px;font-weight:500;color:var(--mut);cursor:pointer;
  background:var(--surf);border:1px solid var(--line);padding:9px 18px;border-radius:999px;transition:all .28s var(--ease)}}
.filter:hover{{color:var(--tx);border-color:var(--line2)}}
.filter.is-on{{background:var(--tx);color:var(--bg);border-color:var(--tx);font-weight:600}}

/* ---------- cards ---------- */
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:20px}}
@media(max-width:520px){{.grid{{grid-template-columns:1fr}}}}
.card{{position:relative;border:1px solid var(--line);border-radius:17px;background:var(--surf);
  overflow:hidden;transition:transform .42s var(--ease),border-color .3s,background .3s}}
.card:hover{{transform:translateY(-5px);border-color:var(--line2);background:var(--surf2)}}
.card-spot{{position:absolute;inset:0;opacity:0;transition:opacity .35s;pointer-events:none;
  background:radial-gradient(420px circle at var(--mx,50%) var(--my,50%),rgba(124,92,255,.16),transparent 42%)}}
.card:hover .card-spot{{opacity:1}}
.card-body{{position:relative;padding:26px}}
.card-top{{display:flex;gap:10px;align-items:flex-start;justify-content:space-between;flex-wrap:wrap}}
.card-title{{font-size:1.14rem;font-weight:700;letter-spacing:-.022em;line-height:1.25}}
.card-sub{{font-size:13.5px;color:var(--a2);font-weight:500;margin-top:5px}}
.card-meta{{font-size:12px;color:var(--dim);margin-top:8px}}
.card-desc{{font-size:14px;color:var(--mut);margin-top:14px}}
.card.hide{{display:none}}
.card.wide{{grid-column:span 2}}
@media(max-width:1100px){{.card.wide{{grid-column:span 1}}}}

/* ---------- tags + links ---------- */
.tags{{display:flex;gap:7px;flex-wrap:wrap;margin-top:16px}}
.tag{{font-size:11.5px;color:var(--mut);background:rgba(255,255,255,.045);
  border:1px solid var(--line);padding:4px 11px;border-radius:6px}}
.lnks{{display:flex;gap:9px;flex-wrap:wrap;margin-top:18px}}
.lnk{{display:inline-flex;align-items:center;gap:7px;font-size:13.5px;font-weight:600;
  padding:9px 16px;border-radius:9px;border:1px solid var(--line2);transition:all .28s var(--ease)}}
.lnk.sm{{font-size:12.5px;padding:7px 13px}}
.lnk .ico{{display:inline-flex;width:14px;height:14px}}
.lnk .ico svg{{width:100%;height:100%}}
.lnk.live{{background:var(--a1);border-color:var(--a1);color:#fff}}
.lnk.live:hover{{background:#6b4ae8;transform:translateY(-2px);box-shadow:0 8px 22px rgba(124,92,255,.34)}}
.lnk.code:hover,.lnk.doc:hover{{background:var(--surf2);border-color:var(--tx);transform:translateY(-2px)}}

/* ---------- marquee ---------- */
.marq{{overflow:hidden;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:26px 0;
  -webkit-mask-image:linear-gradient(90deg,transparent,#000 9%,#000 91%,transparent);
  mask-image:linear-gradient(90deg,transparent,#000 9%,#000 91%,transparent)}}
.marq-in{{display:flex;gap:46px;width:max-content}}
.js .marq-in{{animation:slide 42s linear infinite}}
.marq:hover .marq-in{{animation-play-state:paused}}
@keyframes slide{{to{{transform:translateX(-50%)}}}}
.marq span{{font-size:14.5px;font-weight:600;color:var(--dim);white-space:nowrap;letter-spacing:.01em}}

/* ---------- timeline ---------- */
.tl{{position:relative;padding-left:30px}}
.tl::before{{content:'';position:absolute;left:5px;top:6px;bottom:6px;width:1px;
  background:linear-gradient(180deg,var(--a1),var(--a2),transparent)}}
.tlrow{{position:relative;padding-bottom:38px}}
.tlrow:last-child{{padding-bottom:0}}
.tlrow::before{{content:'';position:absolute;left:-29px;top:7px;width:11px;height:11px;border-radius:50%;
  background:var(--bg);border:2px solid var(--a1)}}
.tlrow h4{{font-size:1.1rem;font-weight:700;letter-spacing:-.02em}}
.tlrow .org{{color:var(--a2);font-size:14px;font-weight:500;margin-top:3px}}
.tlrow .when{{font-size:12.5px;color:var(--dim);margin-top:5px}}
.tlrow p{{color:var(--mut);font-size:14.5px;margin-top:11px}}

/* ---------- about ---------- */
.two{{display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:start}}
@media(max-width:880px){{.two{{grid-template-columns:1fr;gap:44px}}}}
.abtxt p{{color:var(--mut);margin-bottom:17px;font-size:15.5px}}
.abtxt strong{{color:var(--tx);font-weight:600}}
.awards{{display:flex;flex-direction:column;gap:11px}}
.award{{display:flex;gap:14px;align-items:flex-start;border:1px solid var(--line);background:var(--surf);
  border-radius:13px;padding:17px 19px;transition:all .3s var(--ease)}}
.award:hover{{border-color:var(--line2);background:var(--surf2);transform:translateX(4px)}}
.award .em{{font-size:20px;line-height:1.2}}
.award h5{{font-size:14.5px;font-weight:700;letter-spacing:-.015em}}
.award p{{font-size:13px;color:var(--mut);margin-top:3px}}
.award a{{color:var(--a2);border-bottom:1px solid rgba(34,211,238,.35)}}

/* ---------- credentials ---------- */
.creds{{display:grid;grid-template-columns:repeat(auto-fill,minmax(390px,1fr));gap:12px}}
@media(max-width:560px){{.creds{{grid-template-columns:1fr}}}}
.cred{{display:flex;gap:14px;align-items:flex-start;border:1px solid var(--line);
  background:var(--surf);border-radius:13px;padding:17px 19px;transition:all .3s var(--ease)}}
.cred:hover{{border-color:var(--line2);background:var(--surf2);transform:translateY(-2px)}}
.cred-em{{font-size:19px;line-height:1.3;flex-shrink:0}}
.cred-body{{min-width:0}}
.cred h4{{font-size:14.5px;font-weight:700;letter-spacing:-.015em;line-height:1.35}}
.cred-meta{{font-size:12.5px;color:var(--a2);margin-top:3px}}
.cred-note{{font-size:12.5px;color:var(--mut);margin-top:5px}}
.cred-links{{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:9px}}
.cred-link{{font-size:12px;font-weight:600;color:var(--tx);border:1px solid var(--line2);
  padding:4px 11px;border-radius:7px;transition:all .25s var(--ease)}}
.cred-link:hover{{background:var(--tx);color:var(--bg);border-color:var(--tx)}}
.cred-id{{font-size:11px;color:var(--dim);font-family:ui-monospace,SFMono-Regular,Menlo,monospace}}

/* ---------- grants chip ---------- */
.grant-chip{{display:inline-flex;align-items:center;gap:8px;font-size:12px;font-weight:600;
  color:var(--a3);border:1px solid rgba(251,191,36,.32);background:rgba(251,191,36,.08);
  padding:6px 13px;border-radius:999px;margin-top:14px;transition:all .28s var(--ease)}}
.grant-chip:hover{{background:rgba(251,191,36,.16);border-color:var(--a3);transform:translateY(-2px)}}
.feature-head .grant-chip{{margin-top:0}}
.gdot{{width:6px;height:6px;border-radius:50%;background:var(--a3);flex-shrink:0}}
.js .gdot{{animation:pulse 2.4s ease-in-out infinite}}

/* ---------- backing / form ---------- */
.backing{{border:1px solid var(--line);border-radius:22px;overflow:hidden;position:relative;
  background:linear-gradient(160deg,rgba(251,191,36,.07),rgba(124,92,255,.06) 55%,transparent)}}
.backing-in{{position:relative;display:grid;grid-template-columns:1fr 1fr;gap:48px;padding:46px}}
@media(max-width:900px){{.backing-in{{grid-template-columns:1fr;gap:34px;padding:30px 24px}}}}
.backing h3{{font-size:clamp(1.5rem,3vw,2.1rem);font-weight:700;letter-spacing:-.032em;line-height:1.14}}
.backing .bsub{{color:var(--mut);margin-top:15px;font-size:15px}}
.backing .bsub strong{{color:var(--tx);font-weight:600}}

.field{{margin-bottom:14px}}
.field label{{display:block;font-size:12.5px;font-weight:600;color:var(--mut);margin-bottom:6px}}
.field label .req{{color:var(--a3)}}
.field input,.field textarea{{width:100%;font-family:inherit;font-size:14.5px;color:var(--tx);
  background:rgba(255,255,255,.04);border:1px solid var(--line2);border-radius:10px;
  padding:11px 14px;transition:all .25s var(--ease)}}
.field textarea{{resize:vertical;min-height:78px}}
.field input::placeholder,.field textarea::placeholder{{color:var(--dim)}}
.field input:focus,.field textarea:focus{{outline:none;border-color:var(--a1);
  background:rgba(255,255,255,.06);box-shadow:0 0 0 3px rgba(124,92,255,.16)}}
.hp{{position:absolute!important;left:-9999px!important;opacity:0!important;height:0!important}}
.fbtn{{width:100%;justify-content:center;margin-top:4px;cursor:pointer;font-family:inherit;border:none}}
.fmsg{{font-size:13.5px;margin-top:12px;min-height:20px}}
.fmsg.ok{{color:#4ade80}} .fmsg.bad{{color:#f87171}}

.connect{{display:flex;gap:10px;flex-wrap:wrap;margin-top:24px}}
.cbtn{{display:inline-flex;align-items:center;gap:9px;font-size:13.5px;font-weight:600;
  padding:10px 17px;border-radius:10px;border:1px solid var(--line2);transition:all .28s var(--ease)}}
.cbtn:hover{{background:var(--surf2);border-color:var(--tx);transform:translateY(-2px)}}
.cbtn svg{{width:15px;height:15px;flex-shrink:0}}

/* ---------- contact ---------- */
.contact{{text-align:center;padding:110px 0}}
.contact h2{{font-size:clamp(2.1rem,5.6vw,3.8rem);font-weight:800;letter-spacing:-.04em;line-height:1.05;margin-bottom:20px}}
.contact h2 .serif{{font-family:'Instrument Serif',Georgia,serif;font-style:italic;font-weight:400;
  background:linear-gradient(100deg,var(--a2),var(--a1));-webkit-background-clip:text;background-clip:text;color:transparent}}
.contact p{{color:var(--mut);max-width:520px;margin:0 auto 34px;font-size:16px}}
footer{{border-top:1px solid var(--line);padding:30px 0;font-size:13px;color:var(--dim)}}
footer .shell{{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}}
footer a:hover{{color:var(--tx)}}

/* ---------- reveal (JS-gated: no JS = fully visible) ---------- */
.js .reveal{{opacity:0;transform:translateY(26px);
  transition:opacity .78s var(--ease),transform .78s var(--ease)}}
.js .reveal.in{{opacity:1;transform:none}}
.js .grid .reveal{{transition-delay:calc(var(--i,0) * 42ms)}}

@media (prefers-reduced-motion:reduce){{
  *,*::before,*::after{{animation-duration:.001ms!important;animation-iteration-count:1!important;
    transition-duration:.001ms!important;scroll-behavior:auto!important}}
  .js .reveal{{opacity:1!important;transform:none!important}}
}}
</style>
</head>
<body>

<div class="bgfx" aria-hidden="true">
  <div class="orb orb1"></div><div class="orb orb2"></div><div class="orb orb3"></div>
</div>
<div class="grain" aria-hidden="true"></div>

<div class="wrap">

<nav id="nav">
  <div class="shell">
    <a href="#top" class="brand"><i></i> Jannet Akanksha Ekka</a>
    <div class="navlinks">
      <a href="#work">Work</a>
      <a href="#about">About</a>
      <a href="#experience">Experience</a>
      <a href="#credentials">Credentials</a>
      <a href="#backing">Backing</a>
      <a href="Jannet_GenAI.pdf" target="_blank" rel="noopener noreferrer" class="navcta">Résumé</a>
    </div>
  </div>
</nav>

<header class="hero" id="top">
  <div class="shell">
    <div class="idrow reveal">
      <div class="avatar"><img src="profile%20pic.png" alt="Jannet Akanksha Ekka" width="96" height="96"></div>
      <div class="eyebrow"><b></b> Open to AI/ML engineering roles</div>
    </div>
    <h1 class="big reveal">
      I build <span class="serif">agentic AI</span><br>
      that runs in
      <span class="rotor"><span class="rotor-in">
        <span>production.</span><span>the open.</span><span>real markets.</span><span>production.</span>
      </span></span>
    </h1>
    <p class="lede reveal">
      AI/ML engineer shipping multi-agent systems end to end — architecture, learning loop, cloud deployment and live operations.
      Author of a <strong>patent-pending multi-agent trading AI</strong> running continuously on Google Cloud, backed by
      <strong>4+ years of enterprise engineering at Deloitte</strong> and a <strong>Rank&nbsp;1</strong> PGP in AI/ML.
    </p>
    <div class="cta reveal">
      <a class="btn btn-p" href="#work">See the work
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
      <a class="btn btn-g" href="mailto:jannetekka96@gmail.com">Get in touch</a>
    </div>
    <div class="chips reveal">
      <span class="chip">⚙️ Patent pending</span>
      <span class="chip">🏆 OpenServ Best DeFi — Winner</span>
      <span class="chip">🥇 Rank 1 — PGP AI/ML</span>
      <span class="chip">☁️ Google Cloud Gen AI Academy</span>
    </div>
  </div>
</header>

<div class="statbar">
  <div class="shell">
    <div class="statgrid">
      <div class="stat reveal"><div class="n" data-count="24">24</div><div class="l">Projects shipped</div></div>
      <div class="stat reveal"><div class="n" data-count="33">33</div><div class="l">K lines in flagship</div></div>
      <div class="stat reveal"><div class="n" data-count="4">4</div><div class="l">Years enterprise eng.</div></div>
      <div class="stat reveal"><div class="n" data-count="1">1</div><div class="l">Patent filed</div></div>
    </div>
  </div>
</div>

<section id="work">
  <div class="shell">
    <div class="shead reveal">
      <div class="skicker">Selected work</div>
      <h2 class="stitle">Systems, not notebooks.</h2>
      <p class="ssub">Everything below either runs somewhere or ships with the tests that prove it works. Filter by discipline.</p>
    </div>
    {flagship_html(FLAGSHIP)}
    <div class="filters reveal">{filters}</div>
    <div class="grid" id="grid">{cards}</div>
  </div>
</section>

<div class="marq" aria-label="Technology stack">
  <div class="marq-in">
    <span>Python</span><span>Google ADK</span><span>MCP</span><span>Vertex AI</span><span>Gemini</span><span>Imagen</span>
    <span>BigQuery</span><span>AlloyDB</span><span>pgvector</span><span>Cloud Run</span><span>Cloudflare Workers</span>
    <span>TensorFlow</span><span>PyTorch</span><span>scikit-learn</span><span>Optuna</span><span>CatBoost</span>
    <span>FastAPI</span><span>Streamlit</span><span>React</span><span>TypeScript</span><span>Docker</span><span>SQL</span>
    <span>Python</span><span>Google ADK</span><span>MCP</span><span>Vertex AI</span><span>Gemini</span><span>Imagen</span>
    <span>BigQuery</span><span>AlloyDB</span><span>pgvector</span><span>Cloud Run</span><span>Cloudflare Workers</span>
    <span>TensorFlow</span><span>PyTorch</span><span>scikit-learn</span><span>Optuna</span><span>CatBoost</span>
    <span>FastAPI</span><span>Streamlit</span><span>React</span><span>TypeScript</span><span>Docker</span><span>SQL</span>
  </div>
</div>

<section id="about">
  <div class="shell">
    <div class="two">
      <div>
        <div class="shead reveal" style="margin-bottom:30px">
          <div class="skicker">About</div>
          <h2 class="stitle">From breaking systems<br>to building them.</h2>
        </div>
        <div class="abtxt reveal">
          <p>I spent four years at <strong>Deloitte</strong> leading a QA automation team — finding the ways enterprise systems fail before customers did. That work taught me something most ML curricula skip: <strong>a model that cannot tell you when it is wrong is not finished.</strong></p>
          <p>So when I moved into AI, I built the way I used to test. My flagship system refuses to trade on a data feed it cannot verify, logs a plain-English reason for every decision, and gates every weekly model update behind statistical checks designed to catch overfitting rather than flatter it.</p>
          <p>I completed my <strong>PGP in AI/ML at UT Austin McCombs &amp; Great Lakes at Rank 1</strong>, then <strong>Google Cloud's Gen AI Academy</strong> — Vertex AI, Gemini, ADK, MCP and AlloyDB. Today I'm looking for teams building agentic systems that have to survive contact with the real world.</p>
        </div>
      </div>
      <div class="awards reveal">
        <div class="award"><span class="em">⚙️</span><div><h5>Provisional patent filed</h5><p>India, App. No. 202631090789 — the SMT multi-agent decision architecture.</p></div></div>
        <div class="award"><span class="em">📈</span><div><h5>WEEX AI Wars I — #1 preliminary leaderboard</h5><p>Top of 230+ teams, then one of 37 finalists in the $880K live AI trading competition. <a href="https://www.weex.com/news/detail/how-smart-money-tracker-survived-live-ai-trading-at-weex-ai-hackathon-343641" target="_blank" rel="noopener noreferrer">Coverage</a></p></div></div>
        <div class="award"><span class="em">🏆</span><div><h5>Winner — Best DeFi Application</h5><p>OpenServ × Hack2skill. Runner-up for Best Website Application.</p></div></div>
        <div class="award"><span class="em">☁️</span><div><h5>Top 101 of 1,500+ teams</h5><p>Google Cloud Gen AI Academy APAC hackathon, Cohort 2 — advanced to prototype refinement.</p></div></div>
        <div class="award"><span class="em">🥇</span><div><h5>Rank 1 in batch</h5><p>PGP in AI/ML, UT Austin McCombs &amp; Great Lakes — GPA 4.09/5.</p></div></div>
        <div class="award"><span class="em">📜</span><div><h5>11 credentials, all verifiable</h5><p>Google Cloud Gen AI Academy (2025 &amp; APAC 2026 Cohorts 1–2) · Gen AI Exchange · Agentic AI Day · Asha AI Hackathon · CPSAT. <a href="#credentials">See them all</a></p></div></div>
      </div>
    </div>
  </div>
</section>

<section id="experience">
  <div class="shell">
    <div class="shead reveal">
      <div class="skicker">Experience</div>
      <h2 class="stitle">Where I've worked.</h2>
    </div>
    <div class="tl">
      <div class="tlrow reveal">
        <h4>Founder &amp; Sole Engineer — Smart Money Trading (SMT)</h4>
        <div class="org">Independent · patent pending</div><div class="when">2026 – Present</div>
        <p>Designed, built and operate a patent-pending multi-agent trading AI running continuously on Google Cloud — 33,000 lines across 153 modules, a six-persona committee under a learned Judge, a self-retuning learning loop behind a statistical overfitting gate, and an explanation layer that justifies every decision. Shortlisted top 101 of 1,500+ teams at the Google Cloud Gen AI Academy APAC hackathon.</p>
      </div>
      <div class="tlrow reveal">
        <h4>Independent AI Engineer</h4>
        <div class="org">Freelance &amp; competitive builds</div><div class="when">2024 – 2025</div>
        <p>Started at the OpenServ × Hack2skill hackathon, where Smart Money Tracker <strong>won Best DeFi Application</strong> and placed runner-up for Best Website Application. Went on to ship VerseCanvas on Vertex AI, multi-agent assistants on Google ADK, MCP and AlloyDB, and the applied AI projects above.</p>
      </div>
      <div class="tlrow reveal">
        <h4>Lead Frontend Developer</h4>
        <div class="org">AutoKorrekt — EdTech startup MVP</div><div class="when">May 2024 – Jan 2025</div>
        <p>Interactive PDF processing with coordinate-based text extraction, integrating AWS Textract OCR and Mistral models into an AI answer-evaluation workflow. Bilingual EN/DE interface scaling to 1,000+ concurrent submissions.</p>
      </div>
      <div class="tlrow reveal">
        <h4>Machine Learning Intern</h4>
        <div class="org">Internship Studio</div><div class="when">Jul 2024 – Aug 2024</div>
        <p>Random Forest model predicting YouTube ad views across a 15,000+ video dataset, packaged for integration with business dashboards.</p>
      </div>
      <div class="tlrow reveal">
        <h4>Test Automation Engineer (Analyst)</h4>
        <div class="org">Deloitte Consulting LLP — Bangalore</div><div class="when">Aug 2019 – Jan 2023</div>
        <p>Led a 6-member QA team for Fortune 500 clients including AT&amp;T and Hewlett Packard Enterprise. Improved test execution efficiency 83%, tracked quality across 343 components, and analysed 50,000+ SAP Hybris transactions in Python.</p>
      </div>
    </div>
  </div>
</section>

<section id="credentials">
  <div class="shell">
    <div class="shead reveal">
      <div class="skicker">Credentials</div>
      <h2 class="stitle">Every certificate, verifiable.</h2>
      <p class="ssub">Badge profiles first — they are confirmable by a third party and stay current. The certificate files are linked underneath for anything the profiles don't cover.</p>
    </div>
    <div class="connect reveal" style="margin:0 0 26px">{profiles_html()}</div>
    <div class="creds">{creds_html()}</div>
  </div>
</section>

<section id="backing">
  <div class="shell">
    <div class="shead reveal">
      <div class="skicker">Backing &amp; collaboration</div>
      <h2 class="stitle">Actively seeking grants and partners.</h2>
      <p class="ssub">SMT is patent-pending, running live on Google Cloud, and looking for its next backer. If you fund early-stage AI, run a grant programme, or want to build on it &mdash; leave your details and I'll come back to you.</p>
    </div>
    <div class="backing reveal">
      <div class="backing-in">
        <div>
          <h3>Fund, partner, or just say hello.</h3>
          <p class="bsub">I'm looking for <strong>grants and early-stage funding</strong> for Smart Money Trading, and I'm open to collaboration on any of the projects here. Tell me who you are and I'll follow up personally.</p>
          <p class="bsub">Prefer to talk first? Reach me on any of these.</p>
          {connect_html()}
        </div>
        <div>
          <form id="gform" action="https://api.web3forms.com/submit" method="POST" novalidate>
            <input type="hidden" name="access_key" value="{CONTACT.get('web3forms_key','')}">
            <input type="hidden" name="subject" value="Grant / collaboration enquiry from your portfolio">
            <input type="hidden" name="from_name" value="Portfolio — jannetekka.github.io">
            <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
            <div class="field">
              <label for="f-name">Name <span class="req">*</span></label>
              <input id="f-name" type="text" name="name" required placeholder="Your name">
            </div>
            <div class="field">
              <label for="f-email">Email <span class="req">*</span></label>
              <input id="f-email" type="email" name="email" required placeholder="you@organisation.com">
            </div>
            <div class="field">
              <label for="f-site">Website</label>
              <input id="f-site" type="url" name="website" placeholder="https://">
            </div>
            <div class="field">
              <label for="f-msg">Anything else? <span style="color:var(--dim);font-weight:400">(optional)</span></label>
              <textarea id="f-msg" name="message" placeholder="Grant programme, fund, or what you'd like to build"></textarea>
            </div>
            <button type="submit" class="btn btn-p fbtn" id="fsubmit">Send</button>
            <div class="fmsg" id="fmsg" role="status" aria-live="polite"></div>
          </form>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="contact">
  <div class="shell">
    <div class="reveal">
      <h2>Let's build something<br><span class="serif">that actually ships.</span></h2>
      <p>Open to AI/ML engineering, agentic systems and GenAI application roles. The inbox is always open.</p>
      <div class="cta" style="justify-content:center">
        <a class="btn btn-p" href="mailto:jannetekka96@gmail.com">jannetekka96@gmail.com</a>
        <a class="btn btn-g" href="https://www.linkedin.com/in/jannet-akanksha-ekka-a18692122/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
        <a class="btn btn-g" href="https://github.com/JannetEkka" target="_blank" rel="noopener noreferrer">GitHub</a>
      </div>
    </div>
  </div>
</section>

<footer>
  <div class="shell">
    <span>© 2026 Jannet Akanksha Ekka · Kolkata, India</span>
    <span>
      <a href="Jannet_GenAI.pdf" target="_blank" rel="noopener noreferrer">GenAI résumé</a> ·
      <a href="JannetEkka_Resume.pdf" target="_blank" rel="noopener noreferrer">Data science résumé</a> ·
      <a href="https://www.credly.com/users/jannet-akanksha-ekka/badges" target="_blank" rel="noopener noreferrer">Credly</a> ·
      <a href="https://www.skills.google/public_profiles/2a91b2f0-31d3-467e-ba45-3ba1888a908e" target="_blank" rel="noopener noreferrer">Google Skills</a>
    </span>
  </div>
</footer>

</div>

<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="Screenshot viewer">
  <button class="lb-x" id="lbx" aria-label="Close">&times;</button>
  <img id="lbimg" src="" alt="">
  <div class="lb-cap" id="lbcap"></div>
</div>

<script>
(function(){{
  var R = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* sticky nav */
  var nav = document.getElementById('nav');
  addEventListener('scroll', function(){{
    nav.classList.toggle('stuck', scrollY > 40);
  }}, {{passive:true}});

  /* hero enters immediately on load — never waits on a scroll observer */
  var hero = [].slice.call(document.querySelectorAll('.hero .reveal'));
  hero.forEach(function(el,i){{ el.style.transitionDelay = (i*90) + 'ms'; }});
  requestAnimationFrame(function(){{ requestAnimationFrame(function(){{
    hero.forEach(function(el){{ el.classList.add('in'); }});
  }}); }});

  /* scroll reveal — with a hard failsafe so text can never stay hidden */
  var rev = [].slice.call(document.querySelectorAll('.reveal')).filter(function(el){{
    return !el.closest('.hero');
  }});
  function showAll(){{ rev.concat(hero).forEach(function(el){{ el.classList.add('in'); }}); }}
  if (R || !('IntersectionObserver' in window)) {{
    showAll();
  }} else {{
    var io = new IntersectionObserver(function(es){{
      es.forEach(function(e){{
        if (e.isIntersecting) {{ e.target.classList.add('in'); io.unobserve(e.target); }}
      }});
    }}, {{threshold:0.08, rootMargin:'0px 0px -40px 0px'}});
    rev.forEach(function(el){{ io.observe(el); }});
    setTimeout(showAll, 3500);           /* failsafe #1: never leave content invisible */
    addEventListener('load', function(){{ setTimeout(showAll, 1200); }});
  }}

  /* count-up */
  function countUp(el){{
    var target = parseFloat(el.dataset.count), t0 = null, dur = 1300;
    if (isNaN(target) || R) return;
    function step(ts){{
      if (!t0) t0 = ts;
      var p = Math.min((ts - t0)/dur, 1), e = 1 - Math.pow(1-p, 3);
      el.textContent = Math.round(target*e);
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = target;
    }}
    requestAnimationFrame(step);
  }}
  var nums = [].slice.call(document.querySelectorAll('[data-count]'));
  if ('IntersectionObserver' in window && !R) {{
    var nio = new IntersectionObserver(function(es){{
      es.forEach(function(e){{ if (e.isIntersecting) {{ countUp(e.target); nio.unobserve(e.target); }} }});
    }}, {{threshold:0.5}});
    nums.forEach(function(n){{ nio.observe(n); }});
  }}

  /* cursor spotlight on cards */
  if (!R && matchMedia('(hover:hover)').matches) {{
    document.querySelectorAll('.card').forEach(function(c){{
      c.addEventListener('pointermove', function(ev){{
        var r = c.getBoundingClientRect();
        c.style.setProperty('--mx', (ev.clientX - r.left) + 'px');
        c.style.setProperty('--my', (ev.clientY - r.top) + 'px');
      }});
    }});
  }}

  /* screenshot lightbox — anchors point at the image, so it still works without JS */
  var lb=document.getElementById('lb'), lbimg=document.getElementById('lbimg'), lbcap=document.getElementById('lbcap');
  function closeLb(){{ lb.classList.remove('on'); lbimg.src=''; }}
  document.querySelectorAll('.shot').forEach(function(a){{
    a.addEventListener('click', function(ev){{
      ev.preventDefault();
      lbimg.src = a.getAttribute('href');
      lbcap.textContent = a.dataset.cap || '';
      lb.classList.add('on');
    }});
  }});
  document.getElementById('lbx').addEventListener('click', closeLb);
  lb.addEventListener('click', function(e){{ if (e.target === lb) closeLb(); }});
  addEventListener('keydown', function(e){{ if (e.key === 'Escape') closeLb(); }});

  /* grant form */
  var gform=document.getElementById('gform');
  if (gform) {{
    var fmsg=document.getElementById('fmsg'), fbtn=document.getElementById('fsubmit');
    var keyEl=gform.querySelector('[name=access_key]');
    var MAIL='{CONTACT["email"]}';
    gform.addEventListener('submit', function(ev){{
      ev.preventDefault();
      if (!gform.checkValidity()) {{ gform.reportValidity(); return; }}
      var fd=new FormData(gform);
      var key=(keyEl.value||'').trim();

      /* No access key configured yet — fall back to opening an email so an
         enquiry can never be silently lost. */
      if (!key) {{
        var body='Name: '+(fd.get('name')||'')+'%0D%0AEmail: '+(fd.get('email')||'')
                +'%0D%0AWebsite: '+(fd.get('website')||'')+'%0D%0A%0D%0A'+(fd.get('message')||'');
        fmsg.className='fmsg ok';
        fmsg.textContent='Opening your email app…';
        location.href='mailto:'+MAIL+'?subject=Grant%20/%20collaboration%20enquiry&body='+body;
        return;
      }}

      fbtn.disabled=true; fbtn.textContent='Sending…';
      fmsg.className='fmsg'; fmsg.textContent='';
      fetch('https://api.web3forms.com/submit', {{
        method:'POST',
        headers:{{'Content-Type':'application/json', Accept:'application/json'}},
        body: JSON.stringify(Object.fromEntries(fd))
      }})
      .then(function(r){{ return r.json(); }})
      .then(function(d){{
        if (d.success) {{
          gform.reset();
          fmsg.className='fmsg ok';
          fmsg.textContent="Thank you — I'll get back to you shortly.";
        }} else {{
          throw new Error(d.message||'failed');
        }}
      }})
      .catch(function(){{
        fmsg.className='fmsg bad';
        fmsg.innerHTML='Could not send. Please email <a href="mailto:'+MAIL+'" style="color:var(--a2)">'+MAIL+'</a> directly.';
      }})
      .finally(function(){{ fbtn.disabled=false; fbtn.textContent='Send'; }});
    }});
  }}

  /* filters */
  var cards = [].slice.call(document.querySelectorAll('#grid .card'));
  document.querySelectorAll('.filter').forEach(function(btn){{
    btn.addEventListener('click', function(){{
      document.querySelectorAll('.filter').forEach(function(b){{ b.classList.remove('is-on'); }});
      btn.classList.add('is-on');
      var f = btn.dataset.filter;
      cards.forEach(function(c){{
        var show = (f === 'all' || c.dataset.cat === f);
        c.classList.toggle('hide', !show);
        if (show) c.classList.add('in');
      }});
    }});
  }});
}})();
</script>
</body>
</html>
'''

out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "index.html")
out.write_text(HTML, encoding="utf-8")
print(f"wrote {out}  ({len(HTML):,} bytes, {len(PROJECTS)+1} projects)")
