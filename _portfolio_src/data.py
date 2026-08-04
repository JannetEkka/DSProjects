# ---------------------------------------------------------------------------
# CONTACT + FORM CONFIG  — the only things you need to edit to switch the form on
# ---------------------------------------------------------------------------
# WEB3FORMS_KEY: get a free key at https://web3forms.com — enter your email,
#   they send the access key to that inbox. Every submission then arrives there.
#   Free tier: 250 submissions/month. The key is PUBLIC by design (it is tied to
#   your email, it is not a password), so it is safe to commit.
#   While this is blank the form still renders but falls back to opening an
#   email instead of posting, so it can never silently swallow an enquiry.
#
# DISCORD: paste your invite or profile URL. Left blank = the button is not
#   rendered at all (no dead link).
CONTACT = dict(
    email="jannetekka96@gmail.com",
    linkedin="https://www.linkedin.com/in/jannet-akanksha-ekka-a18692122/",
    whatsapp="https://wa.me/919078802572",
    discord="",
    web3forms_key="",
)

# ---- verified link status ----
# 200 OK : workers.dev SMT, run.app SMT World, smt-mantle pages, all github repos (public via API)
# user-confirmed live: versecanvas.streamlit.app
# no repo exists: Smart Money Tracker -> left blank per instruction

GH = "https://github.com/JannetEkka/"

FLAGSHIP = dict(
    slug="smt", grants=True, cat="agents", title="Smart Money Trading (SMT)",
    sub="Explainable Multi-Agent Trading AI",
    meta="2026 – Present · Sole architect & engineer",
    badge="Patent pending · IN 202631090789",
    desc="A three-layer autonomous trading agent for 8 crypto perpetual-futures pairs — a quant base, a self-retuning learning loop, and an explanation layer that ships a plain-English &ldquo;why&rdquo; with every decision. Six specialist personas vote into a learned <em>Judge</em>; an Optuna optimiser and a regime-aware contextual bandit retune it on real outcomes, and a weekly refit only ships through a CPCV + Deflated-Sharpe + PBO + FDR overfitting gate.",
    stats=[("33K","lines of Python"),("153","modules"),("166","tests green"),("8","pairs live")],
    tags=["Multi-Agent Systems","Explainable AI","Optuna","BigQuery + Vector Search","Vertex AI","Cloud Run","Cloudflare Workers"],
    links=[("Live site","https://smt-weex-trading-bot.jannet-ekka.workers.dev/","live"),
           ("SMT World","https://smt-world-2gbcoyhuea-uc.a.run.app/","live"),
           ("Code","https://github.com/JannetEkka/smt-apac","code"),
           ("Press","https://www.weex.com/news/detail/how-smart-money-tracker-survived-live-ai-trading-at-weex-ai-hackathon-343641","doc")],
    note="Core repo private — the linked repo is the public explanatory layer.",
)

