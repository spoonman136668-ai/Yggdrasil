"""FKP04-SRC-V1: owner-only opaque causal transition source, DEV only by default."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib, random

N_MECH=256
N_STATES=4096
N_HIST=N_MECH*N_STATES
N_POOL=128
N_PAID=16
N_HELD=256
DEV_KEY=hashlib.sha256(b'FKP04-public-DEV-only-not-private-science').digest()


def group(seed:int)->str:
    if type(seed) is not int: raise ValueError('SEED_INVALID')
    if 500 <= seed <=515:return 'dev'
    if 1500<=seed<=1563:return 'primary'
    if 2500<=seed<=2515:return 'negative'
    raise ValueError('SEED_OUTSIDE_COHORT')

class Mechanisms:
    def __init__(self,key:bytes):
        if type(key) is not bytes or len(key)<32:raise ValueError('OWNER_KEY_INVALID')
        self.__key=key
    def step(self,mech:int,state:int)->int:
        if type(mech) is not int or not 0<=mech<257:raise ValueError('MECHANISM_INVALID')
        if type(state) is not int or not 0<=state<N_STATES:raise ValueError('STATE_INVALID')
        digest=hashlib.blake2s(mech.to_bytes(2,'big')+state.to_bytes(2,'big'),digest_size=4,key=self.__key).digest()
        return state^(1<<(digest[1]%12)) if digest[0]<32 else state

@dataclass(frozen=True)
class PublicView:
    mechanism_a:int
    mechanism_b:int
    public_pool:tuple[int,...]
    held_states:tuple[int,...]
    state_size:int

class World:
    def __init__(self,seed:int,mechanisms:Mechanisms,*,protected_key:bytes|None=None):
        kind=group(seed)
        if kind!='dev':
            if type(protected_key) is not bytes or len(protected_key)<32:
                raise PermissionError('PROTECTED_EVALUATOR_KEY_REQUIRED')
        elif protected_key is not None:raise ValueError('DEV_MUST_NOT_USE_PROTECTED_KEY')
        self.__kind=kind
        self.__mechanisms=mechanisms
        rr=random.Random(seed^0x3845AC)
        pool=tuple(rr.sample(range(N_STATES),N_POOL))
        held=tuple(x for x in random.Random(seed^0x776621).sample(range(N_STATES),N_STATES) if x not in pool)[:N_HELD]
        if len(held)!=N_HELD:raise AssertionError('HELD_TOO_SMALL')
        self.__held=held
        self.__pool=pool
        # Deterministic source-only pair selection; PUBLIC pair chosen so
        # both candidate causal orders remain distinguishable in action pool.
        for trial in range(300):
            if kind=='negative':
                a,b=256,rr.randrange(N_MECH)
            else:
                a,b=rr.sample(range(N_MECH),2)
            different=sum(self._compose(a,b,x,0)!=self._compose(a,b,x,1) for x in pool)
            if 2<=different<=32:
                break
        else:raise AssertionError('SOURCE_PAIR_NOT_IDENTIFIABLE')
        self.__a=a;self.__b=b
        key=DEV_KEY if kind=='dev' else protected_key
        h=hashlib.blake2s(f'FKP04-ORDER:{seed}'.encode(),key=key,digest_size=4).digest()
        self.__order=h[0]&1
        self.__charged=set()
    def _compose(self,a:int,b:int,x:int,order:int)->int:
        m=self.__mechanisms
        return m.step(b,m.step(a,x)) if order==0 else m.step(a,m.step(b,x))
    def public_view(self)->PublicView:
        return PublicView(self.__a,self.__b,self.__pool,self.__held,N_STATES)
    def observe(self,state:int)->int:
        if type(state) is not int or state not in self.__pool:raise ValueError('NOT_A_PUBLIC_ACTION')
        if state in self.__charged:raise PermissionError('ACTION_DUPLICATED')
        if len(self.__charged)>=N_PAID:raise PermissionError('ACTION_LIMIT_EXCEEDED')
        self.__charged.add(state)
        return self._compose(self.__a,self.__b,state,self.__order)
    def dev_eval(self,states:tuple[int,...])->tuple[int,...]:
        if self.__kind!='dev':raise PermissionError('DEV_EVALUATOR_ONLY')
        if type(states) is not tuple or states!=self.__held:raise ValueError('HELD_INPUT_MISMATCH')
        return tuple(self._compose(self.__a,self.__b,x,self.__order) for x in states)
    def dev_private_order(self)->int:
        if self.__kind!='dev':raise PermissionError('DEV_ONLY')
        return self.__order
    @property
    def charged(self)->int:return len(self.__charged)
