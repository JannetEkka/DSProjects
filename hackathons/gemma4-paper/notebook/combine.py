"""Merge the output folders of the study notebooks and print every table the Writeup uses.

Usage: combine.py <out.md> <study_dir> [<study_dir> ...]
Each study_dir holds results.csv, turns.jsonl and controls.csv as written by the notebook.
Nothing here is typed by hand: all numbers come from those files.
"""
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median

out_md, dirs = Path(sys.argv[1]), [Path(d) for d in sys.argv[2:]]
rows, turns, controls = [], [], []
for d in dirs:
    rows += list(csv.DictReader(open(d / 'results.csv', encoding='utf-8')))
    turns += [json.loads(l) for l in open(d / 'turns.jsonl', encoding='utf-8')]
    if (d / 'controls.csv').exists():
        controls += list(csv.DictReader(open(d / 'controls.csv', encoding='utf-8')))
for r in rows:
    r['resolved'] = r['resolved'] == 'True'
    for k in ('turns', 'malformed_turns', 'usable_turns', 'commands_run', 'patch_chars', 'completion_tokens', 'prompt_tokens'):
        r[k] = int(r[k])
    r['agent_seconds'] = float(r['agent_seconds'])

arms = [a for a in ('json', 'text', 'text_stop') if any(r['arm'] == a for r in rows)]
by_task = defaultdict(dict)
for r in rows:
    by_task[r['task_id']][r['arm']] = r
errors = {t for t, d in by_task.items() if any(x['harness_error'] for x in d.values())}
L = []
P = L.append

# controls (deduplicated by task: the same task may be gated in two notebooks)
ctrl = {}
for c in controls:
    ctrl.setdefault(c['task_id'], c)
if ctrl:
    valid = [c for c in ctrl.values() if c.get('valid_here') == 'True']
    P(f'## Checker control\n\nTasks tried: {len(ctrl)}. Reference patch passes and empty patch fails here: {len(valid)}.\n')
    P('| Repository | Tried | Valid here |\n|---|---|---|')
    for repo in sorted({c['repo'] for c in ctrl.values()}):
        cs = [c for c in ctrl.values() if c['repo'] == repo]
        P(f"| {repo} | {len(cs)} | {sum(c.get('valid_here') == 'True' for c in cs)} |")
    P('')
P(f'Harness-error tasks (left out of every comparison): {len(errors)} {sorted(errors)}\n')


def sign_p(a, b):
    k, m = min(a, b), a + b
    return min(1.0, 2 * sum(math.comb(m, i) for i in range(k + 1)) / 2 ** m) if m else 1.0


def table(task_ids, title):
    n = len(task_ids)
    P(f'## {title} (n = {n} tasks)\n')
    P('| | ' + ' | '.join(f'`{a}`' for a in arms) + ' |\n|---|' + '---|' * len(arms))
    R = {a: [by_task[t][a] for t in task_ids] for a in arms}
    T = {a: [x for x in turns if x['arm'] == a and x['task_id'] in task_ids] for a in arms}

    def line(label, f):
        P(f'| {label} | ' + ' | '.join(str(f(a)) for a in arms) + ' |')
    line('Tasks fixed', lambda a: f"{sum(r['resolved'] for r in R[a])} of {n}")
    line('Malformed turns', lambda a: f"{sum(not t['usable'] for t in T[a])} of {len(T[a])}")
    line('Turns cut off at the output cap', lambda a: sum(t['finish_reason'] == 'length' for t in T[a]))
    line('Turns with more than one action written', lambda a: sum(t['actions_in_reply'] > 1 for t in T[a]))
    line('Runs that submitted', lambda a: sum(r['stop_reason'] == 'submit' for r in R[a]))
    line('Runs stopped by the time limit', lambda a: sum(r['stop_reason'] == 'time_limit' for r in R[a]))
    line('Runs stopped by the turn limit', lambda a: sum(r['stop_reason'] == 'turn_limit' for r in R[a]))
    line('Runs that left a patch', lambda a: sum(r['patch_chars'] > 0 for r in R[a]))
    line('Turns per task (median / mean)', lambda a: f"{median(r['turns'] for r in R[a]):g} / {mean(r['turns'] for r in R[a]):.1f}")
    line('Agent seconds per task (median / mean)', lambda a: f"{median(r['agent_seconds'] for r in R[a]):.0f} / {mean(r['agent_seconds'] for r in R[a]):.0f}")
    line('Output tokens per turn (mean)', lambda a: f"{mean(t['completion_tokens'] for t in T[a]):.0f}" if T[a] else '')
    line('Output tokens per task (mean)', lambda a: f"{mean(r['completion_tokens'] for r in R[a]):.0f}")
    P('')
    for a, b in [(x, y) for i, x in enumerate(arms) for y in arms[i + 1:]]:
        both = sum(by_task[t][a]['resolved'] and by_task[t][b]['resolved'] for t in task_ids)
        oa = sum(by_task[t][a]['resolved'] and not by_task[t][b]['resolved'] for t in task_ids)
        ob = sum(by_task[t][b]['resolved'] and not by_task[t][a]['resolved'] for t in task_ids)
        P(f'- `{a}` vs `{b}`: both {both}, only `{a}` {oa}, only `{b}` {ob}, neither {n - both - oa - ob}; exact two-sided sign test on the {oa + ob} disagreements: p = {sign_p(oa, ob):.3f}')
    P('\nWhy unfixed runs failed (fixed rules, in order):\n\n| Failure type | ' + ' | '.join(f'`{a}`' for a in arms) + ' |\n|---|' + '---|' * len(arms))
    for ft in ('no_patch', 'stuck_on_format', 'out_of_budget_with_patch', 'submitted_tests_fail'):
        line(ft, lambda a: sum(r['failure_type'] == ft for r in R[a]))
    P('\nMalformed turns by reason: ' + '; '.join(f"`{a}`: {dict(Counter(t['malformed_reason'] for t in T[a] if not t['usable'])) or 'none'}" for a in arms))
    P('\nBy repository (fixed / tasks): ' + '; '.join(
        f"{repo}: " + ', '.join(f"`{a}` {sum(r['resolved'] for r in R[a] if r['repo'] == repo)}/{sum(r['repo'] == repo for r in R[a])}" for a in arms)
        for repo in sorted({r['repo'] for r in R[arms[0]]})))
    P('\nMost used command words: ' + '; '.join(f"`{a}`: {Counter(t['command_head'] for t in T[a] if t['command_head']).most_common(6)}" for a in arms))
    P('')


two = sorted(t for t, d in by_task.items() if {'json', 'text'} <= set(d) and t not in errors)
if two:
    saved = arms
    arms = ['json', 'text']
    table(two, 'Main comparison: json vs text')
    arms = saved
three = sorted(t for t, d in by_task.items() if set(arms) <= set(d) and t not in errors)
if len(arms) == 3 and three:
    table(three, 'Tasks run in all three arms')
P('Task ids in the main comparison: ' + ', '.join(two))
out_md.write_text('\n'.join(L) + '\n', encoding='utf-8')
print('\n'.join(L))

# one merged results.csv for the chart and for publishing
with open(out_md.with_name('results_merged.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
