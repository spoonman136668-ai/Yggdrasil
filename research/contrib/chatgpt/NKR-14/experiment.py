"""NKR-14: blind out-of-family action-effect stress + information bound.

A new set of twelve Boolean mechanisms is defined ONLY in this evaluation
module; the unchanged NKR-13 learner never imports or sees world labels,
operator syntax, ground-truth truth tables, or cold outcomes.

The equal-information unrestricted truth-table comparator enumerates its
possible completions mathematically. It avoids pretending eight observed
effect bits determine the remaining eight independent bits.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from yggdrasil.native_operator_discovery import NativeOperatorDiscovery
from yggdrasil.native_intervention_repair import (
    BUNDLE_SCHEMA, SOURCE_MODE, SOURCE_KIND, canonical, digest,
)
from yggdrasil.public_causal_cells import PublicCausalCells

BASE=(1,2,4,8,3,5,6,9,10,12,13,14)
TRAIN=(0,1,2,4,8,3,5,10)
COLD=(6,7,9,11,12,13,14,15)
N_WORLDS=12
ACTION_SEQUENCE=((0,1),(0,0))+tuple(
    (x,a) for x in TRAIN[1:] for a in (0,1))


def bit(x, i):
    return (x>>i)&1


def hidden_operator(world, context):
    """Environment-only mechanisms, none a single positive conjunction.

    These are experimenter-authored families, NOT discovered by the model.
    The source/learner never receives this function or the world ID.
    """
    x=[bit(context,i) for i in range(4)]
    if world==0: return x[0]^x[1]
    if world==1: return x[0]|x[1]
    if world==2: return 1-(x[0]&x[1])
    if world==3: return 1-(x[0]^x[2])
    if world==4: return int(sum(x[:3])==1)
    if world==5: return int(sum(x[:3])>=2)
    if world==6: return x[0]&(1-x[1])
    if world==7: return x[1] if x[0] else x[2]
    if world==8: return (x[0]|x[1])&x[2]
    if world==9: return x[0]^(x[1]&x[2])
    if world==10: return int(sum(x)>=2)
    if world==11: return (x[0]^x[1])|(x[2]^x[3])
    raise ValueError("NKR14_UNKNOWN_WORLD")


class HiddenWorld:
    __slots__=("world","actions")
    def __init__(self, world):
        if type(world) is not int or not 0<=world<N_WORLDS:
            raise ValueError("NKR14_WORLD_INVALID")
        self.world=world
        self.actions=0

    def intervene(self, context, action, *, old=False):
        if (type(context) is not int or not 0<=context<16
                or type(action) is not int or action not in (0,1)):
            raise ValueError("NKR14_ACTION_INVALID")
        self.actions+=1
        if old:
            return ((context & (1<<(self.world%4))).bit_count()&1)^action
        base=(context&BASE[self.world]).bit_count()&1
        return base ^ (action & hidden_operator(self.world,context))


def freeze_bundle(name, records):
    return canonical({
        "schema":BUNDLE_SCHEMA,"source_id":name,
        "source_kind":SOURCE_KIND,"source_mode":SOURCE_MODE,
        "records":[list(r) for r in records],
    })


def warmup(env):
    return [(f"warm-nkr14-{env.world:02d}-{i:02d}",x,a,
             env.intervene(x,a,old=True))
            for i,(x,a) in enumerate((x,a)
            for x in range(16) for a in (0,1))]


def source_visible_actions(env):
    return [(f"trial-nkr14-{env.world:02d}-{i:02d}",x,a,
             env.intervene(x,a))
            for i,(x,a) in enumerate(ACTION_SEQUENCE)]


class UnrestrictedBooleanEffectControl:
    """Independent exact 16-bit Boolean function version-space control.

    The action-zero parity baseline and paired action effects at eight TRAIN
    contexts are fitted using *only* the same 16 observed intervention rows.
    No other hypothesis family is imposed. Unknown cold action-1 effects
    have two possible values each => 256 consistent complete functions.
    """
    __slots__=("intercept","base_mask","effects","completions")

    def __init__(self, source_rows):
        if (type(source_rows) not in (list,tuple)
                or len(source_rows)!=16
                or tuple((x,a) for _,x,a,_ in source_rows)!=ACTION_SEQUENCE):
            raise ValueError("NKR14_VISIBLE_INTERVENTION_CONTRACT")
        observed={(x,a):outcome for _,x,a,outcome in source_rows}
        intercept=observed[(0,0)]
        base_mask=0
        for i in range(4):
            if observed[(1<<i,0)]!=intercept:
                base_mask|=1<<i
        if any(observed[(x,0)] !=
               (intercept^((x&base_mask).bit_count()&1))
               for x in TRAIN):
            raise ValueError("NKR14_VISIBLE_BASELINE_UNIDENTIFIABLE")
        effects={x:observed[(x,1)]^observed[(x,0)] for x in TRAIN}
        self.intercept=intercept
        self.base_mask=base_mask
        self.effects=effects
        self.completions=1<<(16-len(effects))

    def predict(self, context, action):
        if (type(context) is not int or not 0<=context<16
                or type(action) is not int or action not in (0,1)):
            raise ValueError("NKR14_CONTROL_QUERY_INVALID")
        base=self.intercept^((context&self.base_mask).bit_count()&1)
        if action==0:
            return base
        if context in self.effects:
            return base^self.effects[context]
        return None


def score(pred, expected):
    return int(pred is not None and pred==expected)


def run_frozen():
    started=time.monotonic()
    before_native=PublicCausalCells().snapshot()
    metrics={
        "worlds":12,"prior_memory_queries":384,
        "new_public_observations_per_world":16,
        "cold_queries":192,
        "native_operator_proposals":0,
        "native_unsupported_or_unqualified":0,
        "native_cold_correct":0,"native_cold_coverage":0,
        "native_confident_wrong":0,"native_cold_abstentions":0,
        "unrestricted_control_correct":0,
        "unrestricted_control_coverage":0,
        "unrestricted_control_confident_wrong":0,
        "unrestricted_control_abstentions":0,
        "independent_consistent_truth_tables_per_world":256,
        "old_retention_correct":0,
        "exact_cold_checkpoint_restores":0,
        "visible_hidden_context_overlaps":0,
        "in_family_full_truth_table_matches":0,
    }
    worlds=[]
    for world in range(N_WORLDS):
        # Frozen new operator source truth table is OUTSIDE all fifteen
        # conjunction templates across *all* 16 contexts; no env name or
        # function is ever supplied to NativeOperatorDiscovery.
        if any(all(hidden_operator(world,x)==int((x&mask)==mask)
                   for x in range(16)) for mask in range(1,16)):
            metrics["in_family_full_truth_table_matches"]+=1
        env=HiddenWorld(world)
        old=warmup(env)
        old_raw=freeze_bundle(f"nkr14-warm-{world:02d}",old)
        prior=NativeOperatorDiscovery.from_warmup(old_raw,digest(old_raw))
        prior_hash=prior.checkpoint_sha256
        visible=source_visible_actions(env)
        if set(x for _,x,_,_ in visible)!=set(TRAIN):
            raise AssertionError("NKR14_PUBLIC_EVIDENCE_CONTEXT_DRIFT")
        if set(COLD)&set(x for _,x,_,_ in visible):
            metrics["visible_hidden_context_overlaps"]+=1
        source=freeze_bundle(f"nkr14-public-{world:02d}",visible)
        proposed,receipt=prior.stage_public_interventions(source,digest(source))
        if proposed.operator_discovered:
            metrics["native_operator_proposals"]+=1
        else:
            metrics["native_unsupported_or_unqualified"]+=1
        if prior.checkpoint_sha256!=prior_hash:
            raise AssertionError("NKR14_OLD_EVIDENCE_OVERWRITTEN")
        # Only a source-repaired model can be used as a prediction of the
        # changed environment. A rejected candidate's stale warm prior is
        # *not* misrepresented as new-world knowledge.
        cold=(NativeOperatorDiscovery(proposed.checkpoint(),
                                      proposed.checkpoint_sha256)
              if proposed.operator_discovered else None)
        if cold is not None and cold.checkpoint()==proposed.checkpoint():
            metrics["exact_cold_checkpoint_restores"]+=1
        conservative=UnrestrictedBooleanEffectControl(visible)
        if conservative.completions!=256:
            raise AssertionError("NKR14_UNRESTRICTED_VERSION_SPACE_DRIFT")
        row={"world":world,"candidate_qualified":proposed.operator_discovered,
             "candidate_status":receipt["classification"],
             "version_space":conservative.completions,
             "native_correct":0,"native_wrong":0,"native_coverage":0,
             "unrestricted_correct":0,"unrestricted_coverage":0}
        for x in COLD:
            for action in (0,1):
                truth=env.intervene(x,action)
                info=(cold.predict(x,action) if cold is not None else None)
                guessed=info["public_outcome"] if info is not None else None
                control=conservative.predict(x,action)
                if info is not None and (
                    info["native_accepted"] or info["can_write_causal_owner"]
                    or info["can_write_historical_facts"] or info["scientific_pass"]
                ):
                    raise AssertionError("NKR14_HIDDEN_REALITY_PROMOTED")
                metrics["native_cold_correct"]+=score(guessed,truth)
                metrics["native_cold_coverage"]+=int(guessed is not None)
                metrics["native_confident_wrong"]+=int(
                    guessed is not None and guessed!=truth)
                metrics["native_cold_abstentions"]+=int(guessed is None)
                metrics["unrestricted_control_correct"]+=score(control,truth)
                metrics["unrestricted_control_coverage"]+=int(control is not None)
                metrics["unrestricted_control_confident_wrong"]+=int(
                    control is not None and control!=truth)
                metrics["unrestricted_control_abstentions"]+=int(control is None)
                row["native_correct"]+=score(guessed,truth)
                row["native_wrong"]+=int(guessed is not None and guessed!=truth)
                row["native_coverage"]+=int(guessed is not None)
                row["unrestricted_correct"]+=score(control,truth)
                row["unrestricted_coverage"]+=int(control is not None)
        for x in range(16):
            for action in (0,1):
                truth=env.intervene(x,action,old=True)
                metrics["old_retention_correct"]+=score(prior.prior(x,action),truth)
                if cold is not None and cold.prior(x,action)!=prior.prior(x,action):
                    raise AssertionError("NKR14_OLD_WARM_MEMORY_INTERFERED")
        worlds.append(row)
    if PublicCausalCells().snapshot()!=before_native:
        raise AssertionError("NKR14_NATIVE_OWNER_STATE_MUTATED")
    if (metrics["in_family_full_truth_table_matches"]!=0
            or metrics["visible_hidden_context_overlaps"]!=0
            or metrics["unrestricted_control_correct"]!=96
            or metrics["unrestricted_control_coverage"]!=96
            or metrics["unrestricted_control_confident_wrong"]!=0
            or metrics["unrestricted_control_abstentions"]!=96
            or metrics["old_retention_correct"]!=384):
        raise AssertionError("NKR14_FROZEN_SOURCE_OR_SAFE_CONTROL_DRIFT")
    exposed=(metrics["native_confident_wrong"]>0 or
             metrics["native_unsupported_or_unqualified"]>0)
    return {
        "schema":"yggdrasil.nkr14.unseen-family-identifiability-result.v1",
        "classification":"UNKNOWN_OPERATOR_FAMILY_LIMIT_EXPOSED"
        if exposed else "UNSEEN_OPERATOR_STRESS_NOT_FALSIFIED",
        "source_mode":"engineering_fixture_only",
        "source_authenticity":"SELF_GENERATED_NOT_EXTERNAL",
        "function_family_labels_visible_to_learner":False,
        "unrestricted_version_space_exponent":8,
        "unrestricted_worlds_consistent_functions":256,
        "cold_queries":192,
        "frozen_falsification_criteria_met":exposed,
        "science_pass":False,"native_accepted":False,
        "model_operator_grammar_unmodified":True,
        "reusing_original_Wikidata_history":False,
        "new_authentic_action_relations":0,
        "per_world":worlds,"totals":metrics,
        "wall_seconds":time.monotonic()-started,
    }


if __name__=="__main__":
    print("NKR14_FROZEN_UNSEEN_FAMILY="+json.dumps(
        run_frozen(),sort_keys=True,separators=(",",":")),flush=True)
