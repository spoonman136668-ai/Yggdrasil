"""Static original-source derivation and frozen native decision utility audit.

No original source imports, source instantiation, RNG, reset/do or private
runtime observation. Oracle equations are EVALUATOR ONLY. Learned native
counts must reproduce the already sealed NKR19 checkpoints exactly.
"""
from __future__ import annotations
import argparse
import ast
from fractions import Fraction
import hashlib
import itertools
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(HERE.parent/"NKR-19"))
import audit as nkr19
sys.path.insert(0,str(HERE.parent/"NKR-20"))
import campaign as nkr20
from yggdrasil.public_causal_cells import PublicCausalCells

SOURCE_BLOB="6264ec5450754c009e98c3e85f6d5927ece0a9ab"
SCALES=(8,16,24)
HORIZON=7

def canon(d):
    return json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=True,
                      allow_nan=False).encode("ascii")

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def need(ok,reason):
    if not ok:
        raise ValueError("NKR23_"+reason)

def qdoc(q):
    return {"numerator":q.numerator,"denominator":q.denominator,"value":float(q)}

def git_blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def expression(node,values):
    # Tiny explicit Boolean AST interpreter. No Call, exec/eval, imports,
    # source objects, RNG or arbitrary attribute resolution is supported.
    if isinstance(node,ast.Name):
        need(node.id in values,"EXPRESSION_NAME")
        return values[node.id]
    if isinstance(node,ast.Attribute):
        need(isinstance(node.value,ast.Name) and node.value.id=="self"
             and node.attr=="s","EXPRESSION_ATTRIBUTE")
        return values["s"]
    if isinstance(node,ast.Compare):
        need(len(node.ops)==1 and isinstance(node.ops[0],ast.NotEq)
             and len(node.comparators)==1,"EXPRESSION_COMPARE")
        return int(expression(node.left,values)!=expression(node.comparators[0],values))
    if isinstance(node,ast.BinOp) and isinstance(node.op,ast.BitOr):
        return expression(node.left,values)|expression(node.right,values)
    raise ValueError("NKR23_EXPRESSION_FORM_NOT_ALLOWED")

def load_equations(path):
    raw=Path(path).read_bytes()
    need(git_blob(raw)==SOURCE_BLOB,"PINNED_ORIGINAL_SOURCE_BLOB")
    tree=ast.parse(raw.decode("utf-8"))
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="MDPSCM")
    methods={n.name:n for n in cls.body if isinstance(n,ast.FunctionDef)}
    weights={}
    for node in methods["__init__"].body:
        if not isinstance(node,ast.Assign) or len(node.targets)!=1:
            continue
        left=node.targets[0]
        if not isinstance(left,ast.Attribute) or left.attr not in ("_u1","_u2","_u3"):
            continue
        need(isinstance(node.value,ast.Lambda) and isinstance(node.value.body,ast.Call),
             "ORIGINAL_SOURCE_LATENT_SAMPLER")
        call=node.value.body
        need(isinstance(call.func,ast.Attribute) and call.func.attr=="choice"
             and len(call.args)==1 and isinstance(call.args[0],ast.Constant)
             and call.args[0].value==2,"ORIGINAL_BINARY_SOURCE")
        ps=next(k.value for k in call.keywords if k.arg=="p")
        need(isinstance(ps,ast.List) and len(ps.elts)==2
             and all(isinstance(v,ast.Constant) for v in ps.elts),"LATENT_PROBABILITIES")
        q=tuple(Fraction(str(v.value)) for v in ps.elts)
        need(sum(q)==1 and all(0<=v<=1 for v in q),"NOMINAL_SOURCE_DISTRIBUTION")
        weights[left.attr[1:]]=q
    need(set(weights)=={"u1","u2","u3"},"LATENT_SOURCE_KEYS")
    reward=next(n.value for n in methods["step"].body if isinstance(n,ast.Assign)
                and any(isinstance(t,ast.Attribute) and t.attr=="y" for t in n.targets))
    transition=next(n.value for n in methods["state_transition"].body if isinstance(n,ast.Return))
    sampled=next(n.value for n in methods["sample_u"].body if isinstance(n,ast.Return))
    need(isinstance(sampled,ast.Tuple) and len(sampled.elts)==3,"FRESH_LATENT_CALLS")
    need([n.func.attr for n in sampled.elts if isinstance(n,ast.Call)
          and isinstance(n.func,ast.Attribute)]==["_u1","_u2","_u3"],"FRESH_LATENT_ORDER")
    reward_names={n.id for n in ast.walk(reward) if isinstance(n,ast.Name)}
    transition_names={n.id for n in ast.walk(transition) if isinstance(n,ast.Name)}
    need(reward_names=={"self","x","u1","u3"} and transition_names=={"s","x","u1","u2"},
         "SOURCE_HISTORY_DEPENDENCY")
    return weights,reward,transition

