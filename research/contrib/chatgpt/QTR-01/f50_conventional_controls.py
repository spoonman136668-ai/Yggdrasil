#!/usr/bin/env python3
"""F50 law-conditioned conventional meta-learning, strictly source-only.

All three controls ingest the lossless PublicFIT DAG and its 64 observed
source episodes. Source-law-disjoint VALIDATION data are evaluated, never
backpropagated or optimized upon. F50 target ASTs and sealed evaluator data
are not imported. This is implementation, NOT a completed source fit.
"""
from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
import json
import math
from time import process_time

import numpy as np
import f50_public_corpus as public
import f50_worlds as world

SCHEMA = "yggdrasil.qtr01.f50.law-conditioned-controls.v1"
KINDS = ("graph_conditioned_gru", "law_conditioned_set_mlp",
         "graph_conditioned_logistic")
GRAPH_DIM = 15 * 38 + 2 * 15 * 15 + 15
ACTION_DIM = 33
HIDDEN = 128
SUPPORT_EPISODES = 8
EPISODES_PER_LAW = 64
BATCH = 128
LR = 0.001
PATIENCE = 20
MAX_EPOCHS = 200
SEED = 11
L2 = .001
ITERATIONS = 500
TOLERANCE = 1e-8


class ConventionalRejected(public.PublicSourceRejected):
    pass


def source_graph_vector(graph):
    """Injective flattening: all node attributes and both directed edges."""
    feats, left, right, mask = public.graph_one_hot(graph)
    vector = np.asarray(
        [v for row in feats for v in row]
        + [v for row in left for v in row]
        + [v for row in right for v in row]
        + list(mask), dtype=np.float32)
    if vector.shape != (GRAPH_DIM,):
        raise ConventionalRejected("F50_LOSSLESS_GRAPH_VECTOR_BAD_SHAPE")
    return vector


def source_records(size, law_id, *, validation=False):
    """Exactly 64 episodes; access a whole source law in one of two lanes."""
    world.freeze()
    world._check_bank_size(size)
    fit, val = world.source_split(size)
    if (type(law_id) is not int or law_id not in (val if validation else fit)
        or type(validation) is not bool):
        raise ConventionalRejected("F50_SOURCE_LAW_SPLIT_VIOLATION")
    # The same PublicFIT shared access path is used for every FIT arm.
    if validation:
        # Validation-only: NEVER used in gradient, optimizer or FIT cache.
        graph = public.encode_source_graph(world.source_bank(size)[law_id])
        rows = world.source_training_row(size, law_id, validation=True)
    else:
        corpus = public.PublicFIT(size)
        graph = corpus.source_graph(law_id)
        rows = corpus.source_episodes(law_id)
    if len(rows) != EPISODES_PER_LAW:
        raise ConventionalRejected("F50_INCOMPLETE_SOURCE_EPISODES")
    actions = np.asarray([public.action_features(t) for t, _ in rows],
                         dtype=np.float32)
    outcomes = np.asarray([bits for _,bits in rows], dtype=np.float32)
    if (actions.shape != (64, 3, ACTION_DIM)
        or outcomes.shape != (64, 3)
        or not np.isfinite(actions).all() or not np.isfinite(outcomes).all()):
        raise ConventionalRejected("F50_SOURCE_TENSORS_BAD_SHAPE")
    return source_graph_vector(graph), actions, outcomes


def source_meta_episode(graph, actions, labels, *, reverse=False):
    """Eight support episodes, 56 unseen query episodes; no label peeking.

    Reverse rotates support/query membership deterministically, so every
    source FIT trajectory is used in the supervised source objective.
    """
    if (np.shape(graph) != (GRAPH_DIM,)
        or np.shape(actions) != (64,3,33)
        or np.shape(labels) != (64,3)):
        raise ConventionalRejected("F50_SOURCE_META_EPISODE_SHAPE")
    indices = np.arange(64)
    if reverse:
        indices = np.roll(indices, -32)
    support = indices[:SUPPORT_EPISODES]
    query = indices[SUPPORT_EPISODES:]
    sx = actions[support].reshape(-1,33)
    sy = labels[support].reshape(-1,1)
    qx = actions[query].reshape(-1,33)
    qy = labels[query].reshape(-1)
    return (graph, sx, sy, qx, qy)


def graph_mask_for_batch(law_ids, epoch, *, validation=False):
    """Deterministic source-law graph masking for target-law-unknown transfer."""
    if validation:
        return np.zeros((len(law_ids),1),dtype=np.float32)
    return np.asarray([[(int(law_id)+epoch) % 2] for law_id in law_ids],
                      dtype=np.float32)


def _torch():
    try:
        import torch
        import torch.nn as nn
        import torch.nn.functional as F
    except ImportError as exc:
        raise ConventionalRejected("F50_TORCH_CPU_DEPENDENCY_MISSING") from exc
    return torch,nn,F


