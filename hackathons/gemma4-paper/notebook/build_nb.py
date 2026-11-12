"""Assemble the Kaggle notebook from the starter's cells and our study code. Usage: build_nb.py <starter.ipynb> <out.ipynb> <cfg-overrides-json>"""
import json
import sys
from pathlib import Path

here = Path(__file__).parent
starter = json.loads(Path(sys.argv[1]).read_text())
overrides = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}

install_cell = ''.join(starter['cells'][2]['source'])  # the host's environment + wheelhouse cell, unchanged

cfg = {
    'model_name': 'gemma-4-12b-it-qat-w4a16-ct',
    'data_dir': '/kaggle/input/competitions/gemma-4-developer-agent',
    'soundness_csv': '/kaggle/input/datasets/dmitriigluzdov/gemma-4-task-soundness-and-local-results/task_soundness.csv',
    'out_dir': '/kaggle/working/study',
    'base_url': 'http://127.0.0.1:8000/v1',
    # fixed before the run (design brief, section 6)
    'max_turns': 30,
    'time_limit_s': 300,
    'cmd_timeout_s': 60,
    'output_cut': 4000,
    'context_tokens': 32768,
    'max_tokens': 8192,
    'thinking_budget': 4096,
    'temperature': 0.2,
    'top_p': 0.95,
    'seeds': [0],
    # how much to run
    'n_tasks': 10,
    'workers': 6,
    'run_deadline_s': 3 * 3600,
    'control_tasks': 10,
    'save_transcripts': False,
}
cfg.update(overrides)

cfg_cell = (
    '# Study settings. The budget was fixed before the run and is the same in both arms.\n'
    'CFG = ' + json.dumps(cfg, indent=4).replace('false', 'False').replace('true', 'True') + '\n'
    'import glob as _g\n'
    "if not os.path.exists(CFG['soundness_csv']):\n"
    "    _c = _g.glob('/kaggle/input/**/task_soundness.csv', recursive=True)\n"
    "    assert _c, 'task_soundness.csv not found: attach dmitriigluzdov/gemma-4-task-soundness-and-local-results'\n"
    "    CFG['soundness_csv'] = _c[0]\n"
    'print(CFG)\n'
)

plan_cell = '''# Task list (fixed rule, independent of results), prompt check, and the checker controls.
ALL_VALID = planned_tasks()
RUN_TASKS = ALL_VALID[: CFG['n_tasks']]
print(f"Valid public tasks: {len(ALL_VALID)}. Planned for this run: {len(RUN_TASKS)} (first by sha256 of the task id).")
print('Planned task ids:', [t.instance_id for t in RUN_TASKS])

PROMPT_CHECK = prompt_check()
print('Check (c), prompts differ only in the format paragraph:', PROMPT_CHECK)
print((OUT_DIR / 'prompt_diff.txt').read_text())
assert PROMPT_CHECK['identical_outside_format_paragraph']

# Check (a) runs in the background while the model server loads.
import threading as _th
CONTROL_ROWS = []
def _controls():
    CONTROL_ROWS.extend(run_controls(RUN_TASKS[: CFG['control_tasks']], workers=3))
_control_thread = _th.Thread(target=_controls, daemon=True)
if CFG['control_tasks'] > 0:
    _control_thread.start()
'''

server_cell = '''# Model server: same settings as the host's starter notebook (no LoRA adapters are used in this study).
import torch
from adk_submission import VllmConfig, VllmServer

MODEL_VLLM_EXTRA_ARGS = {
    'gemma-4-12b-it-qat-w4a16-ct': (
        '--hf-overrides',
        '{"architectures": ["Gemma4ForCausalLM"], "model_type": "gemma4"}',
    ),
}
MODEL_PATH = Path(f"/kaggle/input/models/google/gemma-4/other/{CFG['model_name']}/2")
assert MODEL_PATH.exists(), f'Model weights not found at {MODEL_PATH}'

gpu_count = torch.cuda.device_count() if torch.cuda.is_available() else 1
tp_size = 4 if gpu_count >= 4 else (2 if gpu_count >= 2 else 1)
print('GPUs:', [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())], 'tp =', tp_size)

vllm_cfg = VllmConfig(
    model=str(MODEL_PATH),
    port=8000,
    host='127.0.0.1',
    tool_call_parser='gemma4',
    reasoning_parser='gemma4',
    max_model_len=CFG['context_tokens'],
    dtype='bfloat16' if (torch.cuda.is_available() and torch.cuda.is_bf16_supported()) else 'auto',
    gpu_memory_utilization=0.90,
    enable_auto_tool_choice=True,
    enable_lora=False,
    max_loras=1,
    max_lora_rank=128,
    scheduler_reserve_full_isl=False,
    tensor_parallel_size=tp_size,
    startup_timeout=60 * 20,
    extra_args=MODEL_VLLM_EXTRA_ARGS.get(CFG['model_name'], ()),
)
server_instance = VllmServer(vllm_cfg)
_t = time.perf_counter()
server_instance.start()
print(f'vLLM server started on {server_instance.base_url} in {time.perf_counter() - _t:.0f}s; serving {model_id()}')
'''