def kernel_from_source(path):
    weights,reward,transition=load_equations(path)
    kernel={}
    checked=0
    for state,action in itertools.product((0,1),repeat=2):
        joint=[[Fraction(0),Fraction(0)],[Fraction(0),Fraction(0)]]
        for u1,u2,u3 in itertools.product((0,1),repeat=3):
            values=dict(s=state,x=action,u1=u1,u2=u2,u3=u3)
            y=expression(reward,values)
            nxt=expression(transition,values)
            # Independent direct Boolean reference for this public source.
            need(y==(state^action^u1^u3)
                 and nxt==(u1^u2^(state|action)),"INDEPENDENT_BOOLEAN_PARITY")
            mass=weights["u1"][u1]*weights["u2"][u2]*weights["u3"][u3]
            joint[y][nxt]+=mass
            checked+=1
        need(sum(sum(v) for v in joint)==1,"SOURCE_KERNEL_NORMALIZATION")
        kernel[state,action]=joint
    report={
      "experiment":"NKR-23","classification":"EXPLORATORY_SOURCE_MECHANISM_DERIVATION",
      "source_blob":SOURCE_BLOB,"exact_boolean_assignments_checked":checked,
      "nominal_iid_scm_assumption_explicit":True,
      "model_learned_source_equations":False,
      "population_history_value_given_public_state_action":0,
      "interpretation":"Under the nominal iid source model, previous reward adds no population conditional information beyond current state/action. PRNG execution or new worlds were not tested.",
      "kernel":[{"state":s,"action":a,
                 "reward_probability":qdoc(sum(kernel[s,a][1])),
                 "next_state_one_probability":qdoc(kernel[s,a][0][1]+kernel[s,a][1][1]),
                 "joint":[[qdoc(q) for q in row] for row in kernel[s,a]]}
                for s,a in sorted(kernel)],
      "original_source_actions":0,"scientific_pass":False}
    return kernel,report

def learned_maps(data,k):
    bank=PublicCausalCells()
    for world,seed in enumerate(nkr19.SEEDS):
        for row in data[seed][:k]:
            nkr19.update(bank,world,row)
    raw=bank.snapshot()
    cold=PublicCausalCells.restore(raw)
    need(cold.snapshot()==raw,"FROZEN_NATIVE_COLD")
    maps={}
    for world,seed in enumerate(nkr19.SEEDS):
        rows=data[seed][:k]
        maps[world]={}
        for state in (0,1):
            p=[nkr19.native_probability(cold,world,0,state,a) for a in (0,1)]
            reference=[]
            for action in (0,1):
                seen=[r["reward"] for r in rows if r["before"]==state and r["action"]==action]
                reference.append(Fraction(sum(seen)+1,len(seen)+2))
            need(p==reference,"SAME_INFORMATION_EXACT_BAYES")
            chosen=int(p[1]>p[0])
            need(chosen==int(reference[1]>reference[0]),"POLICY_REFERENCE")
            maps[world][state]=chosen
    return maps,sha(raw)

def choose(name,state,step,action_map):
    if name=="native":
        return action_map[state]
    if name=="always0":
        return 0
    if name=="always1":
        return 1
    if name=="mechanical":
        return (state+step)%2
    if name=="source_oracle":
        return state
    raise ValueError("NKR24_POLICY")

