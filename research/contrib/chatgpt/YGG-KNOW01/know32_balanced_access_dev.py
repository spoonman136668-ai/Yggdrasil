"""KNOW32: balanced public action coverage and unannounced causal-law retention.

Source-free prospective study. Protocol committed before this module at
97cb673450b469db16b70ceb68808cf2fe274cf3.
NEVER call proof() in focused tests. One held cohort only after exact CI.
No original-world source, native weights, owner model or controller actions.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from know30_blind_archive_reactivation_dev import Pair, Single, Joint, trained, high_brier, MODE
from know31_paired_interference_dev import cold_copy, slot_digest, a_slot_high
from know27_online_action_policy_dev import true_bit
from unknown_action_affordance_dev import ALL_MAPS, TRUE_MAPS, P_TRUE, P_FALSE, digest

SCHEMA = "yggdrasil.know32.balanced-access-causal-retention-result.dev.v1"
PROTO = "yggdrasil.know32.balanced-access-causal-retention-prereg.v1"
PROTO_BLOB = "9f8664601b2161183b16d7b47ac53303e1b73d51"
PREREG = "97cb673450b469db16b70ceb68808cf2fe274cf3"
SEEDS = (17301,17311,17317,17321,17327,17333,17341,17351)
MAP_IDS = (0,1,2)
ARMS = ("archive","switching_bayes","single","rolling8")
BRANCHES = ("control_A","treatment_B")
N = 48
PREFIX = 16
B_END = 32
K = (4,8)


def require(ok, tag):
    if not ok:
        raise ValueError("YGG_KNOW32_" + tag)


def protocol():
    raw = Path(__file__).with_name("know32_balanced_access_protocol.json").read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    require(blob == PROTO_BLOB, "PROTOCOL_BLOB")
    p = json.loads(raw)
    s, b = p["source"], p["budgets"]
    require(p["schema"] == PROTO and s["mode"] == MODE
            and s["seeds"] == list(SEEDS)
            and s["mapping_groups"] == list(MAP_IDS)
            and b["world_pairs"] == 24 and b["steps_per_fork"] == N
            and b["unique_observed_consequences_total"] == 1920
            and b["model_level_witnesses_per_arm_across_forks"] == 2304
            and p["scope"]["original_first_use_issue_426"] is False
            and p["scope"]["accepted_native_modified"] is False, "PROTOCOL_DRIFT")
    return p


def public_tape(t):
    require(type(t) is int and 0 <= t < N, "PUBLIC_STEP")
    return t % 4, (t // 4) % 4


def phase_coverage():
    out = []
    for map_idx, mapping in enumerate(ALL_MAPS):
        require(len(mapping) == 4 and mapping[0] == 0, "MAP_IDENTITY")
        phases = []
        for start in (0,16,32):
            pairs = [public_tape(t) for t in range(start,start+16)]
            physical = [c ^ mapping[a] for c,a in pairs]
            require(len(set(pairs)) == 16 and set(physical) == set(range(8)),
                    "INSUFFICIENT_SUPPORT")
            phases.append({"start":start,"physical_histogram":
                           [physical.count(x) for x in range(8)]})
        out.append({"hypothesis_map_index":map_idx,"phase_support":phases})
    return out


def b_law(seed):
    require(type(seed) is int and seed in SEEDS, "B_LAW_ID")
    return "H2" if SEEDS.index(seed) < 4 else "H1"


def b_family(seed):
    return "known_H2" if b_law(seed) == "H2" else "unfamiliar_H1"


def private_witness(mid, seed, t, action, branch, *, source_mode=MODE):
    """Only private evaluator reads true map/law; callers pass public action."""
    require(source_mode == MODE and type(mid) is int and mid in MAP_IDS
            and type(seed) is int and seed in SEEDS
            and type(t) is int and 0 <= t < N
            and type(action) is int and action in (0,1,2,3)
            and branch in BRANCHES, "PRIVATE_SOURCE")
    c, expected_action = public_tape(t)
    require(action == expected_action, "ACTION_TAPE")
    law = b_law(seed) if branch == "treatment_B" and PREFIX <= t < B_END else "H0"
    q = P_TRUE if true_bit(law, c ^ TRUE_MAPS[mid][action]) else P_FALSE
    h = hashlib.sha256(
        f"know32:private:coin:v1:{mid}:{seed}:{t}".encode("ascii")).digest()
    return int(int.from_bytes(h[:8],"big") / (1 << 64) < q)


def new_arms(fit):
    prior,a,b,pooled,_old = fit
    return {"archive":Pair(a,b,quarantine=True),
            "switching_bayes":Pair(a,b,quarantine=False),
            "single":Single(pooled),
            "rolling8":Single(pooled,rolling=True)}


def run_shared_prefix(fit, mid, seed, witness):
    models = new_arms(fit)
    calls = 0
    for t in range(PREFIX):
        c,a = public_tape(t)
        y = witness(mid,seed,t,a,"control_A")
        require(type(y) is int and y in (0,1), "WITNESS_TYPE")
        calls += 1
        for m in models.values():
            m.observe(t,c,a,y)
    require(calls == PREFIX, "DUPLICATE_PREFIX")
    return models, calls


def source_study_world(mid, seed, fit, witness=private_witness):
    """This function consumes HELD on real witness; never call from unit tests."""
    require(type(mid) is int and mid in MAP_IDS
            and type(seed) is int and seed in SEEDS, "WORLD_ID")
    shared,calls = run_shared_prefix(fit,mid,seed,witness)
    arc = shared["archive"]
    t16 = {"slot_A_hash":slot_digest(arc),
           "slot_A_high":a_slot_high(arc),
           "slot_A_assimilated":arc.slots[0].assimilated,
           "slot_A_brier":high_brier(arc.slots[0],"H0")}
    output={}
    for branch in BRANCHES:
        methods={name:cold_copy(m) for name,m in shared.items()}
        at32=None
        k_scores={name:{} for name in ARMS}
        b_loss={name:[] for name in ARMS}
        for t in range(PREFIX,N):
            if t == B_END:
                at32={name:{
                    "old_A_brier":high_brier(m,"H0"),
                    "slot_A_hash":slot_digest(m) if isinstance(m,Pair) else None,
                    "slot_A_high":a_slot_high(m) if isinstance(m,Pair) else None,
                    "slot_A_assimilated":m.slots[0].assimilated
                    if isinstance(m,Pair) else None,
                    "received":m.received if isinstance(m,Pair) else len(m.rows),
                } for name,m in methods.items()}
                methods={name:cold_copy(m) for name,m in methods.items()}
            c,a=public_tape(t)
            if PREFIX <= t < B_END:
                private_law = b_law(seed) if branch == "treatment_B" else "H0"
                for name,m in methods.items():
                    b_loss[name].append(high_brier(m,private_law))
            y=witness(mid,seed,t,a,branch)
            require(type(y) is int and y in (0,1),"WITNESS_TYPE")
            calls+=1
            for m in methods.values():
                m.observe(t,c,a,y)
            k=t+1-B_END
            if k in K:
                for name,m in methods.items():
                    k_scores[name][str(k)]=high_brier(m,"H0")
        require(at32 is not None and all(set(v)=={"4","8"}
                     for v in k_scores.values()),"SNAPSHOT_K")
        for name,m in methods.items():
            require((m.received if isinstance(m,Pair) else len(m.rows))==N,
                    "MODEL_WITNESS_COUNT")
            cold_copy(m)
        output[branch]={
            "at32":at32,
            "return_after_k":k_scores,
            "middle_brier":{name:sum(a)/len(a) for name,a in b_loss.items()}
        }
    require(calls == 80, "SOURCE_CALL_BUDGET")
    a32=output["treatment_B"]["at32"]["archive"]
    retained=(a32["slot_A_hash"]==t16["slot_A_hash"]
              and a32["slot_A_high"]==t16["slot_A_high"]
              and a32["slot_A_assimilated"]==t16["slot_A_assimilated"])
    return {"map_group":mid,"seed":seed,"B_family":b_family(seed),
            "phase_support":True,"source_calls":calls,"t16":t16,
            "treatment_A_slot_retained_through_B":retained,
            "forks":output}


def proof():
    began=time.monotonic()
    p=protocol()
    support=phase_coverage()
    fit={mid:trained(mid) for mid in MAP_IDS}
    worlds=[source_study_world(mid,seed,fit[mid])
            for mid in MAP_IDS for seed in SEEDS]
    require(len(worlds)==24 and sum(w["source_calls"] for w in worlds)==1920,
            "FIRST_USE_BUDGET")
    family_metrics={}
    for family in ("known_H2","unfamiliar_H1"):
        rows=[w for w in worlds if w["B_family"]==family]
        require(len(rows)==12,"FAMILY_SIZE")
        means={}
        for arm in ARMS:
            means[arm]={
                "return_k4":sum(w["forks"]["treatment_B"]["return_after_k"][arm]["4"]
                                for w in rows)/12,
                "return_k8":sum(w["forks"]["treatment_B"]["return_after_k"][arm]["8"]
                                for w in rows)/12,
                "middle_brier":sum(w["forks"]["treatment_B"]["middle_brier"][arm]
                                    for w in rows)/12,
                "paired_t32_A_exposure":sum(
                    w["forks"]["treatment_B"]["at32"][arm]["old_A_brier"]-
                    w["forks"]["control_A"]["at32"][arm]["old_A_brier"]
                    for w in rows)/12
            }
        wins={ctrl:sum(
            w["forks"]["treatment_B"]["return_after_k"]["archive"]["8"] <
            w["forks"]["treatment_B"]["return_after_k"][ctrl]["8"]
            for w in rows) for ctrl in ("switching_bayes","rolling8")}
        family_metrics[family]={"methods":means,"archive_k8_paired_wins":wins}
    baseline=sum(w["t16"]["slot_A_brier"] for w in worlds)/24
    hypotheses={
        "P0_complete_public_physical_support":len(support)==6,
        "P1_old_A_trained_at_t16":baseline <= .235,
        "H1_return_archive_better_than_both_controls_each_family":all(
            family_metrics[f]["methods"]["archive"]["return_k8"] <=
            family_metrics[f]["methods"][ctrl]["return_k8"]-.005 and
            family_metrics[f]["archive_k8_paired_wins"][ctrl]>=9
            for f in family_metrics for ctrl in ("switching_bayes","rolling8")),
        "H2_live_A_preserved_through_B":all(
            w["treatment_A_slot_retained_through_B"] for w in worlds),
        "H3_B_learning_noninferior_each_family":all(
            family_metrics[f]["methods"]["archive"]["middle_brier"] <=
            family_metrics[f]["methods"]["switching_bayes"]["middle_brier"]+.005
            for f in family_metrics),
        "H4_source_budget_cold_and_platform_qualified":all(
            w["source_calls"]==80 for w in worlds),
    }
    return {
        "schema":SCHEMA,"protocol_blob":PROTO_BLOB,"prereg_commit":PREREG,
        "source_mode":MODE,"support":support,
        "historical_FIT_per_map":236,"held_world_pairs":24,
        "unique_source_witnesses":1920,"model_level_per_arm_fork_actions":2304,
        "at_t16_old_A_brier":baseline,"family_metrics":family_metrics,
        "frozen_hypotheses":hypotheses,"worlds":worlds,
        "development_verdict":("DEVELOPMENT_SUPPORTED_SYNTHETIC"
              if all(hypotheses.values()) else
              "UNDERTRAINED_OLD_A" if not hypotheses["P1_old_A_trained_at_t16"]
              else "DEVELOPMENT_MIXED_OR_NO_GO"),
        "scientific":"SCIENCE_NO_GO_SYNTHETIC_NOT_NATIVE",
        "accepted_native_modified":False,"original_first_use_426":False,
        "deployment":"NONE","script_wall_seconds":time.monotonic()-began
    }


if __name__=="__main__":
    print(json.dumps(proof(),sort_keys=True))
