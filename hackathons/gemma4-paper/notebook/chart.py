"""Paired chart from results.csv: one segmented bar of tasks by outcome pair. Usage: chart.py results.csv out_prefix"""
import csv, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
rows=[r for r in csv.DictReader(open(sys.argv[1])) if not r['harness_error']]
by={}
for r in rows: by.setdefault(r['task_id'],{})[r['arm']]=r['resolved']=='True'
by={k:v for k,v in by.items() if 'json' in v and 'text' in v}
n=len(by)
cats=[('Fixed in both',sum(v['json'] and v['text'] for v in by.values())),
      ('Only text',sum(v['text'] and not v['json'] for v in by.values())),
      ('Only JSON',sum(v['json'] and not v['text'] for v in by.values())),
      ('Fixed in neither',sum(not v['json'] and not v['text'] for v in by.values()))]
themes={'light':dict(bg='#fcfcfb',ink='#0b0b0b',ink2='#52514e',cols=['#52514e','#2a78d6','#eb6834','#d9d8d2']),
        'dark':dict(bg='#1a1a19',ink='#f0efec',ink2='#c3c2b7',cols=['#c3c2b7','#3987e5','#d95926','#3a3a37'])}
for name,t in themes.items():
    fig,ax=plt.subplots(figsize=(9,2.3),dpi=200); fig.patch.set_facecolor(t['bg']); ax.set_facecolor(t['bg'])
    x=0; placed=[]
    for (lab,c),col in zip(cats,t['cols']):
        if c:
            ax.barh(0,c,left=x,height=0.5,color=col,edgecolor=t['bg'],linewidth=2)
            small=c<n*0.12
            if small:
                k=sum(1 for q in placed if q); placed.append(1)
                ax.annotate(f'{lab}: {c}',xy=(x+c/2,0.25),xytext=(n*0.02+k*n*0.2,0.62+0.0*k),ha='left',va='bottom',color=t['ink'],fontsize=10,arrowprops=dict(arrowstyle='-',color=t['ink2'],lw=0.8))
            else:
                ax.text(x+c/2,0,f'{lab}: {c}',ha='center',va='center',color=t['ink'],fontsize=10)
        x+=c
    ax.set_xlim(0,n); ax.set_ylim(-0.45,1.15); ax.set_yticks([])
    ax.set_xlabel(f'Tasks (n = {n}), each run once per action format',color=t['ink2'],fontsize=9)
    ax.tick_params(colors=t['ink2'],labelsize=8)
    for s in ax.spines.values(): s.set_visible(False)
    fig.tight_layout(); fig.savefig(f'{sys.argv[2]}_{name}.png',facecolor=t['bg']); plt.close(fig)
print(n,cats)

# second figure: tasks fixed per arm, on tasks run in all three arms
by3={}
for r in rows: by3.setdefault(r['task_id'],{})[r['arm']]=r['resolved']=='True'
by3={k:v for k,v in by3.items() if {'json','text','text_stop'}<=set(v)}
if by3:
    n3=len(by3); arms3=[('Tool calls (json)','json'),('Bash blocks (text)','text'),('Bash blocks, reply cut after the first block (text_stop)','text_stop')]
    for name,t in themes.items():
        cols=[t['cols'][2],t['cols'][1],'#1baf7a' if name=='light' else '#199e70']
        fig,ax=plt.subplots(figsize=(9,2.6),dpi=200); fig.patch.set_facecolor(t['bg']); ax.set_facecolor(t['bg'])
        for i,((lab,a),col) in enumerate(zip(arms3,cols)):
            c=sum(v[a] for v in by3.values()); y=len(arms3)-1-i
            ax.barh(y,c,height=0.42,color=col,edgecolor=t['bg'],linewidth=2)
            ax.text(c+0.25,y,f'{c} of {n3}',va='center',ha='left',color=t['ink'],fontsize=10)
            ax.text(0,y+0.3,lab,va='bottom',ha='left',color=t['ink2'],fontsize=9)
        ax.set_xlim(0,max(14,max(sum(v[a] for v in by3.values()) for _,a in arms3)+3)); ax.set_ylim(-0.4,len(arms3)-0.15); ax.set_yticks([])
        ax.set_xlabel(f'Tasks fixed (of {n3}), Gemma 4 12B, 50 turns and 15 minutes per run',color=t['ink2'],fontsize=9)
        ax.tick_params(colors=t['ink2'],labelsize=8)
        for s in ax.spines.values(): s.set_visible(False)
        fig.tight_layout(); fig.savefig(f'{sys.argv[2]}_arms_{name}.png',facecolor=t['bg']); plt.close(fig)
