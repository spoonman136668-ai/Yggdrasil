"""CKAD21: frozen two-timescale retention-versus-adaptation experiment.

Isolated development over the already-consumed CKAD20 synthetic corpus.
Only public executed-action receipts train two conventional Beta tables. CKAD20
native checkpoint and every prior witness remain byte-exact. The hypothesis
belief update uses actual first-stage observed s2, not hidden family labels.
"""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE.parent / "CKAD-20"))

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner, EXPERIENCE_SOURCE
from synthetic_world import make_episode, public_views, rollout

BITS = (0, 1)
SEEDS = (101, 202, 303)
ARMS = ("two_timescale_dynamic", "two_timescale_static", "early_only", "late_only",
        "native_ckad20", "full_beta", "trailing64_mle")
COHORTS = (
    ("eval-0", "invariant", 0),
    ("eval-1", "context_switch", 0),
    ("eval-2", "context_switch", 1),
    ("eval-3", "terminal_switch", 1),
)
STATE_PINS = {
    101: "1319b37a689988174593b7b1702cfb974f3c4f4ae4f91d2653ca08e8a22172cc",
    202: "50a8ce4796c2db8d559b18a168e3727a6234e512fce995ab395b9795977700a3",
    303: "52441e6593281ded40b83dbd9b7cd7d2f23ca56bd5b0142f5b52e3ab6277dbfc",
}
SOURCE_PIN = "20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef"


def need(condition, reason):
    if not condition:
        raise ValueError("CKAD21_" + reason)


def ratio(value):
    return [value.numerator, value.denominator]


class FittedTable:
    """Fully fitted public source-only conditional Beta table, no private labels."""

    def __init__(self, events, projection, *, pseudocount=1):
        need(type(projection) is int and projection in (0, 1), "PROJECTION")
        need(type(pseudocount) is int and pseudocount in (0, 1), "PRIOR")
        self.projection = projection
        self.pseudo = pseudocount
        self.transition = Counter()
        self.terminal = Counter()
        self.count = len(events)
        for identifier, views, x1, s2, x2, y in events:
            need(type(identifier) is str and len(identifier) == 64, "PUBLIC_IDENTIFIER")
            need(len(views) == 2 and all(len(v) == 2 for v in views), "VIEWS")
            need(all(type(q) is int and q in BITS for q in (x1, s2, x2, y)), "PUBLIC_BITS")
            a, b = (views[0][projection], views[1][projection])
            context = a if a == b else None
            self.transition[(None, x1, s2)] += 1
            self.terminal[(None, x1, s2, x2, y)] += 1
            if context is not None:
                self.transition[(context, x1, s2)] += 1
                self.terminal[(context, x1, s2, x2, y)] += 1

    def _ctx(self, view):
        need(type(view) is tuple and len(view) == 2
             and all(type(q) is int and q in BITS for q in view), "PUBLIC_VIEW")
        return view[self.projection]

    def _prob(self, counter, key):
        successes = counter[key + (1,)] + self.pseudo
        total = counter[key + (0,)] + counter[key + (1,)] + 2 * self.pseudo
        return Fraction(successes, total) if total else Fraction(1, 2)

    def transition_p(self, view, x1):
        need(type(x1) is int and x1 in BITS, "FIRST_ACTION")
        return self._prob(self.transition, (self._ctx(view), x1))

    def terminal_p(self, view, x1, s2, x2):
        need(all(type(q) is int and q in BITS for q in (x1, s2, x2)), "SECOND_HISTORY")
        return self._prob(self.terminal, (self._ctx(view), x1, s2, x2))


def conventional_plan(table, view):
    actions, values = [], []
    for x1 in BITS:
        q = table.transition_p(view, x1)
        contingent = [int(table.terminal_p(view, x1, s2, 1) >
                          table.terminal_p(view, x1, s2, 0)) for s2 in BITS]
        total = ((1-q)*table.terminal_p(view, x1, 0, contingent[0]) +
                 q*table.terminal_p(view, x1, 1, contingent[1]))
        actions.append(contingent)
        values.append(total)
    return {"first_action":int(values[1] > values[0]), "second_actions":actions}


def mixture_joint(early, late, view, x1, s2, x2):
    """Joint probability of s2 and delayed reward, integrating latent regime."""
    terms = []
    for model in (early,late):
        q=model.transition_p(view,x1)
        p=q if s2 else 1-q
        terms.append(p*model.terminal_p(view,x1,s2,x2))
    return sum(terms, Fraction(0))/2


def posterior_second_value(early, late, view, x1, s2, x2):
    weights=[]
    for model in (early,late):
        q=model.transition_p(view,x1)
        weights.append(q if s2 else 1-q)
    z=sum(weights)
    need(z>0, "ZERO_TRANSITION_MASS")
    return (weights[0]*early.terminal_p(view,x1,s2,x2)+
            weights[1]*late.terminal_p(view,x1,s2,x2))/z


