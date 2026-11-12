import json,csv,sys
from statistics import median
T=[];R=[]
for d in sys.argv[1:]:
    T+=[json.loads(l) for l in open(d+'/turns.jsonl')]; R+=list(csv.DictReader(open(d+'/results.csv')))
for arm in ('json','text','text_stop'):
    t=[x for x in T if x['arm']==arm]
    if not t: continue
    print(arm,'first turns with thinking',sum(x['reasoning_chars']>0 for x in t if x['turn']==1),'of',sum(x['turn']==1 for x in t),
      '| turns>=16 without thinking',sum(x['reasoning_chars']==0 for x in t if x['turn']>=16),'of',sum(x['turn']>=16 for x in t),
      '| median output tokens/turn',median(x['completion_tokens'] for x in t),'| tok/s',round(sum(x['completion_tokens'] for x in t)/sum(x['llm_seconds'] for x in t),1),
      '| finish',{k:sum(x['finish_reason']==k for x in t) for k in {x['finish_reason'] for x in t}})
    r=[x for x in R if x['arm']==arm]; tl=[x for x in r if x['stop_reason']=='turn_limit']
    print('   turn-limit runs',len(tl),'of which no patch',sum(x['patch_chars']=='0' for x in tl),'| runs',len(r),'| rows w/ harness_error',sum(bool(x['harness_error']) for x in r),'| elided outputs',sum(int(x['elided_outputs']) for x in r))
