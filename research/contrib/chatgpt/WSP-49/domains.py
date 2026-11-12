"""Evaluator-owned latent worlds and encodings; never supplied to the learner."""
from frozen_world import World,rng_for

class LatentWorld:
    def __init__(self,width,family,tag):
        self.width=width;self.size=1<<width;self.family=family;self.half=width//2;self.side=1<<self.half
        rng=rng_for(tag+'|parameters')
        self.c0=rng.randrange(1,self.size,2);self.m=rng.randrange(1,self.size,2);self.c1=rng.randrange(self.size)
        self.s0=rng.randrange(1,8);self.s1=rng.randrange(1,8)
        self.g0=rng.randrange(1,self.side,2);self.g1=rng.randrange(1,self.side,2)
        self.frozen=World(width,'linear' if family=='affine_bits' else 'arbitrary_hash',tag)
    def apply(self,a,state):
        if self.family in ('affine_bits','random_map'):return self.frozen.apply(a,state)
        if self.family=='modular_arithmetic':return (state+self.c0)%self.size if a==0 else (self.m*state+self.c1)%self.size
        if self.family=='saturating_counter':return min(self.size-1,state+self.s0) if a==0 else max(0,state-self.s1)
        lo=state&(self.side-1);hi=state>>self.half
        if self.family=='coupled_grid':
            if a==0:lo,hi=(lo+self.g0)%self.side,(hi+(lo&1))%self.side
            else:lo,hi=(lo+(hi&1))%self.side,(hi+self.g1)%self.side
        elif self.family=='checksum_machine':
            if a==0:hi=(hi+self.g0)%self.side;lo^=hi
            else:hi^=((lo<<1)|(lo>>(self.half-1)))&(self.side-1);lo=(lo+self.g1)%self.side
        else:raise ValueError('family')
        return lo|(hi<<self.half)
    def rollout(self,x,actions):
        for a in actions:x=self.apply(a,x)
        return x

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
