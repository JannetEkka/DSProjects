"""Paired chart from results.csv: one segmented bar of tasks by outcome pair. Usage: chart.py results.csv out_prefix"""
import csv, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
rows=[r for r in csv.DictReader(open(sys.argv[1])) if not r['harness_error']]
by={}
for r in rows: by.setdefault(r['task_id'],{})[r['arm']]=r['resolved']=='True'
by={k:v for k,v in by.items() if len(v)==2}
n=len(by)
cats=[('Fixed in both',sum(v['json'] and v['text'] for v in by.values())),
      ('Only text',sum(v['text'] and not v['json'] for v in by.values())),
      ('Only JSON',sum(v['json'] and not v['text'] for v in by.values())),
      ('Fixed in neither',sum(not v['json'] and not v['text'] for v in by.values()))]
themes={'light':dict(bg='#fcfcfb',ink='#0b0b0b',ink2='#52514e',cols=['#52514e','#2a78d6','#eb6834','#d9d8d2']),
        'dark':dict(bg='#1a1a19',ink='#f0efec',ink2='#c3c2b7',cols=['#c3c2b7','#3987e5','#d95926','#3a3a37'])}
for name,t in themes.items():
    fig,ax=plt.subplots(figsize=(9,2.3),dpi=200); fig.patch.set_facecolor(t['bg']); ax.set_facecolor(t['bg'])
    x=0
    for (lab,c),col in zip(cats,t['cols']):
        if c:
            ax.barh(0,c,left=x,height=0.5,color=col,edgecolor=t['bg'],linewidth=2)
            ax.text(x+c/2,0.42,f'{lab}\n{c}',ha='center',va='bottom',color=t['ink'],fontsize=10)
        x+=c
    ax.set_xlim(0,n); ax.set_ylim(-0.45,1.15); ax.set_yticks([])
    ax.set_xlabel(f'Tasks (n = {n}), each run once per action format',color=t['ink2'],fontsize=9)
    ax.tick_params(colors=t['ink2'],labelsize=8)
    for s in ax.spines.values(): s.set_visible(False)
    fig.tight_layout(); fig.savefig(f'{sys.argv[2]}_{name}.png',facecolor=t['bg']); plt.close(fig)
print(n,cats)
