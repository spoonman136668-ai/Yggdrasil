"""FKP12 fully fitted conventional controls; frozen validation-only selection.

PyTorch conventional recurrent GRU, nonrecurrent two-layer MLP and logistic.
No DEV/test observations used for parameter fit or model selection. CPU only.
"""
from __future__ import annotations

import copy
import time

import numpy as np

from model import FEATURES,brier

SEEDS=(1212,3434)
EPOCHS=24
HIDDEN=64
TRAIN_BATCH_SEQ=16
TRAIN_BATCH_FLAT=512
LR=0.001
WEIGHT_DECAY=0.0001


def setup_torch():
    import torch
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    return torch


def make_model(kind,torch):
    from torch import nn
    if kind=="GRU":
        class SequenceModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.recurrent=nn.GRU(input_size=FEATURES,hidden_size=HIDDEN,batch_first=True)
                self.head=nn.Linear(HIDDEN,3)
            def forward(self,x):
                y,_hidden=self.recurrent(x)
                return self.head(y)
        return SequenceModel()
    if kind=="MLP":
        return nn.Sequential(nn.Linear(FEATURES,HIDDEN),nn.Tanh(),
                             nn.Linear(HIDDEN,HIDDEN),nn.Tanh(),
                             nn.Linear(HIDDEN,3))
    if kind=="LOGISTIC":
        return nn.Linear(FEATURES,3)
    raise ValueError("FKP12_CONVENTIONAL_KIND")


def pad_batch(episodes,torch):
    from torch.nn.utils.rnn import pad_sequence
    x=pad_sequence([torch.from_numpy(e["x"]).float() for e in episodes],batch_first=True)
    y=pad_sequence([torch.from_numpy(e["y"]).long() for e in episodes],
                   batch_first=True,padding_value=-100)
    return x,y


def predict(model,kind,episodes,torch):
    model.eval()
    with torch.no_grad():
        if kind=="GRU":
            batch,y=pad_batch(episodes,torch)
            logits=model(batch)
            probs=torch.softmax(logits,dim=-1)
            return [probs[i,:len(e["y"])].cpu().numpy().astype(np.float64)
                    for i,e in enumerate(episodes)]
        return [torch.softmax(model(torch.from_numpy(e["x"]).float()),dim=-1)
                    .cpu().numpy().astype(np.float64) for e in episodes]


def aggregate_brier(predictions,episodes):
    return float(sum(brier(p,e["y"])*len(e["y"]) for p,e in zip(predictions,episodes))/
                 sum(len(e["y"]) for e in episodes))


def train_one(kind,train,valid,torch):
    if kind not in ("GRU","MLP","LOGISTIC"):
        raise ValueError("FKP12_BASELINE_NAME")
    best_model=None;best=1e10;best_details=None
    total_started=time.perf_counter()
    for seed in SEEDS:
        torch.manual_seed(seed)
        m=make_model(kind,torch)
        opt=torch.optim.Adam(m.parameters(),lr=LR,weight_decay=WEIGHT_DECAY)
        generator=torch.Generator().manual_seed(seed)
        best_by_seed=1e10
        for epoch in range(EPOCHS):
            m.train()
            if kind=="GRU":
                order=torch.randperm(len(train),generator=generator).tolist()
                blocks=[ [train[j] for j in order[i:i+TRAIN_BATCH_SEQ]]
                         for i in range(0,len(order),TRAIN_BATCH_SEQ)]
                for episodes in blocks:
                    xx,yy=pad_batch(episodes,torch)
                    opt.zero_grad(set_to_none=True)
                    pred=m(xx)
                    loss=torch.nn.functional.cross_entropy(
                        pred.reshape(-1,3),yy.reshape(-1),ignore_index=-100)
                    loss.backward()
                    opt.step()
            else:
                xx=torch.from_numpy(np.concatenate([e["x"] for e in train])).float()
                yy=torch.from_numpy(np.concatenate([e["y"] for e in train])).long()
                order=torch.randperm(len(xx),generator=generator)
                for start in range(0,len(xx),TRAIN_BATCH_FLAT):
                    sel=order[start:start+TRAIN_BATCH_FLAT]
                    opt.zero_grad(set_to_none=True)
                    pred=m(xx[sel])
                    loss=torch.nn.functional.cross_entropy(pred,yy[sel])
                    loss.backward()
                    opt.step()
            validation=aggregate_brier(predict(m,kind,valid,torch),valid)
            if validation<best:
                best=validation
                best_model=copy.deepcopy(m)
                best_details={"seed":seed,"epoch":epoch+1,"val_brier":best,
                              "parameters":sum(v.numel() for v in m.parameters())}
            if validation<best_by_seed:best_by_seed=validation
    if best_model is None:raise AssertionError("FKP12_NO_FULLY_FITTED_BASELINE")
    best_details["train_wall_seconds"]=time.perf_counter()-total_started
    best_details["full_epochs_per_seed"]=EPOCHS
    best_details["seeds_trained"]=list(SEEDS)
    return best_model,best_details


def train_all(train,valid):
    torch=setup_torch()
    models={};details={}
    for name in ("GRU","MLP","LOGISTIC"):
        m,d=train_one(name,train,valid,torch)
        models[name]=m
        details[name]=d
    return torch,models,details
