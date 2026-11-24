# Lists open Forward Deployed / deployment / solutions roles in India, APAC or "global remote"
# from the public Greenhouse, Ashby and Lever job-board APIs (only open postings are listed there).
# Run: python3 -I resumes/tools/fde_scan.py   (about 2 minutes). Sends no personal data.
# A board's own page can still 404 (Cursor hosts its jobs at cursor.com/careers), so open each link.
import json, re, sys, urllib.request, concurrent.futures as cf
slugs = """11x abridge ada adept ai21 ai21labs airbyte airops airtable aisera aleph-alpha algolia alignerr alloy ambience ambiencehealthcare anthropic anysphere apollo-io appen arize artisan assembled assemblyai atlan atlanhq attio augment base44 baseten basis beamery beautifulai bland blandai bolna bolt brex browserstack capillary cartesia castellum cerebras chainguard character chargebee chroma clay clevertap clickhouse cloudflare cockroachlabs codeium coderabbit cognition cognizant cohere commonroom commure composio confluent contextual convex copyai coreweave coveo cred crescendo crescendoai cresta cribl crusoe cursor daily darwinbox databricks datadog dbtlabs decagon deel deepgram deepmind devrev drata druva eightfold elastic elevenlabs ema emergent emergentlabsinc etched exotel extend factory fern figma fin fireworksai fivetran flagright flyio forethought fractal freshdesk freshworks galileo gamma giga giga-ml gigaml gitlab glean glean-ai glean-work gleanwork gnani gocomet gong grafanalabs graphite greptile gretel groq groww gupshup gushwork h2o h2oai handshake haptik haptik-ai harvey harveyai hashicorp hasura hebbia hevo hevodata hex highspot hightouch hippocratic hirevue honeycomb hummingbird hyperscience icertis imbue inflection innovaccer instabase intercom invisible invisibletech ironclad jasper juspay kore kore-ai koreai koyeb krisp krutrim labelbox lambda lancedb langchain latentview leadsquared leena legora level-ai levelai lightmatter linear liveblocks livekit llamaindex lorikeet lovable lyzr magic mambu maven mavenagi meesho mercor mercury micro1 mindtickle mintlify mistral modal moengage mongodb motherduck moveworks mu-sigma nabla nebius neo4j neon neysa niramai northflank notion nurix nurixai nymbus observe observe-ai observeai ocrolus onfido openai outlier outreach palantir palantirtechnologies paperspace paradox parloa perplexity perplexityai persona phonepe pika pinecone pipe pipecat plaid planetscale plexe poly-ai polyai poolside portkey posthog postman postmanlabs qdrant qdrant-tech qodo quantiphi qure qureai railway ramp rasa razorpay readme realfast realfastai rebellions redis reducto regal regalvoice reka remote render replit resilinc retell retellai retool rillet rippling rocketium rocketlane rossum rox rubrik runpod runway salesloft sama sambanova sardine sarvam scale scaleai scrut seismic sentry shuru sierra sierraai sigmoid simplismart smallest smallestai snorkel snorkelai snowflake snyk socure sourcegraph speakeasy speechmatics sprinklr sprinto spyne stackblitz stainless stripe suki sumsub suno supabase swiggy synthflow tabnine temenos temporal tennr tenstorrent thoughtmachine tigeranalytics tines together togetherai toloka tome tonic torq tredence truefoundry trydecagon turing turso twilio typeface unify uniphore uniphore-1 unit21 unstructured v0 vanta vapi vast vectara vercel vespa vymo warp weaviate whatfix windsurf wiz workato writer wysa xai xata yellow-ai yellowai yellowmessenger zed zeet zendesk zerodha zeta zeta-suite zilliz zluri""".split()
TERMS = re.compile(r"forward[- ]deployed|deployment engineer|deployed engineer|solutions engineer|solutions architect|applied ai engineer|customer engineer|implementation engineer|ai engineer, customer|field engineer|deployment strategist|agent engineer|ai deployment", re.I)
def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"}), timeout=20) as r: return json.load(r)
    except Exception: return None
def scan(s):
    out=[]
    d=get(f"https://boards-api.greenhouse.io/v1/boards/{s}/jobs")
    if d and d.get("jobs"):
        for j in d["jobs"]:
            if TERMS.search(j["title"]): out.append(("gh",s,j["title"],j.get("location",{}).get("name",""),j["absolute_url"],j.get("first_published") or j.get("updated_at","")))
    d=get(f"https://api.ashbyhq.com/posting-api/job-board/{s}")
    if d and d.get("jobs"):
        for j in d["jobs"]:
            if TERMS.search(j["title"]):
                loc=j.get("location","")+(" | remote" if j.get("isRemote") else "")+" | "+";".join(x.get("location","") for x in j.get("secondaryLocations",[]))
                out.append(("ashby",s,j["title"],loc,j["jobUrl"],j.get("publishedAt","")))
    d=get(f"https://api.lever.co/v0/postings/{s}?mode=json")
    if isinstance(d,list):
        for j in d:
            if TERMS.search(j["text"]):
                c=j.get("categories",{}); loc=c.get("location","")+" | "+";".join(c.get("allLocations",[]) or [])+" | "+j.get("workplaceType","")
                out.append(("lever",s,j["text"],loc,j["hostedUrl"],j.get("createdAt","")))
    return out
res=[]
with cf.ThreadPoolExecutor(24) as ex:
    for r in ex.map(scan, slugs): res+=r
IND = re.compile(r"india|bengaluru|bangalore|mumbai|delhi|gurgaon|gurugram|hyderabad|pune|chennai|noida|kolkata|apac|asia|anywhere|worldwide|global", re.I)
seen = set()
for src_, s, t, l, u, d in sorted(res, key=lambda x: (x[1], x[2])):
    if u in seen or not IND.search(l): continue
    seen.add(u); print(s, "|", t, "|", l[:100], "|", str(d)[:10], "|", u)