PROJECTS = [
 dict(slug="versecanvas", grants=True, cat="genai", title="VerseCanvas", sub="AI Poetry-to-Art Generator", meta="2025 · Personal project",
   desc="Turns a poem into original artwork through a multi-stage pipeline: semantic analysis with Gemini 2.0 &rarr; automated prompt engineering &rarr; image synthesis with Imagen 3.0 on Vertex AI &rarr; hybrid editing and text overlay. Six languages, six art styles, tunable mood intensity.",
   tags=["Gemini 2.0","Imagen 3.0","Vertex AI","Streamlit"],
   links=[("Live demo","https://versecanvas.streamlit.app/","live"),("Code",GH+"versecanvas","code")]),

 dict(slug="smartdesk", cat="agents", title="SmartDesk", sub="Multi-Agent Productivity Assistant", meta="2026 · Gen AI Academy APAC — Cohort 1 Hackathon",
   desc="A root ADK orchestrator routing to specialised sub-agents — InboxAgent (Gmail over MCP), PlannerAgent (Calendar over MCP), DataAgent (AlloyDB vector search as a personal CRM) — with a SequentialAgent synthesising the reply. Containerised on Cloud Run.",
   tags=["Google ADK","MCP","AlloyDB + pgvector","Gemini 2.5 Flash","Cloud Run"],
   links=[("Code",GH+"smartdesk","code")]),

 dict(slug="locintel", cat="agents", title="Location Intelligence Agent", sub="MCP over BigQuery + Google Maps", meta="2026 · Google Cloud Gen AI Academy APAC",
   desc="An ADK agent wired to two remote MCP servers — BigQuery for demographic, pricing and sales data, Google Maps for location analysis. Scores zip codes by demographics and foot traffic, flags underperforming stores, projects next-month revenue and measures competitor density.",
   tags=["MCP Servers","BigQuery","Google Maps API","ADK"],
   links=[("Code",GH+"bakery-growth-agent","code")]),

 dict(slug="smtracker", cat="agents", title="Smart Money Tracker", sub="Multi-Agent Blockchain Analytics", meta="2024 · Winner — Best DeFi Application",
   award="OpenServ × Hack2skill",
   desc="Multi-agent whale tracking across Ethereum, BNB Smart Chain and Polygon using the OpenServ SDK, with Alchemy webhooks driving sub-second transaction monitoring. Confidence-scored detection of accumulation, distribution and coordinated movements, with automated exchange-wallet exclusion.",
   tags=["OpenServ SDK","Alchemy","Moralis","Cloud Run","pgvector"],
   links=[]),

 dict(slug="smtchains", grants=True, cat="agents", title="SMT Chain Adapters", sub="Mantle &amp; BNB hackathon builds", meta="2026 · Hackathon adapters",
   desc="Thin per-chain adapters that import the SMT brain and expose it to a specific ecosystem — keeping one shared decision engine behind platform-specific front ends rather than forking the strategy code.",
   tags=["Mantle","BNB Chain","Python"],
   links=[("Live","https://jannetekka.github.io/smt-mantle/","live"),("Mantle",GH+"smt-mantle","code"),("BNB",GH+"smt-bnb","code")]),

 dict(slug="autokorrekt", cat="genai", wide=True, title="AutoKorrekt", sub="AI Answer-Evaluation Platform for Teachers", meta="May 2024 – Jan 2025 · Lead Frontend Developer · EdTech startup MVP",
   desc="An evaluation platform that takes a teacher from sign-up to graded scripts: create a class, upload a student roster and question paper, bulk-upload scanned answer sheets, then track each student through OCR, AI evaluation and validation. I led the frontend and designed the ML data flow across S3, RDS and SageMaker &mdash; interactive PDF processing with coordinate-based text extraction over AWS Textract, a bilingual EN/DE feedback interface on Amazon Comprehend, and a per-student status pipeline that scaled to 1,000+ concurrent submissions.",
   tags=["React","Next.js","TypeScript","AWS Textract","Amazon Comprehend","SageMaker","Django"],
   shots=[("assets/autokorrekt/Index_page_signup.png","Teacher sign-up"),
          ("assets/autokorrekt/Index_pg_signin.png","Sign in"),
          ("assets/autokorrekt/add_Test.png","Create a class — student roster (CSV) + question-paper upload"),
          ("assets/autokorrekt/students.png","Per-student evaluation pipeline &amp; bulk answer-sheet upload")],
   links=[]),

 dict(slug="asha", cat="genai", title="Asha Chatbot", sub="JobsForHer Foundation", meta="2025 · Hackathon project",
   desc="A context-aware chatbot surfacing job listings, community events and mentorship programmes, and handling FAQs — built to support women returning to and advancing in the workforce.",
   tags=["Conversational AI","NLP","Python"], links=[("Code",GH+"asha-chatbot","code")]),

 dict(slug="medtest", cat="genai", title="MedTestAI", sub="HIPAA-Compliant Healthcare AI", meta="2025 – 2026 · Personal project",
   desc="A healthcare AI project built around HIPAA compliance constraints — handling protected health information under the access, auditing and data-handling rules regulated medical software requires.",
   tags=["Healthcare AI","HIPAA","JavaScript"], links=[("Code",GH+"MedTestAI","code")]),

 dict(slug="webqna", cat="genai", title="WebContentQnA", sub="Ask questions about any page", meta="2025 · Personal project",
   desc="Paste a set of URLs and ask questions about their contents; the app retrieves and answers from page text using a DistilBERT question-answering model.",
   tags=["DistilBERT","Question Answering","Transformers"], links=[("Code",GH+"WebContentQnA","code")]),

 dict(slug="capstone", cat="cv", title="Automotive Surveillance System", sub="Capstone — Computer Vision", meta="Dec 2024 – Jan 2025 · Great Learning",
   desc="Vehicle make/model/year classification reaching 69.2% accuracy with ResNet50, plus Fast R-CNN object detection across 16,185 images spanning 196 classes.",
   tags=["ResNet50","Fast R-CNN","TensorFlow","OpenCV"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/Automotive_Surveillance_System_Capstone","code")]),

 dict(slug="botanical", cat="cv", title="MultiModel Botanical Classification", sub="Plant species recognition", meta="Jun – Jul 2024 · UT Austin McCombs",
   desc="83.79% accuracy with a CNN for automated plant-species classification across 4,750+ seedling images, benchmarked against Random Forest and SVM baselines.",
   tags=["CNN","Transfer Learning","Computer Vision"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/MultiModel_Botanical_Classification_CV","code")]),

 dict(slug="signal", cat="cv", title="Signal &amp; SVHN Classification", sub="Neural networks, two domains", meta="Aug – Sep 2024 · UT Austin McCombs",
   desc="Neural networks reaching 90% accuracy on signal-quality prediction and 85% on SVHN street-number digit recognition, with regularisation and a visualisation suite for real-world noise.",
   tags=["Deep Learning","Keras","Regularisation"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/Signal_Classification_Digit_Recognition_NNDL","code")]),

 dict(slug="churn", cat="ml", title="Customer Churn Prediction", sub="Telecom retention", meta="Oct – Nov 2024 · UT Austin McCombs",
   desc="81.48% accuracy identifying customers likely to cancel, comparing Bagging, AdaBoost and Gradient Boosting, and converting the model into a prioritised retention strategy.",
   tags=["Ensemble Methods","scikit-learn","Business Strategy"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/Customer_Churn_Prediction_ET","code")]),

 dict(slug="semi", cat="ml", title="Semiconductor Yield Prediction", sub="591 sensor signals", meta="Sep – Oct 2024 · UT Austin McCombs",
   desc="Pass/fail yield prediction from manufacturing sensor data, using feature selection and SMOTE to cut 591 signals down to the ones that actually carry information about defects.",
   tags=["Feature Selection","SMOTE","Quality Control"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/Semiconductor_Manufacturing_Prediction_FMT","code")]),

 dict(slug="adview", cat="ml", title="YouTube AdView Analytics", sub="Ad-revenue prediction", meta="Jul – Aug 2024 · Internship Studio",
   desc="Random Forest regression predicting advertisement views from engagement metrics across 15,000+ videos, packaged for integration with business dashboards.",
   tags=["Random Forest","pandas","Predictive Analytics"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/YouTube_AdView_Analytics_ML","code")]),

 dict(slug="nbfc", cat="ml", title="NBFC Loan Default Prediction", sub="Credit risk", meta="Feb 2025 · Great Learning Hackathon",
   desc="A classification model predicting whether a client will default on loan repayment, built against a non-banking financial company dataset under hackathon time constraints.",
   tags=["Classification","Risk Modelling"], links=[("Code",GH+"NBFC-Loan-Default","code")]),

 dict(slug="usl", cat="ml", title="Automobile Analysis &amp; Classification", sub="K-Means + PCA-enhanced SVM", meta="Apr – May 2024 · UT Austin McCombs",
   desc="Vehicle segmentation with K-Means clustering and classification with a PCA-enhanced SVM, analysing MPG, displacement, horsepower and weight across 102 features.",
   tags=["K-Means","PCA","SVM"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/Automobile_Analysis_Classification_USL","code")]),

 dict(slug="sentiment", cat="ml", title="Stock Market Sentiment Analysis", sub="Financial news NLP", meta="Nov – Dec 2024 · UT Austin McCombs",
   desc="An ensemble sentiment classifier over financial news using Word2Vec, GloVe and SBERT embeddings, with weekly market summaries generated by a Mistral-7B LLM.",
   tags=["NLP","SBERT","Mistral-7B","Transformers"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/Stock_Market_Sentiment_Analysis_NLP","code")]),

 dict(slug="newwheels", cat="analytics", title="New-Wheels Performance Analytics", sub="SQL business intelligence", meta="Jul – Aug 2024 · UT Austin McCombs",
   desc="Customer behaviour and sales analysis for a vehicle-resale business covering 994 customers and $1.25B revenue, with a KPI tracking system identifying key markets.",
   tags=["SQL","Business Intelligence","KPI Design"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/New_Wheels_Performance_Analytics_SQL","code")]),

 dict(slug="bizanalytics", cat="analytics", title="Business Analytics Portfolio", sub="Pricing + HR attrition", meta="May – Jun 2024 · UT Austin McCombs",
   desc="Two supervised-learning studies: 86% accuracy on used-car price prediction for Cars4U, and 84% on employee attrition for a healthcare HR dataset.",
   tags=["Regression","HR Analytics","scikit-learn"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/Business_Analytics_Portfolio_SL","code")]),

 dict(slug="ecom", cat="analytics", title="E-commerce Behaviour Dashboard", sub="User &amp; sales insight", meta="2024 – 2025 · Personal project",
   desc="A dashboard surfacing user-behaviour and sales-trend insights for an e-commerce site, turning raw event and transaction data into merchandising decisions.",
   tags=["Dashboards","Analytics","Python"], links=[("Code",GH+"ecommerce-analysis","code")]),

 dict(slug="stats", cat="analytics", title="Applied Statistics &amp; Hypothesis Testing", sub="Statistical foundations", meta="May – Jun 2024 · UT Austin McCombs",
   desc="Hypothesis testing on car-purchase behaviour, manufacturing quality control identifying a 5% defect rate, and probability models for weekly sales forecasting.",
   tags=["Hypothesis Testing","SciPy","Probability"],
   links=[("Code","https://github.com/JannetEkka/DSProjects/tree/main/Applied_Statistics_Project","code")]),

 dict(slug="yatra", cat="automation", title="Yatra Test Automation Framework", sub="Hybrid Selenium framework", meta="2024 · Personal project",
   desc="A hybrid data-driven Selenium framework with Page Object Model structure, external test data, cross-browser runs on Edge/Chrome/Firefox, HTML reporting and failure screenshots — wired into Jenkins.",
   tags=["Selenium","PyTest","POM","Jenkins"], links=[("Code",GH+"python-automation","code")]),

 dict(slug="50days", cat="automation", title="50 Days of Python", sub="A challenge a day", meta="2025 · Completed challenge",
   desc="All fifty exercises from Benjamin Bennett Alexander&rsquo;s challenge — data structures, file I/O, CSV and JSON handling, SQLite, and a Flask web app as the day-50 capstone.",
   tags=["Python","Flask","SQLite"], links=[("Code",GH+"50-days-of-python","code")]),
]

CATS = [("all","All work"),("agents","AI Agents"),("genai","Generative AI"),
        ("cv","Computer Vision"),("ml","Machine Learning"),("analytics","Analytics"),("automation","Automation")]
