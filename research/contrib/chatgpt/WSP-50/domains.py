from frozen_world import rng_for
import hashlib

class Encoding:
    def __init__(self,width,kind,tag):
        self.width=width;self.size=1<<width;self.kind=kind;rng=rng_for(tag+'|encoding|'+kind)
        if kind=='identity':self.forward=list(range(self.size))
        elif kind=='random_permutation':
            rest=list(range(1,self.size));rng.shuffle(rest);self.forward=[0]+rest
        elif kind=='linear_bijection':
            rows=[1<<i for i in range(width)]
            for _ in range(4*width):
                i,j=rng.sample(range(width),2);rows[i]^=rows[j]
            self.forward=[sum(((x&row).bit_count()%2)<<i for i,row in enumerate(rows)) for x in range(self.size)]
        else:raise ValueError('encoding')
        assert self.forward[0]==0 and sorted(self.forward)==list(range(self.size))
        self.inverse=[0]*self.size
        for x,y in enumerate(self.forward):self.inverse[y]=x
    def encode(self,x):return self.forward[x]
    def decode(self,x):return self.inverse[x]

class EncodedSource:
    def __init__(self,latent,encoding):self.latent=latent;self.encoding=encoding
    def apply(self,a,x):return self.encoding.encode(self.latent.apply(a,self.encoding.decode(x)))

class LatentWorld:
    def __init__(self,width,family,tag):
        self.width=width;self.size=1<<width;self.family=family;self.tag=tag;rng=rng_for(tag+'|parameters')
        self.c=rng.randrange(1,self.size,2);self.m=rng.randrange(1,self.size,2);self.q=rng.randrange(1,self.size,2);self.b=rng.randrange(self.size)
    def apply(self,a,x):
        if a==0:
            if self.family=='broken_spine':return hashlib.sha256(f'{self.tag}|spine|{x}'.encode()).digest()[0]&(self.size-1)
            return (x+self.c)%self.size
        if self.family=='random_second':return hashlib.sha256(f'{self.tag}|second|{x}'.encode()).digest()[0]&(self.size-1)
        return (self.m*x+self.b+(self.q*x*x if self.family=='quadratic_second' else 0))%self.size
    def rollout(self,x,aa):
        for a in aa:x=self.apply(a,x)
        return x
