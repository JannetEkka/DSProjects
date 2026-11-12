# Every number below is computed from results.csv and turns.jsonl. Nothing is typed by hand.
import json
import math

import pandas as pd

res = pd.read_csv(OUT_DIR / 'results.csv', keep_default_na=False)
turns = pd.read_json(OUT_DIR / 'turns.jsonl', lines=True)
res['resolved'] = res['resolved'].astype(str).str.lower().eq('true')
summary = {'model': CFG['model_name'], 'budget': {k: CFG[k] for k in ('max_turns', 'time_limit_s', 'cmd_timeout_s', 'output_cut', 'max_tokens', 'thinking_budget', 'temperature', 'top_p', 'context_tokens')}}

planned = {(t.instance_id, a, s) for t in RUN_TASKS for a in ARMS for s in CFG['seeds']}
got = {(r.task_id, r.arm, r.seed) for r in res.itertuples()}
missing = sorted(planned - got)
dupes = int(res.duplicated(['task_id', 'arm', 'seed']).sum())
print(f'Planned rows: {len(planned)}. Rows in results.csv: {len(res)}. Missing: {len(missing)}. Duplicates: {dupes}.')
summary['rows'] = {'planned': len(planned), 'present': len(res), 'missing': len(missing), 'duplicates': dupes}

# Tasks where either arm hit a harness error are left out of the comparison, and counted.
bad = set(res.loc[res['harness_error'] != '', 'task_id'])
complete = res.groupby(['task_id', 'seed'])['arm'].nunique().reset_index()
complete = complete[complete['arm'] == 2]
ok = res.merge(complete[['task_id', 'seed']], on=['task_id', 'seed'])
ok = ok[~ok['task_id'].isin(bad)]
print(f'Tasks with a harness error in either arm (left out): {len(bad)}')
summary['harness_error_tasks'] = sorted(bad)

for seed, grp in ok.groupby('seed'):
    n = grp['task_id'].nunique()
    print(f'\n===== seed {seed}: {n} tasks, both arms =====')
    t = turns[(turns['seed'] == seed) & turns['task_id'].isin(grp['task_id'])]
    rows = []
    for arm in ARMS:
        g, tt = grp[grp['arm'] == arm], t[t['arm'] == arm]
        rows.append({
            'arm': arm, 'tasks': n, 'fixed': int(g['resolved'].sum()),
            'turns': len(tt), 'malformed_turns': int((~tt['usable']).sum()),
            'malformed_share': round(float((~tt['usable']).mean()), 4) if len(tt) else None,
            'tasks_with_a_malformed_turn': int((g['malformed_turns'] > 0).sum()),
            'median_turns': float(g['turns'].median()), 'mean_turns': round(float(g['turns'].mean()), 2),
            'median_agent_seconds': float(g['agent_seconds'].median()), 'mean_agent_seconds': round(float(g['agent_seconds'].mean()), 1),
            'submitted': int((g['stop_reason'] == 'submit').sum()), 'hit_time_limit': int((g['stop_reason'] == 'time_limit').sum()),
            'hit_turn_limit': int((g['stop_reason'] == 'turn_limit').sum()),
            'completion_tokens_per_turn': round(float(tt['completion_tokens'].mean()), 1) if len(tt) else None,
        })
    headline = pd.DataFrame(rows).set_index('arm')
    display(headline.T)

    wide = grp.pivot(index='task_id', columns='arm', values='resolved')
    both = int((wide['json'] & wide['text']).sum())
    only_text = int((~wide['json'] & wide['text']).sum())
    only_json = int((wide['json'] & ~wide['text']).sum())
    neither = int((~wide['json'] & ~wide['text']).sum())
    k, m = min(only_text, only_json), only_text + only_json
    p = min(1.0, 2 * sum(math.comb(m, i) for i in range(k + 1)) / 2 ** m) if m else 1.0
    print(f'Paired: both {both}, only text {only_text}, only json {only_json}, neither {neither}.')
    print(f'Exact two-sided sign test on the {m} tasks where the arms disagree: p = {p:.3f}')

    fail = grp[~grp['resolved']].groupby(['arm', 'failure_type']).size().unstack(0, fill_value=0)
    print('\nWhy unfixed tasks failed (fixed rules, in order):')
    display(fail)
    reasons = t[~t['usable']].groupby(['arm', 'malformed_reason']).size().unstack(0, fill_value=0)
    print('Malformed turns by reason:')
    display(reasons)
    by_repo = grp.groupby(['repo', 'arm'])['resolved'].agg(['sum', 'count']).unstack('arm')
    print('By repository (fixed, tasks):')
    display(by_repo)
    summary[f'seed_{seed}'] = {
        'headline': headline.reset_index().to_dict('records'),
        'paired': {'both': both, 'only_text': only_text, 'only_json': only_json, 'neither': neither, 'sign_test_p': round(p, 4)},
        'failure_types': fail.to_dict(), 'malformed_reasons': reasons.to_dict(),
        'by_repo': {f'{r}|{a}': [int(v['sum']), int(v['count'])] for (r, a), v in grp.groupby(['repo', 'arm'])['resolved'].agg(['sum', 'count']).iterrows()},
        'paired_by_task': {tid: {'json': bool(r['json']), 'text': bool(r['text'])} for tid, r in wide.iterrows()},
    }

(OUT_DIR / 'summary.json').write_text(json.dumps(summary, indent=1, default=str), encoding='utf-8')
print('\nWrote summary.json')