def create_neural(kind):
    """128-state real GRU or two-hidden-layer 128-wide set MLP with DAG input."""
    if kind not in KINDS[:2]:
        raise ConventionalRejected("F50_UNREGISTERED_NEURAL_KIND")
    torch,nn,_ = _torch()
    torch.manual_seed(SEED)
    class Neural(nn.Module):
        def __init__(self):
            super().__init__()
            self.kind = kind
            self.graph = nn.Sequential(nn.Linear(GRAPH_DIM,HIDDEN),
                                       nn.ReLU())
            if kind == "graph_conditioned_gru":
                self.support = nn.GRU(
                    input_size=ACTION_DIM + 1 + HIDDEN,
                    hidden_size=HIDDEN, batch_first=True)
                self.head = nn.Sequential(nn.Linear(HIDDEN*2+ACTION_DIM,HIDDEN),
                                          nn.ReLU(),nn.Linear(HIDDEN,1))
            else:
                self.support = nn.Sequential(nn.Linear(ACTION_DIM+1,HIDDEN),
                                             nn.ReLU())
                self.head = nn.Sequential(nn.Linear(HIDDEN*2+ACTION_DIM,HIDDEN),
                                          nn.ReLU(),nn.Linear(HIDDEN,HIDDEN),
                                          nn.ReLU(),nn.Linear(HIDDEN,1))
        def forward(self, graph, support_x, support_y, query_x, known):
            if (graph.ndim!=2 or graph.shape[1]!=GRAPH_DIM
                or support_x.ndim!=3 or support_x.shape[2]!=33
                or query_x.ndim!=3 or query_x.shape[2]!=33
                or support_y.shape!=support_x.shape[:2]+(1,)
                or known.shape!=(len(graph),1)):
                raise ConventionalRejected("F50_NEURAL_BATCH_SHAPE_DRIFT")
            g=self.graph(graph)*known
            support=torch.cat((support_x,support_y),dim=-1)
            if self.kind=="graph_conditioned_gru":
                seq=torch.cat((support,
                               g.unsqueeze(1).expand(-1,support.shape[1],-1)),
                              dim=-1)
                _,hidden=self.support(seq)
                summary=hidden[-1]
            else:
                summary=self.support(support).mean(dim=1)
            conditioning=torch.cat((summary,g),dim=1)
            expanded=conditioning.unsqueeze(1).expand(-1,query_x.shape[1],-1)
            logits=self.head(torch.cat((expanded,query_x),dim=-1))
            return logits.squeeze(-1)
    return Neural()


def meta_batch(law_data, law_ids, *, epoch=0, validation=False):
    """Packed law-disjoint per-law meta episodes, preserving label boundaries."""
    if not law_ids:
        raise ConventionalRejected("F50_EMPTY_META_BATCH")
    data=[source_meta_episode(*law_data[i],reverse=bool(epoch%2))
          for i in law_ids]
    graphs=np.stack([v[0] for v in data])
    support_x=np.stack([v[1] for v in data])
    support_y=np.stack([v[2] for v in data])
    query_x=np.stack([v[3] for v in data])
    query_y=np.stack([v[4] for v in data])
    if len({len(v[3]) for v in data})!=1:
        raise ConventionalRejected("F50_META_QUERY_LENGTH_DRIFT")
    return (graphs,support_x,support_y,query_x,query_y,
            graph_mask_for_batch(law_ids,epoch,validation=validation))


def _to_torch(parts):
    torch,_,_=_torch()
    return tuple(torch.from_numpy(np.ascontiguousarray(x,dtype=np.float32))
                 for x in parts)


def one_neural_step(model, optimizer, batch):
    """One actual Adam(0.001) source-meta update, no target first use."""
    _,_,F=_torch()
    graph,sx,sy,qx,qy,known=_to_torch(batch)
    optimizer.zero_grad(set_to_none=True)
    logits=model(graph,sx,sy,qx,known)
    if logits.shape!=qy.shape:
        raise ConventionalRejected("F50_NEURAL_SOURCE_TARGET_SHAPE")
    loss=F.binary_cross_entropy_with_logits(logits,qy)
    if not bool(np.isfinite(float(loss.item()))):
        raise ConventionalRejected("F50_NONFINITE_NEURAL_LOSS")
    loss.backward()
    optimizer.step()
    return float(loss.item())