def mixture_plan(early, late, view, *, adaptive):
    """Pure readout. At second stage only the actually revealed s2 may update belief."""
    actions, values = [], []
    for x1 in BITS:
        second=[]
        for s2 in BITS:
            score=lambda x2: (posterior_second_value(early,late,view,x1,s2,x2)
                              if adaptive else
                              (early.terminal_p(view,x1,s2,x2)+late.terminal_p(view,x1,s2,x2))/2)
            second.append(int(score(1)>score(0)))
        actions.append(second)
        values.append(sum((mixture_joint(early,late,view,x1,s2,second[s2])
                           for s2 in BITS),Fraction(0)))
    return {"first_action":int(values[1]>values[0]),"second_actions":actions}


def independent_joint(early, late, view, x1, s2, x2):
    """Independent conventional enumerator of the same fixed two-model mixture."""
    outcome = Fraction(0)
    for t in (early,late):
        count_prob = t.transition_p(view,x1)
        p_state = (count_prob if s2 else 1-count_prob)
        count_success = t.terminal_p(view,x1,s2,x2)
        outcome += Fraction(1,2)*p_state*count_success
    return outcome


def check_formula(early, late):
    checks = 0
    for view in product(BITS,repeat=2):
        for x1, s2, x2 in product(BITS,repeat=3):
            j = mixture_joint(early,late,view,x1,s2,x2)
            independent=independent_joint(early,late,view,x1,s2,x2)
            need(j==independent, "INDEPENDENT_FORMULA")
            q_early=early.transition_p(view,x1)
            q_late=late.transition_p(view,x1)
            mass=(q_early if s2 else 1-q_early)+(q_late if s2 else 1-q_late)
            need(j==mass*posterior_second_value(early,late,view,x1,s2,x2)/2,
                 "BAYES_JOINT_POSTERIOR_IDENTITY")
            checks+=1
        for adaptive in (False,True):
            need(mixture_plan(early,late,view,adaptive=adaptive)==
                 mixture_plan(late,early,view,adaptive=adaptive), "EXCHANGEABILITY")
    return checks


def expected_event_id(cohort,seed,index):
    return digest(canonical(["ckad20", SOURCE_PIN,cohort,seed,index,"active"]))


def verify_public_witnesses(events,seed):
    schedule=(("train-0",64),("train-1",64),("train-2",96))
    need(len(events)==224, "TRAINING_EPISODE_COUNT")
    index=0
    for cohort,n in schedule:
        for j in range(n):
            event=events[index+j]
            need(type(event) is list and len(event)==6, "EPISODE_SHAPE")
            need(event[0]==expected_event_id(cohort,seed,j),
                 "TRAINING_EVENT_IDENTITY")
        index+=n
    need(len({row[0] for row in events})==224,"EPISODE_ID_COLLISION")
    return events[:64],events[-96:]


def read_parent(seed):
    path=HERE.parent/"CKAD-20"/f"seed-{seed}-unified-native.json"
    raw=path.read_bytes()
    need(digest(raw)==STATE_PINS[seed],"CHECKPOINT_SOURCE_PIN")
    model=NativeCumulativeLearner.restore(raw,STATE_PINS[seed])
    need(model.checkpoint()==raw,"CHECKPOINT_RESTORATION")
    data=json.loads(raw)
    exp=json.loads(data["experience_ascii"])
    need(exp["schema"]=="yggdrasil.ckad.native-episode-experience.v1", "EXPERIENCE_SCHEMA")
    need(exp["repair"] is True and exp["state_sha256"]==model.info()["episode_experience"]["state_sha256"],
         "EXPERIENCE_CUSTODY")
    return model,raw,exp["episodes"]


def execute(episode,plan):
    return rollout(episode,
                   lambda initial:plan["first_action"],
                   lambda initial,x1,s2:plan["second_actions"][x1][s2])


