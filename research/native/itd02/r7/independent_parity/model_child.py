#!/usr/bin/env python3
"""R7 independent original-dev FIT-only causal predictor controls.

No source-world oracle, fixture truth function or hidden causal parent is
imported by the ordinary training/prediction child.  The only native-specific
import is the unchanged source-native R7 model, for the native arm alone.
"""
from __future__ import annotations
import argparse,base64,hashlib,itertools,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT))
TRIPLES=tuple(itertools.combinations(range(8),3))
ARMS=("native","conventional","nearest")
def need(ok,s):
    if not ok:raise ValueError("R7_PARITY_DENIED_"+s)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def hamming(a,b):return (a^b).bit_count()
def bucket(state,parents):
    return (((state>>parents[0])&1)
          |(((state>>parents[1])&1)<<1)
          |(((state>>parents[2])&1)<<2))
def independent_conventional(rows):
    worlds={}
    for world,action,before,after in rows:
        worlds.setdefault(world,{}).setdefault(str(action),[]).append((before,after))
    out={}
    for world,operations in worlds.items():
        need(set(operations)=={"0","1","2"},"COMPLETE_ACTIONS")
        out[world]={}
        for action in ("0","1","2"):
            samples=operations[action]
            need(len(samples)==192 and len(set(x for x,_ in samples))==192,"COMPLETE_FIT")
            model=[]
            for bit in range(8):
                winner=None
                for parents in TRIPLES:
                    total=[0]*8
                    ones=[0]*8
                    for before,after in samples:
                        j=bucket(before,parents)
                        total[j]+=1
                        ones[j]+=(after>>bit)&1
                    table=[int(2*ones[j]>=total[j]) if total[j] else 0 for j in range(8)]
                    error=sum(min(ones[j],total[j]-ones[j]) for j in range(8))
                    # independent objective; deterministic min-error+min-parent tuple
                    key=(error,parents)
                    if winner is None or key<winner[0]:winner=(key,table)
                model.append({"p":list(winner[0][1]),"t":winner[1]})
            out[world][action]=model
    return out
def conventional_step(model,world,action,x):
    word=0
    for bit,entry in enumerate(model[world][str(action)]):
        word|=entry["t"][bucket(x,entry["p"])]<<bit
    return word
def nearest_step(model,world,action,x):
    entries=model[world][str(action)]
    near=min(entries,key=lambda row:(hamming(x,row[0]),row[0]))
    return near[1]
def validate(rows):
    need(type(rows) is list and len(rows)==1152,"EXACT_AUTHORED_FIT_EVENTS")
    seen=set()
    for row in rows:
        need(type(row) is list and len(row)==4,"PUBLIC_EVENT")
        w,a,x,y=row
        need(w in ("11","12") and type(a) is int and a in (0,1,2)
             and type(x) is int and 0<=x<256
             and type(y) is int and 0<=y<256,"EVENT_BOUNDS")
        key=(w,a,x);need(key not in seen,"DUPLICATE_FIT")
        seen.add(key)
    for w in ("11","12"):
        for a in (0,1,2):
            need(sum(1 for x in seen if x[0]==w and x[1]==a)==192,
                 "PER_WORLD_ACTION_BALANCE")
def train(arm,rows):
    validate(rows)
    if arm=="native":
        from research.native.itd02.r7.learner import NonlinearLocalLearner
        native=NonlinearLocalLearner()
        for world,action,before,after in rows:
            native.observe(world,action,before,after)
        native.fit()
        snap=native.checkpoint()
        need(native.events==1152,"NATIVE_EVENTS")
    elif arm=="conventional":
        models=independent_conventional(rows)
        snap=canonical({"schema":"independent-3parent-conventional-v1","models":models})
    else:
        models={}
        for world,action,x,y in rows:
            models.setdefault(world,{}).setdefault(str(action),[]).append([x,y])
        for world in models:
            for action in models[world]:
                models[world][action].sort()
        snap=canonical({"schema":"independent-1nn-public-v1","models":models})
    return snap
def restored(arm,raw):
    if arm=="native":
        from research.native.itd02.r7.learner import NonlinearLocalLearner
        return NonlinearLocalLearner.restore(raw)
    obj=json.loads(raw)
    need(set(obj)=={"schema","models"},"SNAPSHOT_SCHEMA")
    need(obj["schema"]==("independent-3parent-conventional-v1" if arm=="conventional" else "independent-1nn-public-v1"),"MODEL_SCHEMA")
    need(set(obj["models"])=={"11","12"},"MODEL_WORLDS")
    return obj["models"]
def step(arm,model,w,a,x):
    if arm=="native":return model.step(w,a,x)
    if arm=="conventional":return conventional_step(model,w,a,x)
    return nearest_step(model,w,a,x)
def score(arm,snapshot,queries):
    model=restored(arm,snapshot)
    out=[]
    for q in queries:
        need(type(q) is list and len(q)==3,"LEGAL_QUERY")
        w,x,actions=q
        need(w in ("11","12") and type(x) is int and 0<=x<256
             and type(actions) is list and 1<=len(actions)<=5
             and all(type(a) is int and a in (0,1,2) for a in actions),"PUBLIC_QUERY")
        state=x
        for action in actions:
            state=step(arm,model,w,action,state)
        out.append(state)
    return out
def usage():
    try:
        import resource
        r=resource.getrusage(resource.RUSAGE_SELF)
        return int(r.ru_maxrss*(1024 if sys.platform.startswith("linux") else 1))
    except ImportError:return None
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--arm",choices=ARMS,required=True)
    parser.add_argument("--mode",choices=("train","score","ablate"),required=True)
    args=parser.parse_args()
    payload=json.load(sys.stdin)
    if args.mode=="train":
        snap=train(args.arm,payload["public_fit"])
        result={"checkpoint_b64":base64.b64encode(snap).decode(),
                "checkpoint_bytes":len(snap),"checkpoint_sha256":hashlib.sha256(snap).hexdigest(),
                "public_fit_events":1152}
    else:
        snap=base64.b64decode(payload["checkpoint_b64"],validate=True)
        need(hashlib.sha256(snap).hexdigest()==payload["checkpoint_sha256"],
             "COLD_SNAPSHOT_SHA256")
        q=payload["queries"]
        if args.mode=="score":
            preds=score(args.arm,snap,q)
        else:
            model=restored(args.arm,snap)
            preds=[step(args.arm,model,w,actions[-1],x)
                   for w,x,actions in q]
        result={"predictions":preds,"cold_interpreter":True}
    result["process_cpu_ns"]=time.process_time_ns()
    result["whole_process_peak_rss_bytes"]=usage()
    print(json.dumps(result,sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
