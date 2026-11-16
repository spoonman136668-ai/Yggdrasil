"""AAI-12V two-slot PUBLIC-only posterior; no import of hidden world or oracle."""
import hashlib
import json
import math

FIELDS={"x","y","ports","do_step"}
ARMS=("information_gain","predictive_entropy","random_probe","fixed_probe","sham_probe")
PRIOR=(.45,.45,.10)
EPS=.05

def validate(row):
    if type(row)!=dict or set(row)!=FIELDS:raise ValueError("public field boundary")
    x=row["x"];p=row["ports"];y=row["y"];step=row["do_step"]
    if (type(x)!=list or len(x)!=8 or any(type(v)!=int or v not in (0,1) for v in x)
        or type(p)!=list or len(p)!=4 or len(set(p))!=4 or
        any(type(v)!=int or not 0<=v<8 for v in p) or type(y)!=int or y not in (0,1)
        or type(step)!=int or step not in (0,1)):
        raise ValueError("invalid public observation")
    return tuple(x),tuple(p)

def public_events(rows,expected_pairs=None):
    if len(rows)%2 or (expected_pairs is not None and len(rows)!=2*expected_pairs):
        raise ValueError("noncanonical action count")
    codevals={}
    for before,after in zip(rows[::2],rows[1::2]):
        a,p=validate(before);b,q=validate(after)
        if p!=q or before["do_step"]!=0 or after["do_step"]!=1:raise ValueError("missing do transition")
        if sum(u!=v for u,v in zip(a,b))!=1 or a[p[3]]!=0 or b[p[3]]!=1:
            raise ValueError("wrong intervened bit")
        code=4*a[p[0]]+2*a[p[1]]+a[p[2]]
        if code in codevals:raise ValueError("same ternary input reused as independent evidence")
        bit=before["y"]^a[p[3]]
        if after["y"]^b[p[3]]!=bit:raise ValueError("nonreproducible local causal operator")
        codevals[code]=bit
    return codevals

def learn_mask(rows):
    obs=public_events(rows,8)
    if sorted(obs)!=list(range(8)):raise ValueError("incomplete donor memory")
    return sum(v<<k for k,v in obs.items())

def posterior(masks,obs):
    if len(masks)!=2 or any(type(m)!=int or not 0<=m<256 for m in masks):
        raise ValueError("incorrect memory capacity")
    weights=list(PRIOR)
    for code,val in sorted(obs.items()):
        if code not in range(8) or val not in (0,1):raise ValueError("invalid public code")
        for i in (0,1):
            weights[i]*=(1-EPS if ((masks[i]>>code)&1)==val else EPS)
        weights[2]*=.5
    total=sum(weights)
    return tuple(w/total for w in weights)

def prob_y(masks,weights,code):
    return sum(w*q for w,q in zip(weights,(EPS+(1-2*EPS)*((masks[0]>>code)&1),
                                       EPS+(1-2*EPS)*((masks[1]>>code)&1),.5)))

def ent(probs):
    return -sum(p*math.log2(p) for p in probs if p>0)

def choose(arm,masks,obs,seed):
    if arm not in ARMS:raise ValueError("invalid action selector")
    eligible=tuple(c for c in range(8) if c not in obs)
    if len(eligible)!=6:raise ValueError("receiver public data budget drift")
    if arm=="sham_probe":return min(obs)
    if arm=="fixed_probe":return eligible[0]
    if arm=="random_probe":return eligible[int.from_bytes(hashlib.sha256(seed).digest()[:8],"big")%6]
    weights=posterior(masks,obs)
    scored=[]
    for code in eligible:
        pred=prob_y(masks,weights,code)
        if arm=="predictive_entropy":gain=ent((pred,1-pred))
        else:
            start=ent(weights)
            expected=0
            for result in (0,1):
                ps=(EPS+(1-2*EPS)*((masks[0]>>code)&1),
                    EPS+(1-2*EPS)*((masks[1]>>code)&1),.5)
                joint=[w*(q if result else 1-q) for w,q in zip(weights,ps)]
                likelihood=sum(joint)
                expected+=likelihood*ent(tuple(v/likelihood for v in joint))
            gain=start-expected
        scored.append((gain,-code,code))
    return max(scored)[2]

def fit(rows_d,rows_i,rows_r,arm,seed):
    memories=(learn_mask(rows_d),learn_mask(rows_i))
    initial=public_events(rows_r,2)
    code=choose(arm,memories,initial,seed)
    return memories,initial,code

def predict(masks,obs,ports,x):
    if len(x)!=8 or any(v not in (0,1) for v in x) or len(ports)!=4:raise ValueError("invalid prediction")
    a,b,c,f=ports;code=4*x[a]+2*x[b]+x[c]
    if code in obs:bit=obs[code]
    else:bit=int(prob_y(masks,posterior(masks,obs),code)>.5)
    return bit^x[f]

def cold(masks,obs,ports,arm):
    state={"schema":"aai12v.public.v1","masks":list(masks),
           "observed":sorted([list(z) for z in obs.items()]),"ports":list(ports),"arm":arm}
    return json.dumps(state,sort_keys=True,separators=(",",":"))

def restore(snapshot):
    s=json.loads(snapshot)
    if type(s)!=dict or set(s)!={"schema","masks","observed","ports","arm"} or s["schema"]!="aai12v.public.v1" or s["arm"] not in ARMS:
        raise ValueError("invalid cold state")
    masks=tuple(s["masks"]);obs=dict(s["observed"]);ports=tuple(s["ports"])
    if len(s["observed"])!=(2 if s["arm"]=="sham_probe" else 3) or len(obs)!=len(s["observed"]) or sorted(obs.keys())!=sorted(set(obs)) or len(set(ports))!=4:
        raise ValueError("corrupted public history")
    posterior(masks,obs)
    if cold(masks,obs,ports,s["arm"])!=snapshot:raise ValueError("noncanonical cold state")
    return masks,obs,ports
