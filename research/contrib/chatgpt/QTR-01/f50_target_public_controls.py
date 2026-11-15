#!/usr/bin/env python3
"""F50 conventional public-target adapter: unknown target graph, no oracle.

This does not create target laws or labels. All labels must be supplied by an
external authorized public query outcome; the trained source model is loaded
from an exact-sha checked checkpoint. It never receives target AST or a source
law ID purported to be the unseen target. No F50 DEV first use in this module.
"""
from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path

import numpy as np
import f50_conventional_controls as conventional
import f50_public_corpus as corpus
import f50_source_fit as sourcefit
import f50_worlds as world

SCHEMA = "yggdrasil.qtr01.f50.target-unknown-source-model-cold.v1"
MAX_QUERIES = 64
SUPPORT_EPISODES = conventional.SUPPORT_EPISODES
SOURCE_KINDS = conventional.KINDS


class TargetParityRejected(corpus.PublicSourceRejected):
    pass


def load_source_arm(size,seed,kind,checkpoint_path,checkpoint_sha,source_sha):
    """Factory checks pretrained checkpoint identity before target access."""
    model,metadata=sourcefit.load_checkpoint(
        checkpoint_path,checkpoint_sha,source_sha,
        expected_kind=kind,expected_size=size)
    return TargetPublicArm(size,seed,kind,model,metadata,checkpoint_sha)


