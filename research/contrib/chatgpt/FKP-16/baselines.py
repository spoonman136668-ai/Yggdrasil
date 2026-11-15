"""FKP-16 fully trained recurrent and nonrecurrent 16-step value controls.

All 9 true public branch-return targets TRAIN only; select using validation MSE.
Each seed gets all 24 epochs; no DEV source in fitting or checkpoint selection.
"""
from __future__ import annotations
import copy
import time
import numpy as np

from learners import DIM,mse

SEEDS=(1515,2626)
EPOCHS=24
HIDDEN=64
LR=.001
WEIGHT_DECAY=.0001
BATCH=16

def torch_runtime():
    import torch
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    return torch


def model_new(kind,torch):
    from torch import nn
    if kind=="GRU":
        class Net(nn.Module):
            def __init__(self):
                super().__init__()
                self.gru=nn.GRU(DIM,HIDDEN,batch_first=True)
                self.head=nn.Linear(HIDDEN,9)
            def forward(self,seq,lengths):
                packed=nn.utils.rnn.pack_padded_sequence(
                    seq,lengths.cpu(),batch_first=True,enforce_sorted=False)
                _out,hidden=self.gru(packed)
                return self.head(hidden[-1])
        return Net()
    if kind=="MLP":
        return nn.Sequential(nn.Linear(DIM,HIDDEN),nn.Tanh(),
                             nn.Linear(HIDDEN,HIDDEN),nn.Tanh(),
                             nn.Linear(HIDDEN,9))
    raise ValueError("FKP15_UNQUALIFIED_BASELINE")


def batch_data(rows,kind,torch,labels_required=True):
    if kind=="MLP":
        x=torch.from_numpy(np.stack([r["context"] for r in rows])).float()
        lengths=None
    elif kind=="GRU":
        from torch.nn.utils.rnn import pad_sequence
        seq=[torch.from_numpy(r["sequence"]).float() for r in rows]
        lengths=torch.tensor([len(s) for s in seq],dtype=torch.long)
        x=pad_sequence(seq,batch_first=True)
    else:raise ValueError("FKP15_KIND")
    y=(torch.from_numpy(np.stack([r["returns"] for r in rows])).float()
       if labels_required else None)
    return x,lengths,y


def prediction(net,kind,rows,torch):
    net.eval()
    with torch.no_grad():
        if not rows:return np.empty((0,9))
        out=[]
        for start in range(0,len(rows),BATCH):
            subset=rows[start:start+BATCH]
            x,lengths,_y=batch_data(subset,kind,torch,labels_required=False)
            values=net(x,lengths) if kind=="GRU" else net(x)
            out.append(values.detach().cpu().numpy().astype(np.float64))
        return np.vstack(out)


def fit_kind(kind,train,val,torch):
    if kind not in ("GRU","MLP"):raise ValueError("FKP15_KIND")
    if not train or not val:raise ValueError("FKP15_NONEMPTY_FIT_REQUIRED")
    chosen=None
    best=float("inf")
    details=None
    started=time.perf_counter()
    for seed in SEEDS:
        torch.manual_seed(seed)
        net=model_new(kind,torch)
        optim=torch.optim.Adam(net.parameters(),lr=LR,weight_decay=WEIGHT_DECAY)
        generator=torch.Generator().manual_seed(seed)
        for epoch in range(EPOCHS):
            net.train()
            order=torch.randperm(len(train),generator=generator).tolist()
            for i in range(0,len(order),BATCH):
                rows=[train[k] for k in order[i:i+BATCH]]
                x,lengths,y=batch_data(rows,kind,torch)
                optim.zero_grad(set_to_none=True)
                value=net(x,lengths) if kind=="GRU" else net(x)
                loss=torch.nn.functional.mse_loss(value,y)
                loss.backward()
                optim.step()
            y=np.stack([r["returns"] for r in val])
            score=mse(prediction(net,kind,val,torch),y)
            if score<best:
                best=score
                chosen=copy.deepcopy(net)
                details={"best_seed":seed,"best_epoch":epoch+1,
                         "best_val_mse":score,
                         "parameters":sum(x.numel() for x in net.parameters())}
    if chosen is None:raise AssertionError("FKP15_NOT_FULLY_TRAINED")
    details.update({"epochs_per_seed":EPOCHS,"seeds_trained":list(SEEDS),
                    "train_wall_seconds":round(time.perf_counter()-started,6)})
    return chosen,details


def fit_models(train,val):
    torch=torch_runtime()
    learned={}
    receipts={}
    for kind in ("GRU","MLP"):
        learned[kind],receipts[kind]=fit_kind(kind,train,val,torch)
    return torch,learned,receipts