def evaluate_neural_source(model, law_data, law_ids):
    torch,_,F=_torch()
    model.eval()
    losses=[]
    with torch.no_grad():
        for start in range(0,len(law_ids),BATCH):
            part=law_ids[start:start+BATCH]
            if not part:
                continue
            batch=meta_batch(law_data,part,validation=True)
            graphs,sx,sy,qx,qy,known=_to_torch(batch)
            loss=F.binary_cross_entropy_with_logits(
                model(graphs,sx,sy,qx,known),qy,reduction="sum")
            losses.append((float(loss.item()),qy.numel()))
    model.train()
    if not losses or not all(math.isfinite(x) for x,_ in losses):
        raise ConventionalRejected("F50_VALIDATION_LOSS_INVALID")
    return sum(x for x,_ in losses)/sum(n for _,n in losses)


def train_neural_source(kind, law_data, fit_ids, val_data, val_ids, *,
                        max_epochs=MAX_EPOCHS, patience=PATIENCE,
                        budget_seconds=3600):
    """Fully fitted source-only meta-learner, law-disjoint early stopping.

    The 60-minute/4096-law hard CPU budget is a fail-closed resource stop.
    The result is NOT a source-training PASS if that budget is exhausted.
    """
    if (kind not in KINDS[:2] or max_epochs != MAX_EPOCHS
        or patience != PATIENCE or type(fit_ids) is not tuple
        or type(val_ids) is not tuple or not fit_ids or not val_ids
        or set(fit_ids)&set(val_ids) or budget_seconds<=0):
        raise ConventionalRejected("F50_NEURAL_SOURCE_TRAIN_PROTOCOL_DRIFT")
    torch,_,_=_torch()
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    model=create_neural(kind)
    optimizer=torch.optim.Adam(model.parameters(),lr=LR)
    rng=np.random.default_rng(SEED)
    best=float("inf")
    save=None
    waits=0
    start=process_time()
    receipt={"kind":kind,"validation_law_disjoint":True,
             "source_fit_laws":len(fit_ids),"source_validation_laws":len(val_ids),
             "epochs":0,"optimizer_steps":0,"protocol":"F50-meta-source-only"}
    for epoch in range(max_epochs):
        order=rng.permutation(fit_ids).tolist()
        for off in range(0,len(order),BATCH):
            if process_time()-start>budget_seconds:
                receipt.update(status="RESOURCE_STOP",scientific_pass=False,
                               source_training_complete=False,
                               cpu_seconds=process_time()-start)
                return None,receipt
            batch=meta_batch(law_data,order[off:off+BATCH],epoch=epoch)
            one_neural_step(model,optimizer,batch)
            receipt["optimizer_steps"]+=1
        val=evaluate_neural_source(model,val_data,val_ids)
        receipt["epochs"]=epoch+1
        if val<best-1e-12:
            best=val
            save=deepcopy(model.state_dict())
            waits=0
        else:
            waits+=1
            if waits>=patience:
                break
    model.load_state_dict(save)
    receipt.update(status="TRAINED_SOURCE_ONLY",source_training_complete=True,
                   best_validation_bce=best,
                   cpu_seconds=process_time()-start,scientific_pass=False)
    return model,receipt


def _support_summary(sx,sy):
    """Graph-free meta-statistic for unknown target laws; no target AST input."""
    if sx.shape != (SUPPORT_EPISODES*3,ACTION_DIM) or sy.shape!=(SUPPORT_EPISODES*3,1):
        raise ConventionalRejected("F50_LOGISTIC_SUPPORT_SHAPE")
    return np.concatenate(((sx*sy).mean(axis=0),
                           np.asarray([float(sy.mean())],dtype=np.float32)))


def logistic_source_rows(data, *, hide_graph=False):
    """Explicit full lossless graph vector and public source episodic context."""
    graph,sx,sy,qx,qy=source_meta_episode(*data)
    if type(hide_graph) is not bool:
        raise ConventionalRejected("F50_LOGISTIC_GRAPH_VISIBILITY_INVALID")
    # New target law's AST/DAG is unknown. FIT examples must include an
    # unknown-law graph state; validation always measures that same state.
    if hide_graph:
        graph=np.zeros_like(graph)
    summary=_support_summary(sx,sy)
    samples=np.concatenate((np.broadcast_to(graph,(len(qy),GRAPH_DIM)),
                            np.broadcast_to(summary,(len(qy),34)),
                            qx),axis=1)
    if samples.shape!=(len(qy),GRAPH_DIM+34+ACTION_DIM):
        raise ConventionalRejected("F50_LOGISTIC_GRAPH_INPUT_DIM")
    return np.asarray(samples,dtype=np.float64),np.asarray(qy,dtype=np.float64)


