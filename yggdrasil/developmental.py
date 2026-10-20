"""Candidate-only fixed-budget local-cell developmental prediction.

Eight cells learn private role states from individual locally observable
prediction errors. A shared compact genome holds candidate phenotypes.
A lesion deletes its role state and recovery relearns through subsequent local
consequences rather than neighbor parameter copying.

Scientific novelty, equal-resource superiority, and autonomous cognition
remain unproven. Strong conventional controls are mandatory.
"""
import json
import math

N=8
K=3
D=7

def valid(bits):
    if type(bits) not in (list,tuple) or len(bits)!=N or any(type(v)!=int or v not in (0,1) for v in bits):
        raise ValueError("eight binary cell observations required")

def feat(bits,i):
    valid(bits)
    u=2*bits[i]-1
    a=2*bits[(i-1)%N]-1
    b=2*bits[(i+1)%N]-1
    return (1.,float(u),float(a),float(b),float(a*b),float(u*a),float(u*b))

def sig(z):
    z=max(-35.,min(35.,z))
    return 1./(1.+math.exp(-z))

def softmax(x):
    m=max(x)
    xs=[math.exp(z-m) for z in x]
    den=sum(xs)
    return [z/den for z in xs]

class LocalGenome:
    def __init__(self):
        # Small deterministic numerical symmetry break; no teacher role labels.
        self.genome=[[(k-1)*0.013*((j%3)-1) for j in range(D)] for k in range(K)]
        self.roles=[[0.]*K for _ in range(N)]
        self.events=0

    def predict_cell(self,bits,i):
        if type(i)!=int or not 0<=i<N: raise ValueError("invalid cell")
        f=feat(bits,i)
        experts=[sig(sum(w*v for w,v in zip(row,f))) for row in self.genome]
        gate=softmax(self.roles[i])
        return sum(p*e for p,e in zip(gate,experts))

    def train_cell(self,bits,i,outcome,rate=.035):
        if type(i)!=int or not 0<=i<N or type(outcome)!=int or outcome not in (0,1):
            raise ValueError("invalid local observation")
        if not isinstance(rate,(int,float)) or not math.isfinite(rate) or not 0<rate<=.1:
            raise ValueError("invalid learning rate")
        f=feat(bits,i)
        guesses=[sig(sum(a*b for a,b in zip(w,f))) for w in self.genome]
        gate=softmax(self.roles[i])
        losses=[(outcome-p)**2 for p in guesses]
        avg=sum(g*l for g,l in zip(gate,losses))
        for k in range(K):
            self.roles[i][k]=max(-20.,min(20.,self.roles[i][k]+rate*2.0*(avg-losses[k])))
            delta=rate*gate[k]*(outcome-guesses[k])
            for j in range(D):
                v=self.genome[k][j]+delta*f[j]
                if not math.isfinite(v): raise ValueError("nonfinite update")
                self.genome[k][j]=max(-15.,min(15.,v))
        self.events+=1

    def predict(self,bits):
        valid(bits)
        return [self.predict_cell(bits,i) for i in range(N)]

    def observe(self,bits,outcomes,rate=.035):
        valid(bits);valid(outcomes)
        for i,o in enumerate(outcomes): self.train_cell(bits,i,o,rate)

    def lesion(self,i):
        if type(i)!=int or not 0<=i<N: raise ValueError("invalid cell")
        self.roles[i]=[0.]*K

    def role_weights(self,i):
        if type(i)!=int or not 0<=i<N: raise ValueError("invalid cell")
        return softmax(self.roles[i])

    def snapshot(self):
        return json.dumps({"schema":"yggdrasil.nci04a.local-genome.v1","genome":self.genome,"roles":self.roles,"events":self.events},sort_keys=True,separators=(",",":"))

    def restore(self,payload):
        if not isinstance(payload,str) or len(payload)>16384: raise ValueError("invalid snapshot size")
        o=json.loads(payload)
        if type(o)!=dict or set(o)!={"schema","genome","roles","events"} or o["schema"]!="yggdrasil.nci04a.local-genome.v1": raise ValueError("invalid schema")
        g=o["genome"];roles=o["roles"];e=o["events"]
        if (type(g)!=list or len(g)!=K or any(type(a)!=list or len(a)!=D for a in g) or
            type(roles)!=list or len(roles)!=N or any(type(a)!=list or len(a)!=K for a in roles) or
            type(e)!=int or not 0<=e<=100_000_000): raise ValueError("invalid shape")
        if any(type(x) not in (int,float) or not math.isfinite(x) or abs(x)>20 for row in g+roles for x in row): raise ValueError("invalid coefficient")
        self.genome=[[float(x) for x in a] for a in g]
        self.roles=[[float(x) for x in a] for a in roles]
        self.events=e
