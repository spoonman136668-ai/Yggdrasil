"""KNOW26: discover a causal probe from opaque action/consequence observations.

Synthetic independent contributor evidence, not the accepted Yggdrasil learner.
Pre-score final prereg commit: 116f42959cf4ccbf57713444785a4f5f45fd2b3f.
The private mapping and truth are used ONLY by the environment/evaluator.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import time
from pathlib import Path

SCHEMA = "yggdrasil.know26.opaque-affordance-result.v1"
PROTOCOL = "yggdrasil.know26.opaque-action-affordance-transfer-prereg.v1"
PREREG = "116f42959cf4ccbf57713444785a4f5f45fd2b3f"
SOURCE = "engineering_fixture_only"
GROUPS = ("G0", "G1", "G2")
MAPS = {"G0":(0,2,4,1), "G1":(0,4,1,2), "G2":(0,1,2,4)}
FIT = {"G0":((13101,"FIT_A"),(13107,"FIT_B")),
       "G1":((13201,"FIT_A"),(13209,"FIT_B")),
       "G2":((13301,"FIT_A"),(13311,"FIT_B"))}
HELD_SEEDS = {"G0":(13401,13407),"G1":(13501,13513),"G2":(13601,13609)}
RULES = ("x2xorx1","x2xorand","notx2","x0xorx1")
ARMS = ("episode_effect_fit", "conventional_episode_beta",
        "pooled_beta_fit", "no_fit_held_beta", "rolling_fit_last2",
        "fixed_label1", "random_label", "privileged_mapping_oracle",
        "uninformed_p05")
POSITIVE = frozenset(RULES[:3])


def require(ok, code):
    if not ok:
        raise ValueError("YGG_KNOW26_"+code)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),
                      ensure_ascii=True,allow_nan=False).encode("ascii")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def protocol():
    d=json.loads(Path(__file__).with_name("know26_opaque_affordance_protocol.json")
                 .read_text("utf-8"))
    require(d.get("schema")==PROTOCOL
            and d.get("source_mode")==SOURCE
            and d.get("fit",{}).get("total_actions")==384
            and d.get("held",{}).get("held_actions_per_arm")==1152
            and d.get("held",{}).get("queries_per_arm")==96
            and d["predicates"]["H2"].endswith("0.01500.")
            and d["predicates"]["H3"].endswith("0.01000.")
            and d["predicates"]["H6"].startswith("Matched conventional")
            and d.get("prereg_correction","").startswith("Before any source"),
            "FROZEN_PROTOCOL")
    return d


def context(t,limit):
    require(type(t) is int and 0<=t<limit,"PUBLIC_TIME")
    return t%4


def action(t):
    require(type(t) is int and 0<=t<64,"PUBLIC_TIME")
    return (t//4)%4


def private_law(phase, effective):
    require(type(effective) is int and 0<=effective<8, "PRIVATE_CONTEXT")
    x0,x1,x2=effective&1,(effective>>1)&1,(effective>>2)&1
    return {
        "FIT_A":x2,
        "FIT_B":x2^x0,
        "H0":x2^x1,
        "H1":x2^(x0&x1),
        "H2":1^x2,
        "H3":x0^x1
    }[phase]


def source_tuple(group, seed, phase, t, a):
    require(group in GROUPS and type(seed) is int and
            type(t) is int and type(a) is int and 0<=a<4,
            "PRIVATE_SOURCE")
    if phase.startswith("FIT_"):
        require((seed,phase) in FIT[group] and 0<=t<64,
                "FIT_SOURCE_PIN")
    else:
        require(phase in ("H0","H1","H2","H3")
                and seed in HELD_SEEDS[group] and 0<=t<48,
                "HELD_SOURCE_PIN")
    return group,seed,phase,t,a


def consequence(group,seed,phase,t,a):
    source_tuple(group,seed,phase,t,a)
    c=t%4
    effective=c^MAPS[group][a]
    q=.85 if private_law(phase,effective) else .15
    raw=hashlib.sha256(
        f"know26:private:reward:v1:{group}:{seed}:{phase}:{t}"
        .encode("ascii")).digest()
    return int(int.from_bytes(raw[:8],"big")/2**64 < q)


def fit_rows(group):
    require(group in GROUPS,"PUBLIC_GROUP")
    out=[]
    for episode,(seed,phase) in enumerate(FIT[group]):
        for t in range(64):
            c=context(t,64);a=action(t)
            out.append([episode,t,c,a,consequence(group,seed,phase,t,a)])
    require(len(out)==128,"FIT_BUDGET")
    return out


def held_rows(group,seed,idx):
    require(group in GROUPS and seed in HELD_SEEDS[group]
            and type(idx) is int and 0<=idx<4,"FROZEN_HELD")
    phase="H"+str(idx)
    out=[]
    for t in range(48):
        c=context(t,48);a=action(t)
        out.append([t,c,a,consequence(group,seed,phase,t,a)])
    require(len(out)==48,"HELD_BUDGET")
    return out


def beta_mean(vals):
    return (sum(vals)+1)/(len(vals)+2)


class FitState:
    """Exact cold-preserved public episode/action/outcome records; no private law labels."""
    def __init__(self, rows, *, source_mode=SOURCE):
        require(source_mode==SOURCE and type(rows) is list and len(rows)==128,
                "FIT_SOURCE_MODE_OR_LENGTH")
        for index,row in enumerate(rows):
            ep,t=divmod(index,64)
            require(type(row) is list and len(row)==5
                    and all(type(x) is int for x in row)
                    and row[:4]==[ep,t,t%4,(t//4)%4]
                    and row[4] in (0,1),"FIT_ORDER_OR_WITNESS")
        self.rows=[list(row) for row in rows]
        self.cursor=len(self.rows)

    def mean(self,ep,c,a):
        require(type(ep) is int and ep in (0,1)
                and type(c) is int and c in (0,1,2,3)
                and type(a) is int and 0<=a<4,"PUBLIC_FIT_QUERY")
        vals=[row[4] for row in self.rows
              if row[0]==ep and row[2]==c and row[3]==a]
        require(len(vals)==4,"FIT_CELL_BUDGET")
        return beta_mean(vals)

    def checkpoint(self):
        return canonical({"schema":"yggdrasil.know26.fit-cold.v1",
                          "source_mode":SOURCE,"rows":self.rows,
                          "accepted_native":False,
                          "scientific_gain_verified":False})

    @classmethod
    def restore(cls, raw, expected):
        require(type(raw) is bytes and len(raw)<16384
                and type(expected) is str and digest(raw)==expected,
                "COLD_PIN")
        def unique(pairs):
            d={}
            for key,value in pairs:
                require(key not in d,"COLD_DUPLICATE_KEY")
                d[key]=value
            return d
        try:
            doc=json.loads(raw.decode("ascii"),object_pairs_hook=unique)
            require(type(doc) is dict and set(doc)=={
                "schema","source_mode","rows","accepted_native",
                "scientific_gain_verified"}
                and doc["schema"]=="yggdrasil.know26.fit-cold.v1"
                and doc["source_mode"]==SOURCE
                and doc["accepted_native"] is False
                and doc["scientific_gain_verified"] is False
                and canonical(doc)==raw,"COLD_SCHEMA")
            model=cls(doc["rows"])
            require(model.checkpoint()==raw,"COLD_BYTES")
            return model
        except (KeyError,TypeError,ValueError,UnicodeError,OverflowError) as e:
            raise ValueError("YGG_KNOW26_BAD_COLD") from e


def action_scores(rows,method):
    """Only public evidence. Private mapping/law/seed cannot enter this function."""
    require(method in ("episode","pooled","rolling","held"),"EVIDENCE_METHOD")
    require(type(rows) is list and len(rows) in (48,128),"ROW_COUNT")
    scores=[]
    for a in (1,2,3):
        val=0.0
        episode_range=(0,1) if method in ("episode","rolling") else (0,)
        for ep in episode_range:
            for c in range(4):
                def get(k):
                    matches=[r[-1] for r in rows
                             if r[-3]==c and r[-2]==k
                             and (method not in ("episode","rolling")
                                  or r[0]==ep)]
                    if method=="rolling": matches=matches[-2:]
                    require(matches,"ACTION_CELL_EMPTY")
                    return beta_mean(matches)
                val+=abs(get(a)-get(0))
        scores.append(val)
    return scores


def label_from_scores(scores):
    require(type(scores) is list and len(scores)==3
            and all(type(v) is float and math.isfinite(v) for v in scores),
            "SCORES")
    return max((1,2,3),key=lambda a:(scores[a-1],-a))


def conventional_label(rows):
    """Independently coded conventional per-episode Beta comparator."""
    require(type(rows) is list and len(rows)==128,"CONVENTIONAL_FIT")
    tab={(e,c,a):[] for e in range(2) for c in range(4) for a in range(4)}
    for e,t,c,a,y in rows:
        tab[e,c,a].append(y)
    score=[]
    for a in range(1,4):
        total=0.0
        for ep in range(2):
            for c in range(4):
                lhs=(sum(tab[ep,c,a])+1)/(len(tab[ep,c,a])+2)
                rhs=(sum(tab[ep,c,0])+1)/(len(tab[ep,c,0])+2)
                total+=abs(lhs-rhs)
        score.append(total)
    return sorted(range(1,4),key=lambda a:(-score[a-1],a))[0]


def held_forecast(rows, opaque_label,c):
    require(type(rows) is list and len(rows)==48
            and type(opaque_label) is int and 1<=opaque_label<=3
            and type(c) is int and 0<=c<4,"HELD_FORECAST")
    vals=[r[3] for r in rows if r[1]==c and r[2]==opaque_label]
    require(len(vals)==3,"HELD_CELL_BUDGET")
    return beta_mean(vals)


def high_true_prob(idx,c):
    require(type(idx) is int and 0<=idx<4
            and type(c) is int and 0<=c<4,"EVALUATOR_ONLY")
    return .85 if private_law("H"+str(idx),c^4) else .15


def expected_brier(p,q):
    return q*(1-q)+(p-q)*(p-q)


def proof():
    t0=time.monotonic()
    protocol()
    fitted={group:FitState(fit_rows(group)) for group in GROUPS}
    labels={}
    before={}
    fit_readout={}
    for group,model in fitted.items():
        raw=model.checkpoint()
        before[group]=digest(raw)
        cold=FitState.restore(raw,digest(raw))
        require(cold.checkpoint()==raw,"FIT_COLD")
        fit_readout[group]=[[[model.mean(ep,c,a) for a in range(4)]
                              for c in range(4)] for ep in range(2)]
        labels[group]={
            "episode_effect_fit":label_from_scores(action_scores(model.rows,"episode")),
            "conventional_episode_beta":conventional_label(model.rows),
            "pooled_beta_fit":label_from_scores(action_scores(model.rows,"pooled")),
            "rolling_fit_last2":label_from_scores(action_scores(model.rows,"rolling")),
            "fixed_label1":1}
    predictions={arm:[] for arm in ARMS}
    selections={arm:[] for arm in ARMS}
    group_selected={group:labels[group]["episode_effect_fit"] for group in GROUPS}
    events=0
    for gi,group in enumerate(GROUPS):
        for ri in range(4):
            for si,seed in enumerate(HELD_SEEDS[group]):
                rows=held_rows(group,seed,ri)
                events+=len(rows)
                random_label=random.Random(gi*347+ri*19+si+17).randrange(1,4)
                oracle_label=MAPS[group].index(4)  # evaluator-only privileged baseline
                for arm in ARMS:
                    if arm in labels[group]:
                        label=labels[group][arm]
                    elif arm=="no_fit_held_beta":
                        label=label_from_scores(action_scores(rows,"held"))
                    elif arm=="random_label":
                        label=random_label
                    elif arm=="privileged_mapping_oracle":
                        label=oracle_label
                    elif arm=="uninformed_p05":
                        label=None
                    else:
                        raise ValueError("YGG_KNOW26_UNKNOWN_ARM")
                    selections[arm].append((group,ri,seed,label))
                    forecasts=[held_forecast(rows,label,c) if label is not None
                               else .5 for c in range(4)]
                    losses=[expected_brier(p,high_true_prob(ri,c))
                            for c,p in enumerate(forecasts)]
                    predictions[arm].append({
                        "group":group,"rule_index":ri,"seed":seed,
                        "selected_opaque_label":label,
                        "predictions":forecasts,"losses":losses})
    require(events==1152 and
            all(len(rows)==24 for rows in predictions.values()),"HELD_BUDGET")
    raw_same=all(before[g]==digest(fitted[g].checkpoint())
                 and fit_readout[g]==[[[fitted[g].mean(ep,c,a)
                  for a in range(4)] for c in range(4)] for ep in range(2)]
                 and FitState.restore(fitted[g].checkpoint(),
                     before[g]).checkpoint()==fitted[g].checkpoint()
                 for g in GROUPS)
    parity=all(predictions["episode_effect_fit"][i]["predictions"]==
               predictions["conventional_episode_beta"][i]["predictions"]
               and selections["episode_effect_fit"][i][-1]==
                   selections["conventional_episode_beta"][i][-1]
               for i in range(24))
    briers={}
    correctness={}
    for arm,rows in predictions.items():
        positive=[z for z in rows if z["rule_index"]<3]
        negative=[z for z in rows if z["rule_index"]==3]
        briers[arm]={
            "positive_expected_brier":round(sum(sum(z["losses"]) for z in positive)/72,8),
            "negative_expected_brier":round(sum(sum(z["losses"]) for z in negative)/24,8),
            "overall_expected_brier":round(sum(sum(z["losses"]) for z in rows)/96,8)}
        correctness[arm]=sum(
            s[-1]==MAPS[s[0]].index(4) for s in selections[arm]
            if s[-1] is not None)
    cand=briers["episode_effect_fit"]
    nofit=briers["no_fit_held_beta"]
    pooled=briers["pooled_beta_fit"]
    h={
        "H1_all_three_unknown_maps_learned":
            all(group_selected[g]==MAPS[g].index(4) for g in GROUPS),
        "H2_FIT_vs_held_noFIT_gain_015":
            nofit["positive_expected_brier"]-cand["positive_expected_brier"]>=.015,
        "H3_FIT_vs_pooled_conventional_gain_010":
            pooled["positive_expected_brier"]-cand["positive_expected_brier"]>=.010,
        "H4_irrelevant_x2_not_worse_than_noFIT_015":
            cand["negative_expected_brier"]-nofit["negative_expected_brier"]<=.015,
        "H5_cold_FIT_functional_state":
            raw_same,
        "H6_matched_conventional_parity":
            parity and briers["episode_effect_fit"]==
                       briers["conventional_episode_beta"]}
    require(h["H5_cold_FIT_functional_state"] and
            h["H6_matched_conventional_parity"],"ENGINEERING_COLD_OR_PARITY")
    supported=all(h.values())
    mixed=(h["H5_cold_FIT_functional_state"] and
           h["H6_matched_conventional_parity"] and
           any(h[k] for k in list(h)[:4]))
    return {
        "schema":SCHEMA,"prereg_commit":PREREG,"source_mode":SOURCE,
        "fit_worlds":6,"fit_witnesses":384,"held_worlds":24,
        "held_witnesses_per_arm":events,"held_evaluator_queries_per_arm":96,
        "public_fit_group_probe_labels":group_selected,
        "per_arm_high_expected_brier":briers,
        "per_arm_true_probe_count_evaluator_only":correctness,
        "frozen_hypotheses":h,
        "development_verdict":("DEV_AFFORDANCE_TRANSFER_SUPPORTED" if supported
            else "DEV_MIXED_AFFORDANCE_TRANSFER" if mixed else "DEV_NO_GO"),
        "frozen_margins":{
            "FIT_vs_noFIT_positive_gain":round(nofit["positive_expected_brier"]-
                                               cand["positive_expected_brier"],8),
            "FIT_vs_pooled_positive_gain":round(pooled["positive_expected_brier"]-
                                                cand["positive_expected_brier"],8),
            "negative_harm_vs_noFIT":round(cand["negative_expected_brier"]-
                                           nofit["negative_expected_brier"],8),
            "oracle_over_candidate_positive_gain":round(
                cand["positive_expected_brier"]-
                briers["privileged_mapping_oracle"]["positive_expected_brier"],8)},
        "fit_cold_sha256_by_public_group":before,
        "fit_model_checkpoint_bytes":{g:len(fitted[g].checkpoint()) for g in GROUPS},
        "engineering_gate":"PASS","scientific_gate":"SCIENCE_NO_GO_SYNTHETIC",
        "native_modified":False,"original_first_use_426":False,
        "deployment":"NONE",
        "isolated_wall_seconds":round(time.monotonic()-t0,6)}
if __name__=="__main__":
    print("YGG_KNOW26_FROZEN_RECEIPT="+json.dumps(proof(),sort_keys=True))