def logistic_fit_source(law_data,fit_ids,val_data,val_ids,*,max_iter=ITERATIONS,
                        tolerance=TOLERANCE,budget_seconds=3600):
    """Full-batch deterministic L-BFGS with fixed L2, no validation gradients."""
    if (max_iter!=ITERATIONS or tolerance!=TOLERANCE
        or not fit_ids or not val_ids or set(fit_ids)&set(val_ids)):
        raise ConventionalRejected("F50_LOGISTIC_SOLVER_PROTOCOL_DRIFT")
    try:
        from scipy.special import expit
        from scipy.optimize import minimize
        from scipy.sparse import csr_matrix, vstack, hstack
    except ImportError as exc:
        raise ConventionalRejected("F50_SCIPY_REQUIRED_FOR_FULL_LBFGS") from exc
    start=process_time()
    matrices=[]
    labels=[]
    for law in fit_ids:
        # Alternate public source graph visibility at FIT time. All source
        # graph/episode information is available; hiding it from this predictor
        # prevents an untrainable target-graph oracle dependency.
        x,y=logistic_source_rows(law_data[law],hide_graph=((law+SEED)%2==0))
        matrices.append(csr_matrix(x))
        labels.append(y)
        if process_time()-start>budget_seconds:
            return None,{"kind":KINDS[2],"status":"RESOURCE_STOP",
                         "source_training_complete":False,
                         "cpu_seconds":process_time()-start,"scientific_pass":False}
    x=vstack(matrices,format="csr")
    x=hstack((x,np.ones((x.shape[0],1))),format="csr")
    y=np.concatenate(labels)
    w=np.zeros(x.shape[1],dtype=np.float64)
    pen=np.ones(len(w),dtype=np.float64)*L2
    pen[-1]=0
    def objective(p):
        z=x@p
        prob=expit(z)
        logloss=np.mean(np.logaddexp(0,z)-y*z)
        loss=logloss + .5*np.sum(pen*p*p)
        gradient=(x.T@(prob-y))/len(y)+pen*p
        return float(loss),np.asarray(gradient).reshape(-1)
    result=minimize(objective,w,jac=True,method="L-BFGS-B",
                    options={"maxiter":max_iter,"gtol":tolerance,"ftol":1e-12})
    cost=process_time()-start
    if cost>budget_seconds or not np.isfinite(result.x).all():
        return None,{"kind":KINDS[2],"status":"RESOURCE_STOP",
                     "source_training_complete":False,
                     "cpu_seconds":cost,"scientific_pass":False}
    scores=[]
    for law in val_ids:
        xval,yval=logistic_source_rows(val_data[law],hide_graph=True)
        z=xval@result.x[:-1]+result.x[-1]
        scores.append(float(np.mean(np.logaddexp(0,z)-yval*z)))
    receipt={"kind":KINDS[2],"status":"TRAINED_SOURCE_ONLY",
             "source_training_complete":True,"validation_law_disjoint":True,
             "source_fit_laws":len(fit_ids),
             "source_validation_laws":len(val_ids),
             "maxiter":ITERATIONS,"iterations":int(result.nit),
             "solver_success":bool(result.success),
             "final_gradient_max":float(np.max(np.abs(objective(result.x)[1]))),
             "source_validation_bce":float(np.mean(scores)),
             "optimizer":"deterministic full-batch scipy L-BFGS-B",
             "target_graph_unknown_compatible":True,
             "validation_target_graph_hidden":True,
             "source_graph_mask_policy":"FIT: (law_id+11)%2==0; VALIDATION: all hidden",
             "cpu_seconds":cost,"scientific_pass":False}
    return result.x.copy(),receipt


def pretraining_dataset(size, *, validation=False):
    """Shared source-only dataset, high-first, disjoint by whole law."""
    world.freeze()
    world._check_bank_size(size)
    fit,val=world.source_split(size)
    ids=tuple(sorted(val if validation else fit))
    return {law:source_records(size,law,validation=validation)
            for law in ids}


def dataset_receipt(size, fit_data, validation_data):
    fit,val=world.source_split(size)
    if (set(fit_data)!=fit or set(validation_data)!=val
        or fit&val or len(fit)+len(val)!=size):
        raise ConventionalRejected("F50_SOURCE_DATASET_CUSTODY_INVALID")
    stream=sha256()
    for group,collection in (("FIT",fit_data),("VALIDATION",validation_data)):
        for i in sorted(collection):
            graph,episodes,outcomes=collection[i]
            stream.update(group.encode("ascii"))
            stream.update(i.to_bytes(4,"little"))
            for array in (graph,episodes,outcomes):
                stream.update(np.ascontiguousarray(array,dtype="<f4").tobytes())
    return {"schema":SCHEMA,"size":size,
            "fit_laws":len(fit),"validation_laws":len(val),
            "episodes_per_source_law":64,
            "source_data_sha256":stream.hexdigest(),
            "frozen_prereg_blob":world.PREREG_BLOB,
            "dev_target_outcomes":0,"scientific_pass":False}


if __name__=="__main__":
    world.freeze()
    print("F50_LAW_CONDITIONED_THREE_CONTROLS_DEFINED_NO_SOURCE_TRAINING_CLAIM")
