#!/usr/bin/env python3
"""F50 native tokenless causal-slot composition over PUBLIC interventions only.

No accepted Yggdrasil substrate change. The rule constructor gets exactly the
same FIT source graphs and noisy FIT rows available to conventional controls.
No DEV target AST, evaluator truth, reserved seed, or hidden representation.
"""
from hashlib import sha256
import json
import math

import f50_worlds as world
import f50_public_corpus as public

SCHEMA = "yggdrasil.qtr01.f50.native-association-cold.v1"
MAX_QUERIES = 64
PROPOSALS = 2048
MEMORY = 32
ABLATIONS = ("none","no_causal_slot_retention","public_outcome_shuffle",
             "random_proposals_equal_2048","permuted_action_outcome_alignment")
QUERY_POLICIES = ("native","random","uniform")


class NativeRejected(public.PublicSourceRejected):
    pass


def _public_prediction(rule, episode):
    a,b,c,ctx=world.validate_trajectory(episode)
    return (world.evaluate(rule,a,0,0,ctx),
            world.evaluate(rule,b,a,0,ctx),
            world.evaluate(rule,c,b,a,ctx))


def _node_count(rule):
    return 1 if rule[0]=="leaf" else 1+sum(_node_count(x) for x in rule[1:])


def _strast(rule):
    return json.dumps(rule,separators=(",",":"))


def _tupleast(raw):
    if not isinstance(raw,list):
        raise NativeRejected("F50_COLD_AST_INVALID")
    return tuple(_tupleast(x) if isinstance(x,list) else x for x in raw)


