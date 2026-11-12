# ---------------------------------------------------------------------------
# Study core: one small agent loop, two action formats.
# Everything except the format paragraph and the code that reads an action is
# shared between the two arms. Expects a dict CFG defined in an earlier cell.
# ---------------------------------------------------------------------------
import asyncio
import csv
import difflib
import hashlib
import json
import re
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests as _rq

from swegemma.config import EvalConfig
from swegemma.deduplication import resolve_task_snapshot_paths
from swegemma.harness.agent_runner import build_workspace_tree_command
from swegemma.harness.container_setup import (
    extract_snapshot,
    install_editable_package,
    install_test_dependencies,
    setup_baseline_commit,
    setup_container_wheels,
    setup_git_exclude,
    setup_workspace_test_config,
)
from swegemma.harness.verification import strip_protected_files_from_patch, verify_task
from swegemma.models import load_tasks
from swegemma.sandbox import SubprocessManager

ARMS = tuple(CFG.get('arms') or ('json', 'text'))
# 'text_stop' is the text format with one change in the code that reads it: the reply is cut as soon as the first
# complete ```bash block has arrived (added after the pilot; see the Writeup).
OUT_DIR = Path(CFG['out_dir'])
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------- prompts -------------------------------------
SHARED_PROMPT = """You are a software engineer fixing a bug in the Python repository {repo}. The repository is checked out at /workspace and you work on it through shell commands.

How this works:
- Each turn you take exactly one action: run one shell command, or submit.
- After a command you are shown its exit code and its output. Long output is cut to {cut} characters.
- Every command starts in /workspace in a fresh shell, so `cd` and shell variables do not carry over to the next command.
- There is no network. All dependencies are already installed. Do not run pip install.
- Read, search, edit and test through shell commands, for example grep, sed -n, cat, python3, or pytest on a single test file.
- Fix the library code. Changes to test files are thrown away.
- You have at most {max_turns} turns and {minutes} minutes. A single command is stopped after {cmd_timeout} seconds.
- When the fix is in place, submit. What counts is the state of /workspace when you submit or when the budget runs out.
"""

FORMAT_PARAGRAPH = {
    'json': (
        'How to write an action:\n'
        'Use the provided tools. To run a shell command, call the tool `run_command` with one string argument `command`. '
        'To finish, call the tool `submit` with no arguments. Make exactly one tool call per turn.\n'
    ),
    'text': (
        'How to write an action:\n'
        'Write one fenced code block that starts with ```bash and ends with ```, with the shell command inside it. '
        'To finish, write a ```bash block that contains only the word submit. Write exactly one such block per turn.\n'
    ),
}