def exact_return(kernel,name,action_map,initial,start,horizon=HORIZON):
    need(type(horizon) is int and horizon>=1 and start+horizon<=31,"SOURCE_HORIZON")
    dist=list(initial)
    need(len(dist)==2 and sum(dist)==1 and all(p>=0 for p in dist),"INITIAL_DISTRIBUTION")
    total=Fraction(0)
    for t in range(horizon):
        after=[Fraction(0),Fraction(0)]
        for state in (0,1):
            action=choose(name,state,start+t,action_map)
            joint=kernel[state,action]
            total+=dist[state]*sum(joint[1])
            for nxt in (0,1):
                after[nxt]+=dist[state]*(joint[0][nxt]+joint[1][nxt])
        need(sum(after)==1,"ROLLOUT_NORMALIZATION")
        dist=after
    return total

def run_decisions(data,kernel,prior_results):
    pinned={int(k):r["checkpoint_sha256"] for k,r in prior_results["scales"].items()}
    scales=[]
    for k in SCALES:
        maps,pin=learned_maps(data,k)
        need(pin==pinned[k],"ORIGINAL_NKR19_CHECKPOINT_IDENTITY")
        totals={name:Fraction(0) for name in ("native","always0","always1","mechanical","source_oracle")}
        conditioned={name:Fraction(0) for name in totals}
        for world,seed in enumerate(nkr19.SEEDS):
            # The action map is already frozen before source-kernel scoring.
            actual=data[seed][k]["before"]
            for name in totals:
                totals[name]+=exact_return(kernel,name,maps[world],(Fraction(1,2),Fraction(1,2)),k)/4
                conditioned[name]+=exact_return(kernel,name,maps[world],
                                                (Fraction(1-actual),Fraction(actual)),k)/4
        optimal=sum(maps[w][s]==s for w in maps for s in (0,1))
        scales.append({"observations_per_world":k,"checkpoint_sha256":pin,
          "native_action_maps":maps,"source_oracle_optimal_choices":optimal,"choices":8,
          "common_uniform_start_expected_reward_per_step":{n:qdoc(v/HORIZON) for n,v in totals.items()},
          "historical_prefix_state_expected_reward_per_step":{n:qdoc(v/HORIZON) for n,v in conditioned.items()},
          "horizon":HORIZON,"native_same_information_control_choices_identical":True})
    top=scales[-1]
    metrics=top["common_uniform_start_expected_reward_per_step"]
    n=metrics["native"]; b=metrics["mechanical"]
    gain=Fraction(n["numerator"],n["denominator"])-Fraction(b["numerator"],b["denominator"])
    supported=top["source_oracle_optimal_choices"]>=6 and gain>=Fraction(1,10)
    return {"experiment":"NKR-24","classification":"THEORETICAL_DECISION_VALUE_SUPPORTED" if supported
            else "THEORETICAL_DECISION_VALUE_NOT_ESTABLISHED",
            "scales":scales,"source_model_conditioned_only":True,
            "newly_executed_policy_reward_measured":False,
            "new_original_source_actions":0,
            "native_vs_strongest_equal_information_gain":0,"scientific_pass":False}

def stable(doc):
    out=json.loads(json.dumps(doc))
    for key in ("wall_seconds","environment","source_candidate_sha"):
        out.pop(key,None)
    return out

def run():
    started=time.monotonic()
    data=nkr20.read_fixture(HERE.parent/"NKR-20/source_fixture.json")
    prior=json.loads((HERE.parent/"NKR-19/result.json").read_text())
    kernel,mechanism=kernel_from_source(HERE/"original_mdp.py.txt")
    decisions=run_decisions(data,kernel,prior)
    result={"schema":"yggdrasil.nkr23-24.source-decision.result.v1",
            "experiments":[mechanism,decisions],"source_first_use":False,
            "new_original_source_actions":0,"scientific_pass":False,"accepted_native":False,
            "source_candidate_sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
            "environment":{"python":sys.version,"platform":platform.platform()},
            "wall_seconds":time.monotonic()-started}
    need(result["wall_seconds"]<=120,"WALL_BUDGET")
    result["stable_sha256"]=sha(canon(stable(result)))
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--verify-env",action="store_true")
    args=p.parse_args()
    result=run()
    if args.verify_env:
        need(stable(result)==stable(json.loads(os.environ["NKR23_EXPECTED_RESULT"])),
             "CROSS_PLATFORM_STABLE_DRIFT")
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"],"a") as f:
            f.write("result="+json.dumps(result,separators=(",",":"),sort_keys=True)+"\n")
    print("NKR23_24_SOURCE_DECISION_AUDIT="+json.dumps(result,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