smoke_cell = '''# One request per arm on a toy prompt (no competition text), to show what each format looks like on the wire.
for _arm in ARMS:
    _m = [{'role': 'system', 'content': system_prompt(_arm, 'example/repo')},
          {'role': 'user', 'content': 'Bug report:\\nThis is a connection test, not a real bug. List the files in /workspace.'}]
    _r = chat(_m, _arm, seed=0, timeout=300)
    print(f'--- arm {_arm}: HTTP {_r.status_code}')
    _j = _r.json()
    if _r.status_code == 200:
        _msg = _j['choices'][0]['message']
        print(json.dumps({k: _msg.get(k) for k in ('content', 'reasoning', 'reasoning_content', 'tool_calls')}, indent=1)[:1500])
        print('finish_reason:', _j['choices'][0].get('finish_reason'), '| usage:', _j.get('usage'))
        print('read as:', read_action_json(_msg.get('tool_calls')) if _arm == 'json' else read_action_text(_msg.get('content') or ''))
    else:
        print(_r.text[:800])
'''

run_cell = '''# The run. Both arms of a task run side by side.
_t = time.perf_counter()
DONE, NOT_RUN = run_study(RUN_TASKS, CFG['seeds'], workers=CFG['workers'], deadline_s=CFG['run_deadline_s'])
print(f'Run finished in {(time.perf_counter() - _t) / 60:.1f} min. Rows: {len(DONE)}. Tasks not started: {len(NOT_RUN)}.')
'''

checks_cell = '''# Pilot checks (design brief, section 5).
if CFG['control_tasks'] > 0:
    _control_thread.join()
    import pandas as pd
    _c = pd.DataFrame(CONTROL_ROWS)
    display(_c)
    _ref = int((_c['reference_resolved'] == True).sum()); _emp = int((_c['empty_resolved'] == False).sum())
    print(f'Check (a): checker passes the reference patch on {_ref} of {len(_c)} tasks and fails the empty patch on {_emp} of {len(_c)}.')
_r = pd.read_csv(OUT_DIR / 'results.csv', keep_default_na=False)
_u = _r.pivot_table(index='task_id', columns='arm', values='usable_turns', aggfunc='min')
print(f"Check (b): tasks where each arm produced at least one usable action: json {(int((_u['json'] > 0).sum()))} of {len(_u)}, text {int((_u['text'] > 0).sum())} of {len(_u)}.")
print('Check (c):', PROMPT_CHECK)
print('Harness errors:', int((_r['harness_error'] != '').sum()))
if (OUT_DIR / 'harness_errors.log').exists():
    print((OUT_DIR / 'harness_errors.log').read_text()[:6000])
'''

stop_cell = '''server_instance.stop()
import shutil as _sh
_sh.rmtree(OUT_DIR / 'harness_results', ignore_errors=True)
print(sorted(p.name for p in OUT_DIR.iterdir()))
'''

intro = '''# Same model, same bugs, two formats

Does Gemma 4 fix more bugs when it writes each action as a plain-text `bash` block than when it writes it as a structured (JSON) tool call, with nothing else changed?

One small agent loop runs each of the competition's public bug-fix tasks twice: once per action format. The model file, server settings, system prompt (apart from one paragraph), budget and checker are the same. Workspaces and the patch checker are the host harness's own (`swegemma`). Tasks are the ones marked sound in `task_soundness.csv` from dmitriigluzdov's dataset *Gemma 4 Task Soundness and Local Results* (CC BY 4.0).

Outputs in `/kaggle/working/study`: `results.csv` (one row per task, arm, seed), `turns.jsonl` (one row per turn, counts only), `controls.csv`, `prompt_diff.txt`, `summary.json`. Task texts and transcripts are not written.
'''


def code(src):
    return {'cell_type': 'code', 'metadata': {}, 'execution_count': None, 'outputs': [], 'source': src}


def md(src):
    return {'cell_type': 'markdown', 'metadata': {}, 'source': src}


cells = [
    md(intro),
    md('## 1. Environment (the host starter\'s cell, unchanged)'),
    code(install_cell),
    md('## 2. Settings'),
    code('import json, time\n' + cfg_cell),
    md('## 3. The agent loop, the two formats, and the checker'),
    code((here / 'study_core.py').read_text()),
    md('## 4. Task list, prompt check, checker controls'),
    code(plan_cell),
    md('## 5. Model server'),
    code(server_cell),
    code(smoke_cell),
    md('## 6. Run'),
    code(run_cell),
    md('## 7. Checks'),
    code(checks_cell),
    md('## 8. Results'),
    code((here / 'analysis_cell.py').read_text()),
    code(stop_cell),
]
nb = {'cells': cells, 'metadata': starter['metadata'], 'nbformat': 4, 'nbformat_minor': 4}
Path(sys.argv[2]).write_text(json.dumps(nb, indent=1))
print('cells:', len(cells), 'bytes:', Path(sys.argv[2]).stat().st_size)