def run():
    started=time.monotonic()
    need(digest((HERE.parent/"CKAD-20"/"synthetic_world.py").read_bytes())==
         SOURCE_PIN==EXPERIENCE_SOURCE,"PUBLIC_SOURCE_CUSTODY")
    protocol=json.loads((HERE/"prereg.json").read_bytes())
    need(protocol["exact_source"]["sha256"]==SOURCE_PIN,"PREREG_SOURCE_PIN")
    traces=[]
    per_seed=[]
    audits=0
    for seed in SEEDS:
        model,checkpoint,events=read_parent(seed)
        early_rows,late_rows=verify_public_witnesses(events,seed)
        projection=model.info()["episode_experience"]["projection"]
        need(projection in BITS,"PROJECTION_MISSING")
        early=FittedTable(early_rows,projection)
        late=FittedTable(late_rows,projection)
        full=FittedTable(events,projection)
        recent=FittedTable(events[-64:],projection,pseudocount=0)
        audits+=check_formula(early,late)
        plans={}
        for view in product(BITS,repeat=2):
            plans[view]={
                "two_timescale_dynamic":mixture_plan(early,late,view,adaptive=True),
                "two_timescale_static":mixture_plan(early,late,view,adaptive=False),
                "early_only":conventional_plan(early,view),
                "late_only":conventional_plan(late,view),
                "native_ckad20":model.experience_plan(view),
                "full_beta":conventional_plan(full,view),
                "trailing64_mle":conventional_plan(recent,view),
            }
        evidence={}
        for cohort,family,regime in COHORTS:
            hits={arm:0 for arm in ARMS}
            tags={arm:[] for arm in ARMS}
            for index in range(96):
                episode=make_episode(cohort=cohort,seed=seed,index=index,
                                     family=family,regime=regime)
                first_view,second_view=public_views(episode)
                view=tuple(first_view)
                need(view in plans,"EVALUATION_VIEW")
                for arm in ARMS:
                    plan=plans[view][arm]
                    row=execute(episode,plan)
                    need(type(row) is dict and set(row)=={"s1","x1","s2","x2","y"},
                         "PUBLIC_ROLLOUT_SHAPE")
                    need(all(type(row[k]) is int and row[k] in BITS
                             for k in ("s1","x1","s2","x2","y")), "PUBLIC_ROLLOUT_BITS")
                    hits[arm]+=row["y"]
                    tags[arm].append([row["x1"],row["s2"],row["x2"],row["y"]])
            evidence[cohort]={"successes":hits,"denominator":96,
                              "trace_sha256":{a:digest(canonical(tags[a])) for a in ARMS}}
        need(digest(model.checkpoint())==STATE_PINS[seed] and model.checkpoint()==checkpoint,
             "NATIVE_CHECKPOINT_MUTATION")
        per_seed.append({"seed":seed,"projection":projection,"native_checkpoint_sha256":STATE_PINS[seed],
                         "training_episodes":len(events),"anchor_episodes":len(early_rows),
                         "recent_episodes":len(late_rows),"evaluation":evidence})
    totals={cohort:{arm:sum(x["evaluation"][cohort]["successes"][arm] for x in per_seed)
                    for arm in ARMS} for cohort,_,_ in COHORTS}
    native_final=(totals["eval-0"]["native_ckad20"],totals["eval-2"]["native_ckad20"])
    need(native_final==(204,227),"HISTORICAL_NATIVE_BASELINE_DRIFT")
    # The exact prereg thresholds are intentionally unchanged even if all gates fail.
    gates={
        "prior_retention":totals["eval-0"]["two_timescale_dynamic"]>=233,
        "shift_vs_strongest_control":totals["eval-2"]["two_timescale_dynamic"]>=245,
        "mixture_vs_static_prior":totals["eval-0"]["two_timescale_dynamic"]>=
                                  totals["eval-0"]["two_timescale_static"]+6,
        "mixture_vs_static_shift":totals["eval-2"]["two_timescale_dynamic"]>=
                                  totals["eval-2"]["two_timescale_static"]+6,
    }
    output={
        "schema":"yggdrasil.ckad21.two-timescale-belief-result.v1",
        "classification":"DEVELOPMENT_GO" if all(gates.values()) else "DEVELOPMENT_NO_GO",
        "parent_sha":"d8f27db46af889afdfeb104fc471a710fc6d5c06",
        "source_sha256":SOURCE_PIN,
        "seeds":list(SEEDS),"cases_per_cohort":288,"source_class":"PREVIOUSLY_CONSUMED_SYNTHETIC_DEVELOPMENT",
        "formula_parity_checks":audits,
        "legacy_native_baseline_verified":True,
        "training_updates":0,"held_training_updates":0,"new_original_source_actions":0,
        "source_owner_mutations":0,"checkpoint_mutations":0,
        "gates":gates,"totals":totals,"per_seed":per_seed,
        "scientific_pass":False,"accepted_native":False,"deployment":"NONE",
    }
    output["stable_sha256"]=digest(canonical(output))
    output["whole_wall_seconds"]=time.monotonic()-started
    need(output["whole_wall_seconds"]<120,"WALL_BUDGET")
    return output


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-directory",required=True,type=Path)
    args=parser.parse_args()
    args.output_directory.mkdir(parents=True,exist_ok=True)
    d=run()
    (args.output_directory/"result.json").write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print(json.dumps({key:d[key] for key in ("classification","gates","totals",
                                            "stable_sha256","whole_wall_seconds")},sort_keys=True))
