"""Push a notebook to Kaggle through the proxy (token injected by the proxy). Usage: push.py <ipynb> <slug> <title> [machine]"""
import json, subprocess, sys
nb, slug, title = sys.argv[1], sys.argv[2], sys.argv[3]
machine = sys.argv[4] if len(sys.argv) > 4 else 'NvidiaL4'
body = {
    'slug': f'jannetakankshaekka/{slug}', 'newTitle': title, 'text': open(nb).read(),
    'language': 'python', 'kernelType': 'notebook', 'isPrivate': True,
    'enableGpu': True, 'enableTpu': False, 'enableInternet': False,
    'datasetDataSources': ['metric/gemma-4-developer-agent-wheelhouse', 'dmitriigluzdov/gemma-4-task-soundness-and-local-results'],
    'competitionDataSources': ['gemma-4-developer-agent'], 'kernelDataSources': [],
    'modelDataSources': ['google/gemma-4/Other/gemma-4-12b-it-qat-w4a16-ct/2'],
    'categoryIds': [],
    'dockerImage': 'gcr.io/kaggle-private-byod/python@sha256:37c64f7dd9c54116ecd1bcc88817c5469b88387388fade02bfa8bf3fc647d461',
}
if machine != 'none':
    body['machineShape'] = machine
open('push_body.json', 'w').write(json.dumps(body))
r = subprocess.run(['curl', '-sS', '-X', 'POST', 'https://www.kaggle.com/api/v1/kernels/push', '-H', 'Content-Type: application/json',
                    '--data-binary', '@push_body.json', '-w', '\nHTTP %{http_code}'], capture_output=True, text=True)
print(r.stdout[:1500], r.stderr[:500])
