"""NCI04: local predictive developmental cells, source-only development.
Observational next-state supervision, no hidden graph, task label, or traversal.
Native eight-cell ring; shared three-weight genome; no global cell matching.
"""
import math

class PredictiveColony:
    CELLS=8
    SENSORS=(0,2,4,6)
    def __init__(self,rate=.18,lateral=True):
        if not (math.isfinite(rate) and 0<=rate<=.5):
            raise ValueError("invalid learning rate")
        self.rate=rate
        self.genome=[.6,.16,.25]
        self.phenotype=[0.0]*self.CELLS
        self.lateral=lateral
        self.updates=0
    @staticmethod
    def _check(x):
        if len(x)!=4 or not all(math.isfinite(v) and abs(v)<=2 for v in x):
            raise ValueError("invalid observation")
    def _features(self,i,value):
        left=self.phenotype[(i-1)%self.CELLS]
        right=self.phenotype[(i+1)%self.CELLS]
        neighbor=.5*(left+right) if self.lateral else 0.0
        return self.phenotype[i],neighbor,value
    def predict(self,x):
        self._check(x)
        return tuple(math.tanh(sum(w*v for w,v in zip(self.genome,self._features(i,stim))))
                     for i,stim in zip(self.SENSORS,x))
    def learn(self,previous,observed):
        self._check(previous);self._check(observed)
        prediction=self.predict(previous)
        gradient=[0.0]*3
        for n,(cell,y) in enumerate(zip(self.SENSORS,observed)):
            features=self._features(cell,previous[n])
            delta=y-prediction[n]
            for j in range(3):
                gradient[j]+=delta*(1-prediction[n]**2)*features[j]/4
        states=[]
        for cell in range(self.CELLS):
            stim=previous[cell//2] if cell%2==0 else 0.0
            features=self._features(cell,stim)
            states.append(math.tanh(sum(w*v for w,v in zip(self.genome,features))))
        self.phenotype=states
        self.genome=[max(-3,min(3,w+self.rate*g)) for w,g in zip(self.genome,gradient)]
        self.updates+=1
    def erase_phenotype(self):
        self.phenotype=[0.0]*self.CELLS
    def rollout(self,current,steps):
        if type(steps)!=int or steps not in (1,2):
            raise ValueError("invalid rollout length")
        prediction=self.predict(current)
        if steps==1:return prediction
        # Propagate hypothetical state on a copy, WITHOUT learning from it.
        temporary=PredictiveColony(self.rate,self.lateral)
        temporary.genome=list(self.genome)
        temporary.phenotype=list(self.phenotype)
        states=[]
        for i in range(self.CELLS):
            stimulation=current[i//2] if i%2==0 else 0.0
            f=temporary._features(i,stimulation)
            states.append(math.tanh(sum(w*v for w,v in zip(temporary.genome,f))))
        temporary.phenotype=states
        return temporary.predict(prediction)

class LocalOnly(PredictiveColony):
    def __init__(self,rate=.18):
        super().__init__(rate=rate,lateral=False)

class RecurrentControl:
    """32-weight stronger recurrent benchmark with the same observed stream."""
    def __init__(self,rate=.24):
        self.w=[[.75 if i==j else 0.0 for j in range(4)] for i in range(4)]
        self.v=[[0.0]*4 for _ in range(4)]
        self.h=[0.0]*4
        self.rate=rate
    def predict(self,x):
        return tuple(sum(self.w[i][j]*x[j]+self.v[i][j]*self.h[j]
                         for j in range(4)) for i in range(4))
    def learn(self,previous,observed):
        guess=self.predict(previous)
        for i in range(4):
            for j in range(4):
                delta=observed[i]-guess[i]
                self.w[i][j]=max(-2,min(2,self.w[i][j]+self.rate*delta*previous[j]))
                self.v[i][j]=max(-2,min(2,self.v[i][j]+self.rate*delta*self.h[j]))
        self.h=[.7*a+.3*b for a,b in zip(self.h,previous)]
