# Gemini pass (run in a session that has GEMINI_API_KEY)

```bash
git clone --depth 1 https://github.com/interviewstreet/hackerrank-orchestrate-october26.git /tmp/hro
cp -r hackathons/hackerrank-orchestrate-oct26/code /tmp/hro/
cd /tmp/hro && pip install -q google-genai rapidocr-onnxruntime pdfplumber
python3 code/main.py                # uses GEMINI_API_KEY -> fills code/cache/intent.json + media_text.json
cp code/cache/*.json output.usage.json "$OLDPWD/hackathons/hackerrank-orchestrate-oct26/gemini_results/"
```