TOOLS = [
    {
        'type': 'function',
        'function': {
            'name': 'run_command',
            'description': 'Run one shell command in /workspace and return its exit code and output.',
            'parameters': {
                'type': 'object',
                'properties': {'command': {'type': 'string', 'description': 'The shell command to run.'}},
                'required': ['command'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'submit',
            'description': 'Finish the task. The current state of /workspace is your answer.',
            'parameters': {'type': 'object', 'properties': {}},
        },
    },
]

CORRECTION = (
    'Your last reply did not contain a usable action. '
    'Reply with exactly one action in the required format.'
)
ONLY_FIRST_NOTE = '(Your reply contained more than one action. Only the first one was run.)\n'
ELIDED = '[earlier output removed to save space]'


def system_prompt(arm: str, repo: str) -> str:
    shared = SHARED_PROMPT.format(
        repo=repo,
        cut=CFG['output_cut'],
        max_turns=CFG['max_turns'],
        minutes=CFG['time_limit_s'] // 60,
        cmd_timeout=CFG['cmd_timeout_s'],
    )
    return shared + '\n' + FORMAT_PARAGRAPH['json' if arm == 'json' else 'text']


def user_prompt(task, tree: str) -> str:
    parts = [f'Bug report:\n{task.problem_statement.strip()}\n']
    hints = (getattr(task, 'hints_text', '') or '').strip()
    if hints:
        parts.append(f'Hints:\n{hints}\n')
    if tree:
        parts.append('Layout of /workspace (up to 3 levels):\n```\n' + tree + '\n```\n')
    return '\n'.join(parts)


def prompt_check() -> dict:
    """Pilot check (c): the two prompts differ only in the format paragraph."""
    a, b = system_prompt('json', 'REPO'), system_prompt('text', 'REPO')
    diff = list(difflib.unified_diff(a.splitlines(), b.splitlines(), 'system_prompt[json]', 'system_prompt[text]', lineterm='', n=0))
    (OUT_DIR / 'prompt_diff.txt').write_text('\n'.join(diff) + '\n', encoding='utf-8')
    a_rest = a.replace(FORMAT_PARAGRAPH['json'], '<FORMAT>')
    b_rest = b.replace(FORMAT_PARAGRAPH['text'], '<FORMAT>')
    changed = [l for l in diff if l[:1] in '+-' and not l.startswith(('+++', '---'))]
    return {
        'identical_outside_format_paragraph': a_rest == b_rest and a_rest.count('<FORMAT>') == 1,
        'changed_lines': len(changed),
        'user_prompt_shared': True,  # one function, no arm argument
        'correction_shared': True,  # one constant
    }


# ----------------------------- reading an action ---------------------------
BASH_BLOCK = re.compile(r'```bash[ \t]*\r?\n(.*?)```', re.DOTALL)


def read_action_text(content: str):
    """Return (kind, command, n_actions, reason). kind is 'run', 'submit' or None."""
    blocks = BASH_BLOCK.findall(content or '')
    if not blocks:
        return None, None, 0, 'no_bash_block'
    first = blocks[0].strip()
    if not first:
        return None, None, len(blocks), 'empty_block'
    if first == 'submit':
        return 'submit', None, len(blocks), ''
    return 'run', first, len(blocks), ''


def read_action_json(tool_calls):
    """Return (kind, command, n_actions, reason) from the server's parsed tool calls."""
    if not tool_calls:
        return None, None, 0, 'no_tool_call'
    fn = (tool_calls[0] or {}).get('function') or {}
    name = fn.get('name')
    if name not in ('run_command', 'submit'):
        return None, None, len(tool_calls), 'unknown_tool'
    raw = fn.get('arguments')
    try:
        args = json.loads(raw) if isinstance(raw, str) and raw.strip() else (raw or {})
    except Exception:
        return None, None, len(tool_calls), 'arguments_not_json'
    if not isinstance(args, dict):
        return None, None, len(tool_calls), 'arguments_not_object'
    if name == 'submit':
        return 'submit', None, len(tool_calls), ''
    cmd = args.get('command')
    if not isinstance(cmd, str) or not cmd.strip():
        return None, None, len(tool_calls), 'missing_command'
    return 'run', cmd, len(tool_calls), ''


# ----------------------------- model call ----------------------------------
_MODEL_ID = None


def model_id() -> str:
    global _MODEL_ID
    if _MODEL_ID is None:
        r = _rq.get(CFG['base_url'] + '/models', timeout=30)
        _MODEL_ID = r.json()['data'][0]['id']
    return _MODEL_ID


def chat(messages, arm: str, seed: int, timeout: float):
    body = {
        'model': model_id(),
        'messages': messages,
        'temperature': CFG['temperature'],
        'top_p': CFG['top_p'],
        'max_tokens': CFG['max_tokens'],
        'seed': seed,
        'chat_template_kwargs': {'enable_thinking': True},
        'thinking_token_budget': CFG['thinking_budget'],
    }
    if arm == 'json':
        body['tools'] = TOOLS
        body['tool_choice'] = 'auto'
    if arm != 'text_stop':
        return _rq.post(CFG['base_url'] + '/chat/completions', json=body, timeout=timeout)
    return _StreamedReply(body, timeout)


class _StreamedReply:
    """Same request as the text arm, read as a stream and closed once the first complete ```bash block has arrived.
    Presents the same fields as a normal reply (status_code, text, json())."""

    def __init__(self, body, timeout):
        body = dict(body, stream=True, stream_options={'include_usage': True, 'continuous_usage_stats': True})
        deadline = time.perf_counter() + timeout
        content, reasoning, finish, usage, cut = '', '', None, {}, False
        r = _rq.post(CFG['base_url'] + '/chat/completions', json=body, timeout=(10, 120), stream=True)
        self.status_code = r.status_code
        self.text = ''
        if r.status_code != 200:
            self.text = r.text
            r.close()
            return
        try:
            for line in r.iter_lines():
                if time.perf_counter() > deadline:
                    raise _rq.exceptions.Timeout('time limit reached while streaming')
                if not line or not line.startswith(b'data:'):
                    continue
                payload = line[5:].strip()
                if payload == b'[DONE]':
                    break
                chunk = json.loads(payload)
                if chunk.get('usage'):
                    usage = chunk['usage']
                for ch in chunk.get('choices') or []:
                    delta = ch.get('delta') or {}
                    content += delta.get('content') or ''
                    reasoning += delta.get('reasoning') or delta.get('reasoning_content') or ''
                    if ch.get('finish_reason'):
                        finish = ch['finish_reason']
                if BASH_BLOCK.search(content):
                    cut = finish is None
                    break
        finally:
            r.close()
        if cut:
            finish = 'cut_after_first_block'
        self._data = {'choices': [{'message': {'content': content, 'reasoning': reasoning, 'tool_calls': []}, 'finish_reason': finish or ''}], 'usage': usage}

    def json(self):
        return self._data


def cut_output(text: str) -> str:
    n = CFG['output_cut']
    if len(text) <= n:
        return text
    head, tail = int(n * 0.6), n - int(n * 0.6)
    return text[:head] + f'\n[... {len(text) - n} characters cut ...]\n' + text[-tail:]


def est_tokens(messages) -> int:
    chars = 0
    for m in messages:
        chars += len(m.get('content') or '')
        for tc in m.get('tool_calls') or []:
            chars += len(json.dumps(tc))
    return chars // 3


def elide_oldest(messages) -> bool:
    """Replace the oldest command output still in the history with a stub. Same rule in both arms."""
    for m in messages[2:]:
        if m.get('_obs') and m['content'] != ELIDED:
            m['content'] = ELIDED
            return True
    return False


def wire(messages):
    return [{k: v for k, v in m.items() if not k.startswith('_')} for m in messages]


COMMAND_HEAD = re.compile(r'^\s*(?:cd\s+\S+\s*(?:&&|;)\s*)?([A-Za-z0-9_./-]+)')


# ----------------------------- sandbox helpers -----------------------------
_EVAL_CFG = EvalConfig(
    tasks_path=Path(CFG['data_dir']) / 'tasks.jsonl',
    snapshots_dir=Path(CFG['data_dir']) / 'snapshots',
    results_dir=OUT_DIR / 'harness_results',
    submission_dir=OUT_DIR / 'no_submission',
    models=None,
    sandbox='subprocess',
    timeout_seconds=CFG['cmd_timeout_s'],
    verification_timeout_seconds=300,
    wheels_dir=Path(CFG['data_dir']) / 'wheels',
    verbose=False,
)
SANDBOX = SubprocessManager(timeout_seconds=300)


def build_workspace(task):
    """Fresh workspace from the task's snapshot, with the same steps the host harness runs before its agent."""
    snap, base_snap, patch_path = resolve_task_snapshot_paths(_EVAL_CFG.snapshots_dir, task.instance_id, task.repo)
    if not snap.exists():
        raise FileNotFoundError(f'snapshot missing for {task.instance_id}')
    sid = SANDBOX.start()
    setup_container_wheels(SANDBOX, sid, _EVAL_CFG)
    extract_snapshot(SANDBOX, sid, snap, patch_path=patch_path, base_snapshot_path=base_snap)
    setup_git_exclude(SANDBOX, sid)
    install_editable_package(SANDBOX, sid)
    install_test_dependencies(SANDBOX, sid, task.repo, config=_EVAL_CFG)
    setup_workspace_test_config(SANDBOX, sid, repo=task.repo)
    setup_baseline_commit(SANDBOX, sid, 'baseline')
    return sid


def current_patch(sid, task) -> str:
    """The workspace diff, taken and stripped of test files the way the host harness does it."""
    SANDBOX.exec(sid, 'cd /workspace && git add -N .')
    res = SANDBOX.exec(sid, 'cd /workspace && (git diff --binary _swegemma_baseline 2>/dev/null || git diff --binary HEAD)')
    if res.exit_code != 0:
        raise RuntimeError(f'git diff failed: {res.stderr[:300]}')
    diff = res.stdout or ''
    if not diff.strip():
        return ''
    return strip_protected_files_from_patch(diff, extra_protected_paths=list(task.test_files or ()))


def check_patch(task, patch: str):
    """The competition's checker (swegemma.verify_task) on a patch, in a clean workspace."""
    snap, base_snap, patch_path = resolve_task_snapshot_paths(_EVAL_CFG.snapshots_dir, task.instance_id, task.repo)
    t0 = time.perf_counter()
    res = asyncio.run(
        verify_task(
            SANDBOX, _EVAL_CFG, task, snap,
            base_snapshot_path=base_snap, patch_path=patch_path,
            agent_patch=patch, agent_error=None, trace=None, start_time=t0,
        )
    )
    return bool(res.resolved), int(res.test_exit_code), (res.error or ''), time.perf_counter() - t0


# ----------------------------- one run --------------------------------------
_write_lock = threading.Lock()
RESULT_FIELDS = [
    'task_id', 'repo', 'arm', 'seed', 'model', 'resolved', 'failure_type', 'stop_reason',
    'turns', 'usable_turns', 'malformed_turns', 'extra_action_turns', 'commands_run',
    'agent_seconds', 'llm_seconds', 'cmd_seconds', 'setup_seconds', 'verify_seconds',
    'prompt_tokens', 'completion_tokens', 'elided_outputs',
    'patch_chars', 'patch_files', 'test_exit_code', 'checker_error', 'harness_error',
]


def failure_type(row) -> str:
    """Fixed rules over the logs, in this order."""
    if row['harness_error']:
        return 'harness_error'
    if row['resolved']:
        return ''
    if row['patch_chars'] == 0:
        return 'no_patch'
    if row['turns'] and row['malformed_turns'] * 2 >= row['turns']:
        return 'stuck_on_format'
    if row['stop_reason'] != 'submit':
        return 'out_of_budget_with_patch'
    return 'submitted_tests_fail'


def run_one(task, arm: str, seed: int) -> dict:
    row = {k: '' for k in RESULT_FIELDS}
    row.update(task_id=task.instance_id, repo=task.repo, arm=arm, seed=seed, model=CFG['model_name'],
               resolved=False, stop_reason='', turns=0, usable_turns=0, malformed_turns=0,
               extra_action_turns=0, commands_run=0, agent_seconds=0.0, llm_seconds=0.0, cmd_seconds=0.0,
               setup_seconds=0.0, verify_seconds=0.0, prompt_tokens=0, completion_tokens=0,
               elided_outputs=0, patch_chars=0, patch_files=0, test_exit_code='', checker_error='', harness_error='')
    turn_rows, transcript = [], []
    sid = None
    try:
        t_setup = time.perf_counter()
        sid = build_workspace(task)
        ws_real = str(SANDBOX.sandboxes[sid]['workspace'])
        tree_res = SANDBOX.exec(sid, build_workspace_tree_command())
        tree = tree_res.stdout.strip() if tree_res.exit_code == 0 else ''
        row['setup_seconds'] = round(time.perf_counter() - t_setup, 1)

        messages = [
            {'role': 'system', 'content': system_prompt(arm, task.repo)},
            {'role': 'user', 'content': user_prompt(task, tree)},
        ]
        prompt_budget = CFG['context_tokens'] - CFG['max_tokens'] - 512
        t0 = time.perf_counter()
        stop = ''
        last_diff_sig = ''
        while not stop:
            if row['turns'] >= CFG['max_turns']:
                stop = 'turn_limit'
                break
            remaining = CFG['time_limit_s'] - (time.perf_counter() - t0)
            if remaining <= 0:
                stop = 'time_limit'
                break
            while est_tokens(messages) > prompt_budget and elide_oldest(messages):
                row['elided_outputs'] += 1

            # ---- the model chooses the next action -------------------------
            t_llm = time.perf_counter()
            resp, context_retries = None, 0
            while True:
                try:
                    resp = chat(wire(messages), arm, seed, timeout=remaining + 2)
                except _rq.exceptions.Timeout:
                    stop = 'time_limit'
                    break
                if resp.status_code == 400 and 'context' in resp.text.lower() and context_retries < 8 and elide_oldest(messages):
                    context_retries += 1
                    row['elided_outputs'] += 1
                    continue
                break
            if stop:
                break
            llm_s = time.perf_counter() - t_llm
            if resp.status_code == 400 and 'context' in resp.text.lower():
                stop = 'context_limit'
                break
            if resp.status_code != 200:
                raise RuntimeError(f'model server returned {resp.status_code}: {resp.text[:300]}')
            data = resp.json()
            choice = data['choices'][0]
            msg = choice.get('message') or {}
            content = msg.get('content') or ''
            reasoning = msg.get('reasoning') or msg.get('reasoning_content') or ''
            tool_calls = msg.get('tool_calls') or []
            usage = data.get('usage') or {}
            row['llm_seconds'] += llm_s
            row['prompt_tokens'] += int(usage.get('prompt_tokens') or 0)
            row['completion_tokens'] += int(usage.get('completion_tokens') or 0)
            if time.perf_counter() - t0 > CFG['time_limit_s']:
                stop = 'time_limit'  # the reply arrived after the time limit; it is not used
                break

            # ---- code decides whether the reply holds a usable action ------
            row['turns'] += 1
            if arm == 'json':
                kind, command, n_actions, reason = read_action_json(tool_calls)
            else:
                kind, command, n_actions, reason = read_action_text(content)
            if kind is None and choice.get('finish_reason') == 'length':
                reason = 'cut_off_at_max_tokens'
            trow = {
                'task_id': task.instance_id, 'arm': arm, 'seed': seed, 'turn': row['turns'],
                'usable': kind is not None, 'malformed_reason': reason, 'action': kind or '',
                'actions_in_reply': n_actions, 'finish_reason': choice.get('finish_reason') or '',
                'prompt_tokens': int(usage.get('prompt_tokens') or 0),
                'completion_tokens': int(usage.get('completion_tokens') or 0),
                'reasoning_chars': len(reasoning), 'content_chars': len(content),
                'markup_in_content': bool(re.search(r'<\|?tool_call|<tool_call\|?>|"name"\s*:\s*"(run_command|submit)"', content)),
                'llm_seconds': round(llm_s, 2), 'command_head': '', 'command_chars': 0,
                'cmd_seconds': '', 'exit_code': '', 'timed_out': '', 'output_chars': '', 'workspace_changed': '',
            }
            tr = {'turn': row['turns'], 'reasoning': reasoning, 'content': content, 'tool_calls': tool_calls,
                  'finish_reason': choice.get('finish_reason'), 'usable': kind is not None, 'reason': reason}

            if kind is None:
                row['malformed_turns'] += 1
                shown = content
                if tool_calls:
                    shown = (content + '\n' if content else '') + json.dumps(tool_calls)
                messages.append({'role': 'assistant', 'content': shown or '[empty reply]'})
                messages.append({'role': 'user', 'content': CORRECTION})
            else:
                row['usable_turns'] += 1
                if n_actions > 1:
                    row['extra_action_turns'] += 1
                if arm == 'json':
                    call = dict(tool_calls[0])
                    call.setdefault('id', f'call_{row["turns"]}')
                    call.setdefault('type', 'function')
                    messages.append({'role': 'assistant', 'content': content, 'tool_calls': [call]})
                else:
                    messages.append({'role': 'assistant', 'content': content})
                if kind == 'submit':
                    stop = 'submit'
                else:
                    remaining = CFG['time_limit_s'] - (time.perf_counter() - t0)
                    cmd_timeout = int(max(5, min(CFG['cmd_timeout_s'], remaining)))
                    t_cmd = time.perf_counter()
                    res = SANDBOX.exec(sid, command, timeout=cmd_timeout)
                    cmd_s = time.perf_counter() - t_cmd
                    row['cmd_seconds'] += cmd_s
                    row['commands_run'] += 1
                    if res.timed_out:
                        obs = f'The command was stopped after {cmd_timeout} seconds.'
                    else:
                        out = (res.stdout or '')
                        if res.stderr:
                            out += ('\n' if out and not out.endswith('\n') else '') + '[stderr]\n' + res.stderr
                        out = out.replace(ws_real, '/workspace')
                        obs = f'exit code: {res.exit_code}\n' + cut_output(out)
                    if n_actions > 1:
                        obs = ONLY_FIRST_NOTE + obs
                    if arm == 'json':
                        messages.append({'role': 'tool', 'tool_call_id': call['id'], 'name': 'run_command', 'content': obs, '_obs': True})
                    else:
                        messages.append({'role': 'user', 'content': obs, '_obs': True})
                    sig_res = SANDBOX.exec(sid, 'cd /workspace && git status --porcelain | sha1sum; git diff HEAD | sha1sum')
                    sig = sig_res.stdout or ''
                    head = COMMAND_HEAD.match(command)
                    trow.update(command_head=(head.group(1).split('/')[-1] if head else ''), command_chars=len(command),
                                cmd_seconds=round(cmd_s, 2), exit_code=res.exit_code, timed_out=bool(res.timed_out),
                                output_chars=len(res.stdout or '') + len(res.stderr or ''),
                                workspace_changed=(sig != last_diff_sig and row['commands_run'] > 1) or (row['commands_run'] == 1 and 'da39a3ee' not in sig.split('\n')[0]))
                    last_diff_sig = sig
                    tr.update(command=command, observation=obs)
            turn_rows.append(trow)
            transcript.append(tr)
        row['stop_reason'] = stop
        row['agent_seconds'] = round(time.perf_counter() - t0, 1)

        # ---- the competition's checker decides whether the bug is fixed ----
        patch = current_patch(sid, task)
        row['patch_chars'] = len(patch)
        row['patch_files'] = patch.count('diff --git')
        SANDBOX.stop(sid)
        sid = None
        if patch.strip():
            ok, code, err, secs = check_patch(task, patch)
            row.update(resolved=ok, test_exit_code=code, checker_error=err[:200].replace('\n', ' '), verify_seconds=round(secs, 1))
        if CFG.get('save_transcripts'):
            tdir = OUT_DIR / 'transcripts'
            tdir.mkdir(exist_ok=True)
            (tdir / f'{task.instance_id}__{arm}__s{seed}.json').write_text(
                json.dumps({'row': row, 'turns': transcript, 'patch': patch}, indent=1, default=str), encoding='utf-8')
    except Exception as e:  # a crash in our own code is a harness_error row, never a silent "unfixed"
        row['harness_error'] = f'{type(e).__name__}: {str(e)[:300]}'.replace('\n', ' ')
        row['resolved'] = False
        with _write_lock:
            with open(OUT_DIR / 'harness_errors.log', 'a', encoding='utf-8') as f:
                f.write(f'--- {task.instance_id} {arm} s{seed}\n{traceback.format_exc()}\n')
    finally:
        if sid is not None:
            try:
                SANDBOX.stop(sid)
            except Exception:
                pass
    for k in ('llm_seconds', 'cmd_seconds'):
        row[k] = round(row[k], 1)
    row['failure_type'] = failure_type(row)
    with _write_lock:
        new = not (OUT_DIR / 'results.csv').exists()
        with open(OUT_DIR / 'results.csv', 'a', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=RESULT_FIELDS)
            if new:
                w.writeheader()
            w.writerow(row)
        with open(OUT_DIR / 'turns.jsonl', 'a', encoding='utf-8') as f:
            for t in turn_rows:
                f.write(json.dumps(t) + '\n')
    return row


# ----------------------------- task list ------------------------------------
def planned_tasks():
    """Valid tasks in a fixed order that does not depend on any result: sorted by sha256 of the task id."""
    all_tasks = {t.instance_id: t for t in load_tasks(Path(CFG['data_dir']) / 'tasks.jsonl')}
    with open(CFG['soundness_csv'], encoding='utf-8') as f:
        sound = [r['task_id'] for r in csv.DictReader(f) if r['sound'] == '1']
    ids = sorted((i for i in sound if i in all_tasks), key=lambda i: hashlib.sha256(i.encode()).hexdigest())
    return [all_tasks[i] for i in ids]


def shard(tasks):
    """This notebook's share of the fixed order: every num_shards-th task starting at shard_index."""
    return [t for k, t in enumerate(tasks) if k % CFG['num_shards'] == CFG['shard_index']]


def control(task) -> dict:
    """Gate: a task is run only if, in this environment, the checker passes the reference patch and fails the empty patch."""
    out = {'task_id': task.instance_id, 'repo': task.repo}
    try:
        ok_ref, code_ref, err_ref, s1 = check_patch(task, task.patch)
        ok_empty, code_empty, err_empty, s2 = check_patch(task, '')
        out.update(reference_resolved=ok_ref, empty_resolved=ok_empty, reference_exit=code_ref, empty_exit=code_empty,
                   seconds=round(s1 + s2, 1), valid_here=bool(ok_ref and not ok_empty), error=(err_ref if not ok_ref else '')[:200].replace('\n', ' '))
    except Exception as e:
        out.update(reference_resolved='', empty_resolved='', reference_exit='', empty_exit='', seconds='', valid_here=False, error=f'{type(e).__name__}: {e}'[:200])
    return out


def run_study(tasks, seeds, workers: int, deadline_s: float):
    """Run both arms of each task side by side, so the two arms of a task see the same server load.
    No new task is started after deadline_s; tasks not started are listed in not_run.csv."""
    t_start = time.perf_counter()
    done, not_run, controls = [], [], []
    lock = threading.Lock()

    def pair(job):
        task, seed = job
        if time.perf_counter() - t_start > deadline_s:
            with lock:
                not_run.append({'task_id': task.instance_id, 'seed': seed, 'reason': 'not started: run deadline reached'})
            return
        c = control(task)
        with lock:
            controls.append(c)
        if not c['valid_here']:
            print(f"[skip] {task.instance_id}: reference patch resolved={c['reference_resolved']}, empty patch resolved={c['empty_resolved']}", flush=True)
            return
        with ThreadPoolExecutor(max_workers=len(ARMS)) as two:
            rows = list(two.map(lambda arm: run_one(task, arm, seed), ARMS))
            rows = [r for r in rows if r]
        with lock:
            done.extend(rows)
            n = len(done) // len(ARMS)
            print(f'[{n}] {task.instance_id} s{seed}: ' + ' | '.join(
                f"{r['arm']}: {'FIXED' if r['resolved'] else r['failure_type']} "
                f"({r['turns']}t, {r['malformed_turns']} malformed, {r['agent_seconds']}s, {r['stop_reason']})" for r in rows), flush=True)

    jobs = [(t, s) for s in seeds for t in tasks]
    with ThreadPoolExecutor(max_workers=max(1, workers // len(ARMS))) as pool:
        list(pool.map(pair, jobs))
    with open(OUT_DIR / 'not_run.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['task_id', 'seed', 'reason'])
        w.writeheader()
        w.writerows(not_run)
    with open(OUT_DIR / 'controls.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['task_id', 'repo', 'reference_resolved', 'empty_resolved', 'reference_exit', 'empty_exit', 'seconds', 'valid_here', 'error'])
        w.writeheader()
        w.writerows(controls)
    return done, not_run