class NativeAssociation:
    """Evidence-first causal hypothesis construction; 2048 attempts/event."""

    def __init__(self, size, dev_seed, *, mode="none", query_policy="native"):
        world.freeze()
        if mode not in ABLATIONS or query_policy not in QUERY_POLICIES:
            raise NativeRejected("F50_NATIVE_POLICY_NOT_REGISTERED")
        world._check_bank_size(size)
        world._check_dev_seed(dev_seed)
        self.size,self.seed,self.mode,self.policy=size,dev_seed,mode,query_policy
        self.corpus=public.PublicFIT(size)
        self.pool=world.public_candidate_pool(size,dev_seed)
        self.fit_ids=self.corpus.ids
        self.used=[]
        self.pending=None
        self.observations=[]
        self.proposals=0
        self.prediction_accesses=0
        self.contradictions=0
        self.hypotheses=self._initial()

    def _initial(self):
        indices=[]
        for i in range(MEMORY):
            index=world.random_uint("F50/native-initial/v1",self.size,i)%len(self.fit_ids)
            lawid=self.fit_ids[index]
            if lawid not in indices:
                indices.append(lawid)
        # The candidate source-law graphs are public, as for every control.
        return tuple(public.decode_source_graph(self.corpus.source_graph(i)) for i in indices)

    def _new_proposal(self, step, ordinal):
        key=world.random_uint("F50/native-construct/v1",self.size,self.seed,step,ordinal)
        origin=world.random_uint("F50/native-base/v1",self.size,step,ordinal)
        take_retained=(self.mode!="random_proposals_equal_2048" and
                       step>0 and self.hypotheses and (key&3)!=0)
        if take_retained:
            base=self.hypotheses[(origin>>8)%len(self.hypotheses)]
        else:
            lawid=self.fit_ids[origin%len(self.fit_ids)]
            base=public.decode_source_graph(self.corpus.source_graph(lawid))
        newleaf=world.leaf((key>>11)%world.N_VARIABLES)
        second=world.leaf((key>>17)%world.N_VARIABLES)
        op=("and","or","xor")[key%3]
        form=(key>>21)%4
        if form==0:
            candidate=(op,base,newleaf)
        elif form==1:
            candidate=(op,newleaf,base)
        elif form==2:
            candidate=("xor",base,("and",newleaf,second))
        else:
            candidate=("and",("not",newleaf),("xor",base,second))
        if world.ast_depth(candidate)>6:
            # Deterministic bounded legal fallback, still charged as one attempt.
            candidate=("xor",world.leaf((key>>27)%33),("and",newleaf,second))
        return candidate

    def _score(self, rule):
        mismatches=0
        for episode,bits in self.observations:
            compared=episode
            if self.mode=="permuted_action_outcome_alignment":
                a,b,c,context=episode
                compared=(b,c,a,context)
            pred=_public_prediction(rule,compared)
            self.prediction_accesses+=3
            mismatches+=sum(p!=y for p,y in zip(pred,bits))
        return (mismatches*1000+_node_count(rule),_node_count(rule),_strast(rule))

    def observe(self, index, outcomes):
        if (type(index) is not int or self.pending is None
            or index!=self.pending or index in self.used):
            raise NativeRejected("F50_NATIVE_UNAUTHORIZED_OR_REPLAYED_EVENT")
        _,bits=public.observed_episode(self.pool[index],outcomes)
        if len(self.used)>=MAX_QUERIES:
            raise NativeRejected("F50_NATIVE_QUERY_BUDGET_EXHAUSTED")
        if self.hypotheses:
            predicted=_public_prediction(self.hypotheses[0],self.pool[index])
            self.prediction_accesses+=3
            self.contradictions+=int(predicted!=bits)
        if self.mode=="public_outcome_shuffle":
            bits=(bits[1],bits[2],bits[0])
        self.observations.append((self.pool[index],bits))
        step=len(self.used)
        candidates=list(self.hypotheses)
        for ordinal in range(PROPOSALS):
            candidates.append(self._new_proposal(step,ordinal))
        self.proposals+=PROPOSALS
        seen=set()
        ranked=[]
        for rule in candidates:
            exact=world.anf(rule)
            if exact in seen:
                continue
            seen.add(exact)
            ranked.append((self._score(rule),rule))
        ranked.sort(key=lambda x:x[0])
        self.hypotheses=tuple(rule for _,rule in ranked[:MEMORY])
        self.used.append(index)
        self.pending=None
        if self.mode=="no_causal_slot_retention":
            self.observations.clear()
            self.hypotheses=self._initial()

    def probability(self,episode):
        tr=world.validate_trajectory(episode)
        if not self.hypotheses:
            return (0.5,0.5,0.5)
        # Bounded hypothesis posterior (10% public label-noise model).
        rules=self.hypotheses[:16]
        scores=[self._score(rule)[0]/1000 for rule in rules]
        peak=min(scores)
        weights=[math.exp(-math.log(9)*(s-peak)) for s in scores]
        predictions=[_public_prediction(rule,tr) for rule in rules]
        self.prediction_accesses+=3*len(rules)
        total=sum(weights)
        return tuple(sum(weight*(0.9 if pred[i] else 0.1)
                         for weight,pred in zip(weights,predictions))/total
                     for i in range(3))

    def select(self):
        if self.pending is not None or len(self.used)>=MAX_QUERIES:
            raise NativeRejected("F50_NATIVE_QUERY_STATE_INVALID")
        unseen=[i for i in range(len(self.pool)) if i not in self.used]
        if self.policy=="uniform":
            selected=unseen[0]
        elif self.policy=="random":
            selected=unseen[world.random_uint(
                "F50/public-random/v1",self.size,self.seed,len(self.used))%len(unseen)]
        else:
            witnesses=self.hypotheses[:8]
            def score(index):
                votes=[_public_prediction(rule,self.pool[index]) for rule in witnesses]
                self.prediction_accesses+=3*len(votes)
                return sum(n*(len(votes)-n) for n in (sum(y[k] for y in votes) for k in range(3)))
            selected=max(unseen,key=lambda i:(score(i),-i))
        self.pending=selected
        return selected,self.pool[selected]

    @property
    def observed_bits(self):
        return len(self.used)*3

    def cold_checkpoint(self):
        if self.pending is not None:
            raise NativeRejected("F50_COLD_PENDING_QUERY_UNSAFE")
        state={"schema":SCHEMA,"bank_size":self.size,"seed":self.seed,
               "mode":self.mode,"query_policy":self.policy,
               "fit_graph_sha":self.corpus.digest_for_fit_graphs(),
               "used":self.used,"events":[[list(a),list(bits)] for a,bits in self.observations],
               "rules":[json.loads(_strast(rule)) for rule in self.hypotheses],
               "proposals":self.proposals,
               "contradictions":self.contradictions,
               "prediction_accesses":self.prediction_accesses}
        raw=json.dumps(state,sort_keys=True,separators=(",",":")).encode("ascii")
        return raw+b"."+sha256(raw).hexdigest().encode("ascii")

    @classmethod
    def restore(cls,checkpoint):
        if type(checkpoint) is not bytes or b"." not in checkpoint:
            raise NativeRejected("F50_COLD_CHECKSUM_INVALID")
        body,checksum=checkpoint.rsplit(b".",1)
        if sha256(body).hexdigest().encode("ascii")!=checksum:
            raise NativeRejected("F50_COLD_CHECKSUM_INVALID")
        try:
            state=json.loads(body)
            if state["schema"]!=SCHEMA:
                raise ValueError("schema")
            out=cls(state["bank_size"],state["seed"],
                    mode=state["mode"],query_policy=state["query_policy"])
            if state["fit_graph_sha"]!=out.corpus.digest_for_fit_graphs():
                raise ValueError("source bank drift")
            indices=state["used"]
            if (type(indices) is not list or len(indices)>MAX_QUERIES
                or len(set(indices))!=len(indices)
                or any(type(i) is not int or not 0<=i<len(out.pool) for i in indices)):
                raise ValueError("public action receipts")
            events=[public.observed_episode(*entry) for entry in state["events"]]
            if (len(events)>len(indices) or
                (state["mode"]!="no_causal_slot_retention" and len(events)!=len(indices))):
                raise ValueError("observations")
            if state["mode"]=="no_causal_slot_retention" and events:
                raise ValueError("no retention")
            rules=tuple(_tupleast(x) for x in state["rules"])
            if (not 1<=len(rules)<=MEMORY or
                any(world.ast_depth(x)>6 for x in rules) or
                len(set(world.anf(x) for x in rules))!=len(rules)):
                raise ValueError("rule shapes")
            for episode,_ in events:
                if episode not in [out.pool[i] for i in indices]:
                    raise ValueError("outcome outside public events")
            attempts=state["proposals"]
            if type(attempts) is not int or attempts!=len(indices)*PROPOSALS:
                raise ValueError("proposal counts")
            if any(type(state[k]) is not int or state[k]<0
                   for k in ("contradictions","prediction_accesses")):
                raise ValueError("accounting")
            out.used=indices
            out.observations=events
            out.hypotheses=rules
            out.proposals=attempts
            out.contradictions=state["contradictions"]
            out.prediction_accesses=state["prediction_accesses"]
            if out.cold_checkpoint()!=checkpoint:
                raise ValueError("noncanonical bytes")
            return out
        except (KeyError,IndexError,ValueError,TypeError,world.F50Rejected,
                public.PublicSourceRejected) as exc:
            raise NativeRejected("F50_COLD_STATE_REJECTED") from exc


if __name__=="__main__":
    world.freeze()
    print("F50_NATIVE_CAUSAL_ASSOCIATION_CODE_READY_NO_TARGET_FIRST_USE")
