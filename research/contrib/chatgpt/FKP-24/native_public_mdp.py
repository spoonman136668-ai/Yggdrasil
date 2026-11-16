"""FKP-24 public-action-only interface to an independently authored causal MDP.

This module deliberately does NOT import or ship the upstream source at
module import time. Normal source admission tests use a fake *interface*,
never an upstream world. Native admission remains a separate, authorized,
dependency-qualified stage.

The only native environment entrypoints used by a mechanical test are
reset(seed=...) and do(sealed_action_callback). No see(), ctf_do(),
step(), env/get_graph, natural_action, exogenous variables or info
reach a learner, even if the source returns such a dictionary.

An API data boundary is not a secure Python sandbox. Any independently
blind acceptance must place the source behind an isolated process boundary.
"""
from __future__ import annotations

from hashlib import sha256
import json
import operator
from typing import NamedTuple

UPSTREAM_REPO="CausalAILab/Causal-Gymnasium"
UPSTREAM_SHA="c94e9a4cd3641588b6b8507e71ccee5c27032bdf"
MECHANICAL_PUBLIC_SEEDS=(996100,996101,996102,996103)
MAX_ACTIONS=32


class PublicConsequence(NamedTuple):
    before:int
    action:int
    reward:int
    after:int
    terminated:bool
    truncated:bool


def _binary(v,name):
    """Accept Python/numpy integer/boolean values but NEVER floating labels."""
    if type(v).__module__=="numpy" and type(v).__name__=="bool_":
        n=int(v)
    else:
        try:
            n=operator.index(v)
        except (TypeError,ValueError) as e:
            raise ValueError("FKP24_NONINTEGER_PUBLIC_"+name) from e
    if n not in (0,1):
        raise ValueError("FKP24_OUT_OF_RANGE_PUBLIC_"+name)
    return int(n)


def _action(a):
    if type(a) is not int or a not in (0,1):
        raise ValueError("FKP24_LEARNER_ACTION_NOT_SEALED_BINARY")
    return a


def _canonical(v):
    return json.dumps(v,sort_keys=True,allow_nan=False,
                      separators=(",",":")).encode("ascii")


def _digest(v):
    return sha256(_canonical(v)).hexdigest()


def native_source_factory():
    """Import original native third-party package ONLY in separately gated run.

    CausalGym imports many unrelated environments eagerly, so this may raise
    an ImportError if qualified dependencies are missing. Do not suppress,
    stub, monkey-patch or replace its native class for a real-source claim.
    """
    from causal_gym.envs.mdp import MDPPCH
    from causal_gym.core.task import Task,LearningRegime

    def _factory():
        return MDPPCH(max_step=30,
                      task=Task(learning_regime=LearningRegime.do))
    return _factory


def public_mechanical_episode(source_factory,policy,*,seed,max_actions=MAX_ACTIONS):
    """Perform physical, strictly action-first do interventions, exactly once.

    source_factory is a trusted non-learner boundary, not model input.
    Policy receives ONLY prior observed state and public transition tuple.
    Returned report is a source-safe outer record. It must never be fed back
    as privileged metadata to the policy.
    """
    if type(seed) is not int or seed not in MECHANICAL_PUBLIC_SEEDS:
        raise PermissionError("FKP24_UNAUTHORIZED_OR_PROTECTED_WORLD")
    if type(max_actions) is not int or not 1<=max_actions<=MAX_ACTIONS:
        raise ValueError("FKP24_INVALID_PHYSICAL_ACTION_BUDGET")
    if not callable(source_factory) or not callable(getattr(policy,"choose",None)) or (
        not callable(getattr(policy,"observe",None))):
        raise ValueError("FKP24_TRUSTED_SOURCE_AND_PUBLIC_POLICY_REQUIRED")
    env=source_factory()
    if env is None:
        raise ValueError("FKP24_NATIVE_SOURCE_FACTORY_RETURNED_NONE")
    events=[]
    try:
        reset=env.reset(seed=seed)
        if type(reset) not in (tuple,list) or len(reset)!=2:
            raise ValueError("FKP24_PUBLIC_NATIVE_RESET_CONTRACT")
        # Reset info is intentionally NEVER inspected, copied or passed.
        state=_binary(reset[0],"STATE")
        complete=False
        for _ in range(max_actions):
            # A policy can depend only on the already witnessed public trace.
            chosen=_action(policy.choose(state,tuple(events)))
            seal={"calls":0}
            def sealed_action(native_observation):
                seal["calls"]+=1
                if seal["calls"]!=1 or _binary(native_observation,"CALLBACK_STATE")!=state:
                    raise ValueError("FKP24_SOURCE_ACTION_CALLBACK_VIOLATION")
                return chosen
            # PHYSICAL intervention: no future reward or info available yet.
            result=env.do(sealed_action)
            if seal["calls"]!=1 or type(result) not in (tuple,list) or len(result)!=5:
                raise ValueError("FKP24_NOT_ONE_NATIVE_PHYSICAL_DO")
            next_state=_binary(result[0],"NEXT_STATE")
            reward=_binary(result[1],"REWARD")
            termination=_binary(result[2],"TERMINATION")
            truncation=_binary(result[3],"TRUNCATION")
            # result[4] (info) is NEVER accessed, even if it has private keys.
            public=PublicConsequence(state,chosen,reward,next_state,
                                     bool(termination),bool(truncation))
            events.append(public)
            policy.observe(public)
            state=next_state
            if termination or truncation:
                complete=True
                break
        if not events:
            raise ValueError("FKP24_ZERO_ACTUAL_PHYSICAL_ACTIONS")
        serialized=[dict(before=e.before,action=e.action,reward=e.reward,
                         after=e.after,terminated=e.terminated,
                         truncated=e.truncated) for e in events]
        return {
            "schema":"fkp24.native-public-mdp-transcript.v1",
            "upstream_sha":UPSTREAM_SHA,
            "public_seed":seed,
            "physical_do_actions":len(events),
            "ended_by_source":complete,
            "budget_exhausted":not complete,
            "public_transitions_sha256":_digest(serialized),
            "public_transitions":serialized,
            "forbidden_info_passed_to_policy":False,
            "counterfactuals_used":False
        }
    finally:
        close=getattr(env,"close",None)
        if callable(close):
            close()


class FixedPublicPolicy:
    """Untrained public-only deterministic source-mechanical control.

    This is NOT a learning baseline or scored scientific claimant.
    """
    def __init__(self):
        self.actions=0
        self.received=[]

    def choose(self,state,history):
        _binary(state,"POLICY_STATE")
        if type(history) is not tuple or len(history)!=self.actions:
            raise ValueError("FKP24_POLICY_PUBLIC_TRACE_ORDER")
        return (state+self.actions)%2

    def observe(self,public):
        if type(public) is not PublicConsequence:
            raise ValueError("FKP24_POLICY_OBSERVED_NONPUBLIC")
        self.received.append(public)
        self.actions+=1
