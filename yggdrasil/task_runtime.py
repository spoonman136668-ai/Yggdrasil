"""NCI-04D2 opt-in Yggdrasil task execution, lesions and unlabeled repair.

This runtime is an engineering consumer of the existing LocalGenome. It
preserves a compact candidate state but does NOT establish functional
regeneration or outperform trained conventional graph models.
"""
import json
import math
from .developmental import LocalGenome, N, K, D, valid, sig, softmax

class LocalTaskRuntime:
    def __init__(self, neighbors=None):
        if neighbors is None:
            neighbors = [((i-1)%N,(i+1)%N) for i in range(N)]
        if (type(neighbors) not in (list,tuple) or len(neighbors)!=N or
            any(type(edge) not in (list,tuple) or len(edge)!=2 or
                any(type(x)!=int or not 0<=x<N or x==i for x in edge) or
                edge[0]==edge[1] for i,edge in enumerate(neighbors))):
            raise ValueError("invalid two-neighbor graph")
        self.neighbors=tuple(tuple(x) for x in neighbors)
        self.core=LocalGenome()
        self.damaged=set()
        self.steps=0

    def features(self,bits,i):
        valid(bits)
        a,b=self.neighbors[i]
        x=2*bits[i]-1
        left=2*bits[a]-1
        right=2*bits[b]-1
        return (1.,float(x),float(left),float(right),
                float(left*right),float(x*left),float(x*right))

    def component(self,bits,i):
        f=self.features(bits,i)
        guess=[sig(sum(a*b for a,b in zip(w,f))) for w in self.core.genome]
        gate=softmax(self.core.roles[i])
        return sum(p*v for p,v in zip(gate,guess))

    def predict(self,bits):
        valid(bits)
        return [self.component(bits,i) for i in range(N)]

    def observe(self,bits,outcomes,rate=.035):
        valid(bits);valid(outcomes)
        if self.damaged: raise ValueError("post-lesion labeled training forbidden")
        if type(rate) not in (float,int) or not math.isfinite(rate) or not 0<rate<=.1:
            raise ValueError("invalid training rate")
        for i,target in enumerate(outcomes):
            f=self.features(bits,i)
            guesses=[sig(sum(w*x for w,x in zip(row,f))) for row in self.core.genome]
            gate=softmax(self.core.roles[i])
            losses=[(target-p)**2 for p in guesses]
            avg=sum(w*v for w,v in zip(gate,losses))
            for k in range(K):
                self.core.roles[i][k]=max(-20.,min(20.,self.core.roles[i][k]+rate*2*(avg-losses[k])))
                delta=rate*gate[k]*(target-guesses[k])
                for j in range(D):
                    self.core.genome[k][j]=max(-15.,min(15.,self.core.genome[k][j]+delta*f[j]))
        self.core.events+=1

    def lesion(self,cells):
        if type(cells) not in (tuple,list) or not cells or len(cells)>N:
            raise ValueError("invalid lesion")
        if len(set(cells))!=len(cells) or any(type(i)!=int or not 0<=i<N for i in cells):
            raise ValueError("invalid lesion cells")
        for i in cells:
            self.core.roles[i]=[0.]*K
            self.damaged.add(i)

    def repair_unlabeled(self,bits,steps=1,rate=.05):
        valid(bits)
        if type(steps)!=int or not 0<=steps<=64:
            raise ValueError("invalid repair steps")
        if type(rate) not in (int,float) or not math.isfinite(rate) or not 0<rate<=.1:
            raise ValueError("invalid repair rate")
        # Freeze all genome weights. Only damaged local role logits can adapt.
        # Neighbor predictions are pseudo-observations, NOT teacher labels.
        for _ in range(steps):
            previous=self.predict(bits)
            delta={}
            for i in sorted(self.damaged):
                neighbors=self.neighbors[i]
                pseudo=(previous[neighbors[0]]+previous[neighbors[1]])/2
                f=self.features(bits,i)
                experts=[sig(sum(w*v for w,v in zip(row,f))) for row in self.core.genome]
                gate=softmax(self.core.roles[i])
                response=sum(a*b for a,b in zip(gate,experts))
                delta[i]=[rate*gate[k]*(experts[k]-response)*(pseudo-response)
                          for k in range(K)]
            for i,deltas in delta.items():
                for k,d in enumerate(deltas):
                    self.core.roles[i][k]=max(-20.,min(20.,self.core.roles[i][k]+d))
            self.steps+=1
        return self.predict(bits)

    def snapshot(self):
        return json.dumps({"schema":"yggdrasil.nci04d2.task.v1",
                           "neighbors":self.neighbors,"core":json.loads(self.core.snapshot()),
                           "damaged":sorted(self.damaged),"steps":self.steps},
                          sort_keys=True,separators=(",",":"))

    @classmethod
    def restore(cls,payload):
        if type(payload)!=str or len(payload)>65536:
            raise ValueError("invalid runtime snapshot")
        obj=json.loads(payload)
        if type(obj)!=dict or set(obj)!={"schema","neighbors","core","damaged","steps"} or obj["schema"]!="yggdrasil.nci04d2.task.v1":
            raise ValueError("invalid runtime schema")
        target=cls(obj["neighbors"])
        target.core.restore(json.dumps(obj["core"]))
        cells=obj["damaged"]
        if type(cells)!=list or any(type(i)!=int or not 0<=i<N for i in cells) or cells!=sorted(set(cells)):
            raise ValueError("invalid damaged cells")
        target.damaged=set(cells)
        if type(obj["steps"])!=int or not 0<=obj["steps"]<=10_000_000:
            raise ValueError("invalid repair count")
        target.steps=obj["steps"]
        return target

class LocalCountControl:
    """Equally informed conventional conditional-count comparator."""
    def __init__(self,neighbors):
        self.neighbors=tuple(tuple(v) for v in neighbors)
        self.table=[{} for _ in range(N)]
    def context(self,bits,i):
        a,b=self.neighbors[i]
        return (bits[i],bits[a],bits[b])
    def observe(self,bits,outcomes):
        valid(bits);valid(outcomes)
        for i,y in enumerate(outcomes):
            key=self.context(bits,i)
            yes,total=self.table[i].get(key,(0,0))
            self.table[i][key]=(yes+y,total+1)
    def predict(self,bits):
        valid(bits)
        return [(lambda a,b:(a+1)/(b+2))(*self.table[i].get(self.context(bits,i),(0,0))) for i in range(N)]
