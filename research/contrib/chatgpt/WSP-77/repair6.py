"""WSP77 source-blind paid intervention and gradient-free neural coordinate repair.

No source import or physically unpaid query. The active policy chooses public
actions by disagreement of two frozen, same-evidence Stage-A neural models.
Repair edits existing hidden ReLU REAL numeric input weights by a bounded
finite-difference loss search on paid A+B observations, never test physics.
After repair, a genuine numerical ridge-readout replay writes weights.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from random import Random
import sys

_BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(_BASE))
from neural6 import FeatureGrowthNeural,inputs,check

TOP_UNITS=8
MAX_EDITS=4
DELTA=0.5
MIN_OBJECTIVE_GAIN=1e-9
A_CHARGES=96
B_CHARGES=48


def policy_action(primary,secondary,state,seed,step):
    """Max Hamming of predicted SIX-bit consequences; tie is source blind."""
    check(state,0)
    if type(seed) is not int or type(step) is not int or not 0<=step<48:
        raise ValueError("invalid physically charged policy step")
    ranked=[]
    for action in range(6):
        lhs=primary.predict(state,action,force=True)
        rhs=secondary.predict(state,action,force=True)
        mismatch=sum(a!=b for a,b in zip(lhs,rhs))
        h=sha256(f"WSP77|disagree|{seed}|{step}|{action}".encode("ascii")).digest()
        ranked.append((-mismatch,h,action))
    return min(ranked)[2]


def random_policy(seed):
    return Random(int.from_bytes(sha256(
        f"WSP77|uniform-B-policy|{seed}".encode("ascii")).digest(),"big"))


def _shape(rows,n):
    if len(rows)!=n:
        raise ValueError("wrong physical paid-row budget")
    for state,action,target in rows:
        check(state,action)
        check(target,action)


def fitted_readout(stageA_snapshot,charge_A,charge_B):
    _shape(charge_A,A_CHARGES)
    _shape(charge_B,B_CHARGES)
    net=FeatureGrowthNeural.restore(stageA_snapshot)
    if len(net.hidden_weights)<33:
        raise ValueError("Stage A trained neural hidden features are missing")
    net._init_readout()
    for s,a,y in list(charge_A)+list(charge_B):
        net._learn_row(s,a,y)
    return net


def _squared_error6(raw,after):
    return sum((raw[i]-after[i])**2 for i in range(6))


def repair(stageA_snapshot,charge_A,charge_B,policy,seed):
    """Mutate existing hidden neural parameters, not model width or a rule table.

    Each candidate +/-0.5 coefficient trial uses numerical ReLU activations
    and original Stage-A numeric readout. Numeric readout refit occurs ONCE
    after all accepted bounded edits, from actual physically charged rows.
    """
    if policy not in ("counterexample","random") or type(seed) is not int:
        raise ValueError("invalid frozen neural-edit policy")
    _shape(charge_A,A_CHARGES)
    _shape(charge_B,B_CHARGES)
    teacher=FeatureGrowthNeural.restore(stageA_snapshot)
    model=FeatureGrowthNeural.restore(stageA_snapshot)
    n=len(model.hidden_weights)
    if n<33 or n>56 or len(model.w_readout[0])!=13+n:
        raise ValueError("invalid frozen stage-A network dimensions")
    charged=list(charge_A)+list(charge_B)
    xrows=[inputs(s,a) for s,a,y in charged]
    target=[y for s,a,y in charged]
    numerical=[list(teacher.raw(s,a)) for s,a,y in charged]
    loss=lambda:sum((2.0 if i>=96 else 1.0)*_squared_error6(pred,target[i])
                    for i,pred in enumerate(numerical))
    before_loss=loss()
    # source-blind top-eight selection from actual B prediction residual.
    rankings=[]
    for neuron in range(32,n):
        weighted=0.0
        for row_idx in range(96,144):
            x=xrows[row_idx]
            h=max(0.0,sum(w*z for w,z in zip(
                teacher.hidden_weights[neuron],x))+
                teacher.hidden_biases[neuron])
            weighted+=abs(h)*_squared_error6(numerical[row_idx],target[row_idx])
        rankings.append((-weighted,neuron))
    ranked_neurons=[n for score,n in sorted(rankings)[:TOP_UNITS]]
    edited_coordinates=set()
    record=[]
    rng=Random(int.from_bytes(sha256(
        f"WSP77|random-hidden-edit|{seed}".encode("ascii")).digest(),"big"))
    for iteration in range(MAX_EDITS):
        if policy=="random":
            remaining=[(j,k) for j in range(32,n) for k in range(6)
                       if (j,k) not in edited_coordinates]
            if not remaining:
                break
            neuron,coord=rng.choice(remaining)
            delta=rng.choice((-DELTA,DELTA))
            model.hidden_weights[neuron][coord]+=delta
            edited_coordinates.add((neuron,coord))
            record.append((neuron,coord,delta,None))
            continue
        current_loss=loss()
        best=None
        best_gain=MIN_OBJECTIVE_GAIN
        for neuron in ranked_neurons:
            offset=13+neuron
            original_weights=model.hidden_weights[neuron]
            bias=model.hidden_biases[neuron]
            original_activation=[
                max(0.0,sum(w*z for w,z in zip(original_weights,x))+bias)
                for x in xrows
            ]
            for coord in range(6):
                if (neuron,coord) in edited_coordinates:
                    continue
                for delta in (-DELTA,DELTA):
                    gain=0.0
                    deltas=[]
                    for i,x in enumerate(xrows):
                        if not x[coord]:
                            deltas.append(0.0)
                            continue
                        dh=(max(0.0,sum(w*z for w,z in zip(
                            original_weights,x))+bias+delta)-
                            original_activation[i])
                        deltas.append(dh)
                        if dh:
                            old=_squared_error6(numerical[i],target[i])
                            after=_squared_error6([
                                numerical[i][bit]+teacher.w_readout[bit][offset]*dh
                                for bit in range(6)],target[i])
                            gain+=(2.0 if i>=96 else 1.0)*(old-after)
                    key=(neuron,coord,delta)
                    if gain>best_gain+1e-12 or (abs(gain-best_gain)<=1e-12
                           and best is not None and key<best[0]):
                        best=(key,deltas)
                        best_gain=gain
        if best is None:
            break
        (neuron,coord,delta),deltas=best
        model.hidden_weights[neuron][coord]+=delta
        edited_coordinates.add((neuron,coord))
        offset=13+neuron
        for i,dh in enumerate(deltas):
            for bit in range(6):
                numerical[i][bit]+=teacher.w_readout[bit][offset]*dh
        record.append((neuron,coord,delta,round(best_gain,12)))
    final_frozen_loss=loss()
    model._init_readout()
    for s,a,y in charged:
        model._learn_row(s,a,y)
    # Real numerical matrices are modified in the source-blind memory store.
    return model,{
        "policy":policy,
        "candidate_coordinate_evaluations_upper_bound":
            MAX_EDITS*TOP_UNITS*6*2 if policy=="counterexample" else 0,
        "hidden_edits":tuple(record),
        "hidden_width":len(model.hidden_weights),
        "frozen_numeric_train_loss_before":round(before_loss,10),
        "frozen_numeric_train_loss_after":round(final_frozen_loss,10),
        "changed_hidden_coefficients":sum(
            model.hidden_weights[i][j]!=teacher.hidden_weights[i][j]
            for i in range(n) for j in range(12)),
        "readout_reprogrammed":model.w_readout!=teacher.w_readout,
        "direct_gradient_steps":0,
        "physical_charged_A":96,
        "physical_charged_B":48,
    }
