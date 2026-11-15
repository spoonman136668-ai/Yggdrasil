"""FKP13 real closed-loop policy heads. No hidden source/environment fields."""
from __future__ import annotations
import copy
import hashlib
import random
import sys
from pathlib import Path
import numpy as np

PARENT=Path(__file__).resolve().parent.parent/"FKP-12"
sys.path.insert(0,str(PARENT))
import source as s12
from model import DirectMemory,indices

ARMS=("DIRECT_ONLINE","COUNT_ONLINE","GRU_ONLINE",
      "DIRECT_FROZEN","GRU_FROZEN","MLP_FROZEN",
      "RANDOM","MACRO8","SHUFFLED_FROZEN")
EPSILON=0.2
UPDATES_EVERY=16
REPLAY_MAX=64

def candidates(rgb_obs,prev):
    if type(prev) is not int or prev not in (0,1,2):
        raise ValueError("FKP13_PREVIOUS_PUBLIC_LABEL")
    pooled=s12.pooled_public_rgb(rgb_obs)
    x=np.zeros((9,204),dtype=np.float32)
    x[:,:192]=pooled
    x[np.arange(9),192+np.arange(9)]=1
    x[:,201+prev]=1
    return x

def arm_rng(seed,name):
    if name not in ARMS or type(seed) is not int:raise ValueError("FKP13_ARM_RNG")
    h=hashlib.sha256(("FKP13:"+name+":"+str(seed)).encode()).digest()
    return random.Random(int.from_bytes(h[:8],"big"))

def choose_index(prob,rng):
    prob=np.asarray(prob,dtype=np.float64)
    if prob.shape!=(9,3) or not np.isfinite(prob).all() or not np.allclose(prob.sum(axis=1),1,atol=1e-5):
        raise ValueError("FKP13_ACTION_POSTERIOR")
    if rng.random()<EPSILON:return rng.randrange(9)
    reward_est=0.1*prob[:,2]-0.05*prob[:,0]
    tie=np.flatnonzero(np.abs(reward_est-np.max(reward_est))<1e-12)
    return int(tie[rng.randrange(len(tie))])

def increment(memory,x,y):
    """Atomic one-event source-observed count write; no gradient or new slots."""
    if type(y) is not int or y not in (0,1,2):
        raise ValueError("FKP13_REAL_SOURCE_LABEL")
    if x.shape!=(1,204):raise ValueError("FKP13_SINGLE_OBSERVATION")
    keys=[int(indices(x,0,memory.ignore_action)[0])]
    if memory.two_hash:keys.append(int(indices(x,1,memory.ignore_action)[0]))
    deltas={}
    for k in keys:deltas[k]=deltas.get(k,0)+1
    for k,d in deltas.items():
        if int(memory.weights[k,y])+d>=2**31-1:
            raise ValueError("FKP13_NUMERIC_CAPACITY_EXCEEDED")
    for k,d in deltas.items():
        memory.weights[k,y]+=d

class Controller:
    def __init__(self,name,direct,counts,trained,shuffled,torch):
        if name not in ARMS:raise ValueError("FKP13_ARM_NAME")
        self.name=name
        self.torch=torch
        if name=="DIRECT_ONLINE":
            self.memory=DirectMemory.restore(direct.snapshot())
        elif name=="COUNT_ONLINE":
            self.memory=DirectMemory.restore(counts.snapshot())
        elif name=="DIRECT_FROZEN":
            self.memory=DirectMemory.restore(direct.snapshot())
        elif name=="SHUFFLED_FROZEN":
            self.memory=DirectMemory.restore(shuffled.snapshot())
        else:self.memory=None
        if name.startswith("GRU_"):
            self.net=copy.deepcopy(trained["GRU"])
        elif name=="MLP_FROZEN":
            self.net=copy.deepcopy(trained["MLP"])
        else:self.net=None
        self.optimizer=(torch.optim.Adam(self.net.parameters(),lr=.001,
                           weight_decay=.0001) if name=="GRU_ONLINE" else None)
        self.learning_updates=0
        self.total_source_observations=0
        self.current_hidden=None
        self.recent=[]

    def new_world(self):
        self.current_hidden=None
        self.recent=[]

    def estimate(self,features):
        if self.memory is not None:
            return self.memory.predict(features),None
        if self.net is None:raise ValueError("FKP13_NO_LEARNED_POSTERIOR")
        self.net.eval()
        with self.torch.no_grad():
            feat=self.torch.from_numpy(features).float()
            if self.name.startswith("GRU_"):
                seq=feat.reshape(9,1,204)
                hidden=(self.current_hidden.expand(1,9,64).contiguous()
                        if self.current_hidden is not None else None)
                out,branches=self.net.recurrent(seq,hidden)
                logits=self.net.head(out[:,0,:])
                return self.torch.softmax(logits,dim=-1).cpu().numpy().astype(np.float64),branches
            return self.torch.softmax(self.net(feat),dim=-1).cpu().numpy().astype(np.float64),None

    def observed(self,features,idx,branches,reward_cls):
        """Only after env.step's actual public outcome, never counterfactual label."""
        if type(idx) is not int or not 0<=idx<9:raise ValueError("FKP13_CHOSEN_ACTION")
        if self.name in ("DIRECT_ONLINE","COUNT_ONLINE"):
            increment(self.memory,features[idx:idx+1],reward_cls)
        if self.name.startswith("GRU_"):
            if branches is None:raise ValueError("FKP13_RECURRENT_BRANCH_MISSING")
            self.current_hidden=branches[:,idx:idx+1,:].detach()
        if self.name=="GRU_ONLINE":
            self.recent.append((features[idx].copy(),int(reward_cls)))
            self.total_source_observations+=1
            if self.total_source_observations%UPDATES_EVERY==0:
                self._online_gru_update()
        elif self.name in ("DIRECT_ONLINE","COUNT_ONLINE"):
            self.total_source_observations+=1

    def _online_gru_update(self):
        rows=self.recent[-REPLAY_MAX:]
        if not rows:return
        x=self.torch.from_numpy(np.stack([f for f,y in rows])).float().unsqueeze(0)
        y=self.torch.tensor([v for f,v in rows],dtype=self.torch.long)
        self.net.train()
        self.optimizer.zero_grad(set_to_none=True)
        output=self.net(x).reshape(-1,3)
        loss=self.torch.nn.functional.cross_entropy(output,y)
        loss.backward()
        self.optimizer.step()
        self.current_hidden=None
        self.learning_updates+=1

    def cold(self,probe_x):
        if self.memory is None:return None
        blob=self.memory.snapshot()
        clone=DirectMemory.restore(blob)
        before=self.memory.predict(probe_x)
        after=clone.predict(probe_x)
        if not np.array_equal(before,after) or clone.snapshot()!=blob:
            raise AssertionError("FKP13_COLD_RESTORE_NOT_EXACT")
        damaged=bytearray(blob);damaged[42]^=1
        try:DirectMemory.restore(bytes(damaged))
        except ValueError:pass
        else:raise AssertionError("FKP13_COLD_TAMPER_ACCEPTED")
        return hashlib.sha256(blob).hexdigest()
