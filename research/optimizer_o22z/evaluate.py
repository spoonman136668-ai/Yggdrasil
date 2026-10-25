"""O22-Z deterministic ORIGINAL-PUBLIC-SHAPED contradictory-history preflight.

Authored legal public observation/turn/return triples deliberately have NO
authenticated MiniGrid source identity, real episodic continuity, reward,
scientific original-source outcomes or observed alternate physical futures.
Purpose: demonstrate whether RETAINED past observed actions can affect a
decision at an IDENTICAL current observation, with fair trained controls.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,os,sys,subprocess,time
from pathlib import Path
from research.native.itd02.r1.native_policy import canonical
from research.optimizer_o22x.transition_belief import (
    NativeCausalCells,ConventionalNineRidge,check_transition
)
from research.optimizer_o22z.memory_control import ConditionalRecencyBeta,choice
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
P=json.loads((HERE/"PREREG.json").read_text())

def current():
    return dict(P["fixed_identical_query"])

def selected_return(before,action,blocked):
    if action not in (0,1):
        raise ValueError("O22Z_ONLY_LEGAL_REAL_SHAPED_TURNS")
    out=dict(before)
    out["direction"]=(before["direction"]-1)%4 if action==0 else (before["direction"]+1)%4
    out["front_blocked"]=blocked
    check_transition(before,action,out)
    return out

def fixture(phase):
    """Only prereg exactly 12 chosen LEFT and 12 chosen RIGHT observations."""
    if phase not in ("A","B"):
        raise ValueError("O22Z_NO_EXTRA_FIT_PHASE")
    state=current()
    observations=[]
    for _ in range(12):
        for action in (0,1):
            # Phase A: LEFT reports blocked, RIGHT clear.
            # Phase B: LEFT reports clear, RIGHT blocked.
            blocked=(action==0) if phase=="A" else (action==1)
            after=selected_return(state,action,blocked)
            observations.append({"before":dict(state),"selected_action":action,"returned_after":after})
    return observations

def train(native,shuffled,conventional,events):
    for e in events:
        before=e["before"];a=e["selected_action"];after=e["returned_after"]
        native.learn(before,a,after)
        conventional.learn(before,a,after)
        swapped=1-a
        altered=selected_return(before,swapped,after["front_blocked"])
        shuffled.learn(before,swapped,altered)

def fresh_os(model,state):
    cp=model.checkpoint()
    if type(model).restore(cp).checkpoint()!=cp:
        raise ValueError("O22Z_LOCAL_HISTORY_RESTORE_DRIFT")
    code=(
        "import json,sys;"
        "from research.optimizer_o22x.transition_belief import NativeCausalCells;"
        "from research.optimizer_o22z.memory_control import ConditionalRecencyBeta,choice;"
        "p=json.loads(sys.stdin.buffer.read());"
        "m=globals()[p['name']].restore(p['blob'].encode());"
        "print(json.dumps({'events':m.events,'choice':choice(m,p['state']),"
        "'front':[m.predict(p['state'],a)[0] for a in (0,1)]}))"
    )
    payload=canonical({"name":type(model).__name__,"blob":cp.decode(),"state":state})
    proc=subprocess.run([sys.executable,"-B","-c",code],input=payload,
        capture_output=True,timeout=20,cwd=ROOT,
        env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE="1"))
    if proc.returncode:
        raise ValueError("O22Z_FRESH_INTERPRETER_FAILED:"+proc.stderr.decode())
    out=json.loads(proc.stdout)
    want={"events":model.events,"choice":choice(model,state),
          "front":[model.predict(state,a)[0] for a in (0,1)]}
    if out!=want:
        raise ValueError("O22Z_FRESH_INTERPRETER_POLICY_MEMORY_DRIFT")
    return len(cp)

def batch_fit_conventional(events):
    """Original independent full-nine public feature L2 ridge, same source-shaped rows."""
    model=ConventionalNineRidge()
    for e in events:
        model.learn(e["before"],e["selected_action"],e["returned_after"])
    # The fitted conventional also needs forward samples; use legal source-shaped
    # FORWARD returns with zero extra reward and both sensor outcomes?
    # Not allowed: extra observations would break equal FIT event rights.
    # Fit separate independent source-public two-arm ridge on exactly provided turns.
    # Return the accumulated actual rows for a separately implemented fit below.
    return model

def simple_full9_ridge_turn(events,state):
    """Independently trained actual O22-X full-nine-feature ridge, same 24/48
    turns, with its unused FORWARD block regularized to prior zero. No invented
    forward observation and no physically assumed reward.
    """
    from research.optimizer_o22v.delayed_cells import _solve
    from research.optimizer_o22x.transition_belief import check_public
    grams={a:[[0.]*9 for _ in range(9)] for a in (0,1)}
    ys={a:[0.]*9 for a in (0,1)}
    for e in events:
        a=e["selected_action"]
        check_transition(e["before"],a,e["returned_after"])
        phi=check_public(e["before"])
        label=float(e["returned_after"]["front_blocked"])
        for i in range(9):
            ys[a][i]+=phi[i]*label
            for j in range(9):grams[a][i][j]+=phi[i]*phi[j]
    results=[]
    phi=check_public(state)
    for a in (0,1):
        m=[list(v) for v in grams[a]]
        for i in range(9):m[i][i]+=1.
        w=_solve(m,ys[a])
        results.append(max(.001,min(.999,sum(w[i]*phi[i] for i in range(9)))))
    return results

def declared_choice(prob):
    if abs(prob[0]-prob[1])<.10:return None
    return 0 if prob[0]<prob[1] else 1

def actual():
    state=current()
    history_A=fixture("A")
    history_B=fixture("B")
    if len(history_A)!=24 or len(history_B)!=24:
        raise ValueError("O22Z_FROZEN_FIXTURE_LENGTH")
    native=NativeCausalCells()
    frozen=NativeCausalCells()
    shifted=NativeCausalCells()
    conventional=ConditionalRecencyBeta()
    cohorts={}
    start=time.process_time()
    for phase,events in (("prior",[]),("A",history_A),("A_then_B",history_B)):
        if events:train(native,shifted,conventional,events)
        combined=[] if phase=="prior" else (history_A if phase=="A" else history_A+history_B)
        ridge=simple_full9_ridge_turn(combined,state)
        cohorts[phase]={
            "native_R1_fast_slow":choice(native,state),
            "native_action_shuffled_negative":choice(shifted,state),
            "native_frozen_zero_cell":choice(frozen,state),
            "independent_conditional_conventional_recency":choice(conventional,state),
            "independent_conventional_full9_ridge":declared_choice(ridge),
            "native_turn_front_predictions":[native.predict(state,a)[0] for a in (0,1)],
            "conventional_turn_front_predictions":[conventional.predict(state,a)[0] for a in (0,1)],
            "conventional_full9_ridge_turn_front_predictions":ridge,
            "equal_training_selected_action_rows":len(combined),
            "actual_original_source_actions_performed":0,
            "actual_original_source_reward_or_goal_value":"NOT_OBSERVED"
        }
    sizes={k:fresh_os(v,state) for k,v in (
      ("native_R1_fast_slow",native),
      ("native_action_shuffled_negative",shifted),
      ("native_frozen_zero_cell",frozen),
      ("independent_conditional_conventional_recency",conventional)
    )}
    a=cohorts["A"];b=cohorts["A_then_B"];z=cohorts["prior"]
    native_revises=(a["native_R1_fast_slow"]==1 and b["native_R1_fast_slow"]==0)
    zero_abstains=(z["native_R1_fast_slow"] is None
                   and a["native_frozen_zero_cell"] is None
                   and b["native_frozen_zero_cell"] is None)
    legitimate_conventional=(a["independent_conditional_conventional_recency"]==1
                              and b["independent_conditional_conventional_recency"]==0)
    stop=not(native_revises and zero_abstains and legitimate_conventional)
    science={
      "schema":P["schema"],
      "source_first_parent":P["parent"],
      "same_PUBLIC_six_field_current_observation_for_all_phases":state,
      "public_episode_data":"AUTHORED_LEGAL_SCHEMA_FIXTURES_NO_ORIGINAL_SOURCE_PHYSICS",
      "authored_before_selected_action_after_frozen_history_sha256":{
        "A":hashlib.sha256(canonical(history_A)).hexdigest(),
        "B":hashlib.sha256(canonical(history_B)).hexdigest()
      },
      "scenario_selected_public_turn_return_rows_count":len(history_A)+len(history_B),
      "phases":cohorts,
      "native_A_to_B_contradiction_revised_legal_action":native_revises,
      "zero_cell_both_phases_abstains":zero_abstains,
      "independently_trained_conventional_recency_also_revises":legitimate_conventional,
      "conventional_superiority_or_original_world_transfer":"NOT_TESTED",
      "public_world_source_original_new_episodes":0,
      "authored_fixtures_cannot_prove_world_dynamics_or_reward":True,
      "scientific_gate":"NO_GO_SOURCE_FREE_MEMORY_REVISION_FAILS_PREDECLARED" if stop
                       else "SOURCE_ONLY_HISTORY_DEPENDENT_DECISION_MECHANISM_PASS_NOT_ORIGINAL_SCIENCE"
    }
    return {"science":science,
      "source_free_cold_full_checkpoints_bytes":sizes,
      "source_free_total_CPU_s":round(time.process_time()-start,8),
      "science_SHA256":hashlib.sha256(canonical(science)).hexdigest()}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    opts=parser.parse_args()
    result=actual()
    opts.out.write_bytes(canonical(result)+b"\n")
    s=result["science"]
    for label,phase in s["phases"].items():
        print("O22Z_"+label.upper()+"_NATIVE_ACTION="+str(phase["native_R1_fast_slow"]),flush=True)
        print("O22Z_"+label.upper()+"_CONVENTIONAL_RECENCY="+str(phase["independent_conditional_conventional_recency"]),flush=True)
        print("O22Z_"+label.upper()+"_FROZEN="+str(phase["native_frozen_zero_cell"]),flush=True)
    print("O22Z_SOURCE_PHYSICS_OR_REWARD_PERFORMED=ZERO",flush=True)
    print("O22Z_SCIENCE_SHA256="+result["science_SHA256"],flush=True)
    print("O22Z_GATE="+s["scientific_gate"],flush=True)

if __name__=="__main__":main()
