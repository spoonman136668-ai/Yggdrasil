"""MG94-K matched-public-history aliasing negative; development only."""
import json

def evaluate(training):
    two, one = {}, {}
    for prior,current,action,outcome in training:
        two.setdefault((prior,current,action),[0,0])[outcome] += 1
        one.setdefault((current,action),[0,0])[outcome] += 1
    probes=[(0,0,1,0),(1,0,1,1)]
    def vote(counts):
        return None if counts is None or counts[0]==counts[1] else int(counts[1]>counts[0])
    return {"matched_order2":[vote(two.get(p[:3])) for p in probes],
            "order1":[vote(one.get(p[1:3])) for p in probes],
            "targets":[p[3] for p in probes]}

def run():
    train=[(p,0,1,p) for p in (0,1) for _ in range(5)]
    result=evaluate(train)
    assert result["matched_order2"]==[0,1]
    assert result["order1"]==[None,None]
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__": run()