class TargetPublicArm:
    def __init__(self,size,seed,kind,trained,metadata,checkpoint_sha):
        world.freeze()
        world._check_bank_size(size)
        world._check_dev_seed(seed)
        if kind not in SOURCE_KINDS or type(metadata) is not dict:
            raise TargetParityRejected("F50_TARGET_UNREGISTERED_MODEL_KIND")
        if (metadata.get("schema")!=sourcefit.SCHEMA
            or metadata.get("kind")!=kind
            or metadata.get("bank_size")!=size
            or metadata.get("frozen_prereg_blob")!=world.PREREG_BLOB
            or metadata.get("no_target_first_use") is not True
            or metadata.get("scientific_pass") is not False
            or metadata.get("source_fit_laws")!=size*4//5
            or metadata.get("source_validation_laws")!=size-size*4//5
            or metadata.get("episodes_per_law")!=world.TRAIN_EPISODES
            or metadata.get("model_training",{}).get("status")!="TRAINED_SOURCE_ONLY"
            or metadata.get("model_training",{}).get("source_training_complete") is not True
            or type(checkpoint_sha) is not str
            or len(checkpoint_sha)!=64
            or any(c not in "0123456789abcdef" for c in checkpoint_sha)):
            raise TargetParityRejected("F50_TARGET_SOURCE_CUSTODY_REJECTED")
        if kind=="graph_conditioned_logistic":
            if (metadata["model_training"].get("target_graph_unknown_compatible") is not True
                or metadata["model_training"].get("validation_target_graph_hidden") is not True):
                raise TargetParityRejected("F50_TARGET_LOGISTIC_GRAPH_LEAKAGE")
            if (type(trained) is not np.ndarray
                or trained.shape!=(conventional.GRAPH_DIM+34+33+1,)
                or not np.isfinite(trained).all()):
                raise TargetParityRejected("F50_TARGET_LOGISTIC_WEIGHT_INVALID")
            self.model=trained.copy()
        else:
            torch,_,_=conventional._torch()
            if (not isinstance(trained,torch.nn.Module)
                or getattr(trained,"kind",None)!=kind):
                raise TargetParityRejected("F50_TARGET_NEURAL_MODEL_INVALID")
            self.model=deepcopy(trained).eval()
            if any(not bool(torch.isfinite(p).all()) for p in self.model.parameters()):
                raise TargetParityRejected("F50_TARGET_NEURAL_NONFINITE")
        self.size,self.seed,self.kind=size,seed,kind
        self.model_sha=checkpoint_sha
        self.source_sha=metadata["candidate_sha"]
        self.source_data_sha=metadata["source_data_sha256"]
        self.pool=world.public_candidate_pool(size,seed)
        self.awaiting=None
        self.events=[]
        self.used=[]
        self.prediction_accesses=0
        self.optimizer_steps=0
        # Strict invariant: target AST/DAG and target-law ID do not exist here.
        self.target_graph_available=False

    def _support(self):
        """At most eight complete public episodes, same support size as FIT."""
        sx=np.zeros((SUPPORT_EPISODES*3,33),dtype=np.float32)
        sy=np.zeros((SUPPORT_EPISODES*3,1),dtype=np.float32)
        for idx,(episode,bits) in enumerate(self.events[-SUPPORT_EPISODES:]):
            a=np.asarray(corpus.action_features(episode),dtype=np.float32)
            sx[idx*3:(idx+1)*3]=a
            sy[idx*3:(idx+1)*3,0]=bits
        return sx,sy

    def probabilities(self,episodes):
        if (type(episodes) not in (list,tuple) or not episodes
            or len(episodes)>world.PUBLIC_QUERIES):
            raise TargetParityRejected("F50_TARGET_PREDICTION_BATCH_INVALID")
        features=np.asarray([corpus.action_features(x) for x in episodes],
                            dtype=np.float32)
        sx,sy=self._support()
        if self.kind=="graph_conditioned_logistic":
            summary=conventional._support_summary(sx,sy)
            # Target graph is deliberately all zeros, even when source-bank
            # graph signatures and target seed are available to the evaluator.
            query=features.reshape(-1,33).astype(np.float64)
            w=self.model
            tail=np.asarray(summary,dtype=np.float64)@w[
                conventional.GRAPH_DIM:conventional.GRAPH_DIM+34]
            logits=query@w[conventional.GRAPH_DIM+34:-1]+tail+w[-1]
            p=1/(1+np.exp(-np.clip(logits,-60,60)))
            answers=p.reshape(len(episodes),3)
        else:
            torch,_,_=conventional._torch()
            with torch.no_grad():
                g=torch.zeros((1,conventional.GRAPH_DIM),dtype=torch.float32)
                known=torch.zeros((1,1),dtype=torch.float32)
                inputs=torch.from_numpy(features.reshape(1,-1,33))
                support_x=torch.from_numpy(sx[None])
                support_y=torch.from_numpy(sy[None])
                answers=torch.sigmoid(
                    self.model(g,support_x,support_y,inputs,known)
                ).numpy().reshape(len(episodes),3)
        if answers.shape!=(len(episodes),3) or not np.isfinite(answers).all():
            raise TargetParityRejected("F50_TARGET_CONVENTIONAL_NONFINITE")
        self.prediction_accesses+=3*len(episodes)
        return tuple(tuple(float(x) for x in row) for row in answers)

    def probability(self,episode):
        return self.probabilities((world.validate_trajectory(episode),))[0]

    def select(self):
        if self.awaiting is not None or len(self.used)>=MAX_QUERIES:
            raise TargetParityRejected("F50_TARGET_QUERY_STATE_INVALID")
        options=[i for i in range(len(self.pool)) if i not in self.used]
        probs=np.asarray(self.probabilities([self.pool[i] for i in options]))
        entropy=-(probs*np.log2(np.clip(probs,1e-12,1))+
                  (1-probs)*np.log2(np.clip(1-probs,1e-12,1)))
        winner=int(np.argmax(entropy.sum(axis=1)))
        self.awaiting=options[winner]
        return self.awaiting,self.pool[self.awaiting]

    def observe(self,index,outcome):
        if (type(index) is not int or index!=self.awaiting
            or index in self.used or len(self.used)>=MAX_QUERIES):
            raise TargetParityRejected("F50_TARGET_UNAUTHORIZED_EVENT_OR_REPLAY")
        episode,bits=corpus.observed_episode(self.pool[index],outcome)
        self.used.append(index)
        self.events.append((episode,bits))
        self.awaiting=None

    @property
    def observed_bits(self):
        return len(self.used)*3

    def cold_checkpoint(self):
        if self.awaiting is not None:
            raise TargetParityRejected("F50_TARGET_COLD_PENDING_EVENT")
        packet={"schema":SCHEMA,"kind":self.kind,"size":self.size,"seed":self.seed,
                "source_sha":self.source_sha,"source_data_sha":self.source_data_sha,
                "source_model_sha256":self.model_sha,
                "used":self.used,
                "events":[[list(episode),list(bits)] for episode,bits in self.events],
                "prediction_accesses":self.prediction_accesses,
                "optimizer_steps":self.optimizer_steps,
                "target_graph_available":False}
        raw=json.dumps(packet,sort_keys=True,separators=(",",":")).encode("ascii")
        return raw+b"."+sha256(raw).hexdigest().encode("ascii")

    @classmethod
    def restore(cls,packet,trained,metadata,checkpoint_sha):
        if type(packet) is not bytes or b"." not in packet:
            raise TargetParityRejected("F50_TARGET_COLD_BAD_ENVELOPE")
        raw,mac=packet.rsplit(b".",1)
        if sha256(raw).hexdigest().encode("ascii")!=mac:
            raise TargetParityRejected("F50_TARGET_COLD_CHECKSUM")
        try:
            obj=json.loads(raw)
            arm=cls(obj["size"],obj["seed"],obj["kind"],trained,metadata,checkpoint_sha)
            if (obj["schema"]!=SCHEMA or obj["target_graph_available"] is not False
                or obj["source_sha"]!=arm.source_sha
                or obj["source_data_sha"]!=arm.source_data_sha
                or obj["source_model_sha256"]!=arm.model_sha):
                raise ValueError("custody mismatch")
            ids=obj["used"]
            if (type(ids) is not list or len(ids)>MAX_QUERIES
                or len(set(ids))!=len(ids)
                or any(type(i) is not int or i<0 or i>=len(arm.pool) for i in ids)
                or len(obj["events"])!=len(ids)):
                raise ValueError("event count")
            events=[corpus.observed_episode(*event) for event in obj["events"]]
            if any(episode!=arm.pool[ids[n]]
                   for n,(episode,_) in enumerate(events)):
                raise ValueError("unapproved public event")
            for key in ("prediction_accesses","optimizer_steps"):
                if type(obj[key]) is not int or obj[key]<0:
                    raise ValueError("accounting")
            if obj["optimizer_steps"]!=0:
                raise ValueError("source model mutated by public adaptation")
            arm.used=ids
            arm.events=events
            arm.prediction_accesses=obj["prediction_accesses"]
            if arm.cold_checkpoint()!=packet:
                raise ValueError("noncanonical")
            return arm
        except (KeyError,TypeError,ValueError,IndexError,world.F50Rejected,
                corpus.PublicSourceRejected) as exc:
            raise TargetParityRejected("F50_TARGET_COLD_STATE_REJECTED") from exc


if __name__=="__main__":
    world.freeze()
    print("F50_TARGET_UNKNOWN_GRAPH_CONVENTIONAL_INTERFACE_READY_NO_DEV_FIRST_USE")
