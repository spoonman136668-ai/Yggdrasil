"""KNOW12: identify source-feature roles from explicit witnessed consequences.

Source-free research only. The selector never sees the private feature-role
index, simulator equation, held labels, or real-source owner credentials.
No accepted Amalgam checkpoint, trained specialists or official world changed.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import random
import time

SEEDS = (404, 505, 606)
PREDICATES = (930, 931, 932, 933)
SUBJECT_BASE = 4_203_000_000
OBJECT_BASE = 4_202_000_000
FACT_ROWS = 21_343_681
FIT = 32
ENTITIES = 64
JOINT_SHA = "576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8"
IMAGE_SHA = "6dd87ba5bbf5fd7ecaffa6d48f674e34ce2a7cc7fa748ec7698d2c0a4cdae3d1"


def require(value, code):
    if not value:
        raise ValueError("YGG_KNOW12_" + code)


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("ascii")


def digest(raw):
    return sha256(raw).hexdigest()


def _domain(seed, seed_index, phase):
    require(seed in SEEDS and type(seed) is int and
            type(seed_index) is int and SEEDS[seed_index] == seed and
            type(phase) is int and phase in (0, 1), "FROZEN_COHORT")


def entity_subject(seed_index, entity):
    require(type(seed_index) is int and 0 <= seed_index < len(SEEDS) and
            type(entity) is int and 0 <= entity < ENTITIES, "ENTITY_DOMAIN")
    return SUBJECT_BASE + seed_index * 1000 + entity


def feature_object(phase, feature, bit):
    require(type(phase) is int and phase in (0, 1) and
            type(feature) is int and 0 <= feature < len(PREDICATES) and
            type(bit) is int and bit in (0, 1), "FEATURE_DOMAIN")
    return OBJECT_BASE + phase * 100 + feature * 10 + bit


def synthetic_world(seed, seed_index, phase):
    """Evaluator-only secret role, plus four candidate public bit columns.

    The learner and comparison fits receive ONLY the returned synthetic Q/P/Q
    facts and distinct witnessed action-consequence rows, never this role.
    """
    _domain(seed, seed_index, phase)
    modes = []
    for split in (0, 1):
        half = [0] * 16 + [1] * 16
        random.Random(seed * 10000 + phase * 100 + split + 19).shuffle(half)
        modes.extend(half)
    truth = tuple(modes)
    private_role = (seed_index + phase) % len(PREDICATES)
    cols = []
    for feature in range(len(PREDICATES)):
        if feature == private_role:
            cols.append(truth)
            continue
        values = [None] * ENTITIES
        for split in (0, 1):
            for mode in (0, 1):
                locations = [index for index in range(split*FIT, (split+1)*FIT)
                             if truth[index] == mode]
                require(len(locations) == 16, "MODE_BALANCE")
                bits = [0] * 8 + [1] * 8
                random.Random(seed * 100000 + phase * 10000 +
                              feature * 100 + split * 10 + mode).shuffle(bits)
                for index, bit in zip(locations, bits, strict=True):
                    values[index] = bit
        require(all(type(v) is int for v in values), "NUISANCE_COMPLETE")
        cols.append(tuple(values))
    return private_role, truth, tuple(cols)


def bundle(seed, seed_index, phase):
    from yggdrasil.native_cumulative_facts import BUNDLE_SCHEMA
    _role, _truth, columns = synthetic_world(seed, seed_index, phase)
    rows = [
        [entity_subject(seed_index, ent), PREDICATES[feature],
         feature_object(phase, feature, columns[feature][ent]),
         f"know12:{seed}:p{phase}:e{ent:03d}:f{feature}"]
        for ent in range(ENTITIES)
        for feature in range(len(PREDICATES))
    ]
    payload = {
        "schema": BUNDLE_SCHEMA, "source_id": f"know12-synthetic-{seed}-phase-{phase}",
        "source_kind": "direct_public_observation",
        "source_mode": "engineering_fixture_only",
        "records": sorted(rows, key=lambda r: r[3]),
    }
    require(len(rows) == 256, "BUNDLE_ROWS")
    raw = canonical(payload)
    require(len(raw) <= 196608, "BUNDLE_CAPACITY")
    return raw


def public_bit(facts, q, phase, feature):
    """Strict direct source-typed public fact; unknown or ambiguous abstains."""
    require(type(q) is int and type(feature) is int and
            0 <= feature < len(PREDICATES), "SOURCE_KEY")
    answers = [facts.fact(q, PREDICATES[feature], feature_object(phase,feature,bit))
               for bit in (0, 1)]
    supported = [
        x.get("classification") == "DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED"
        and x.get("source_mode") == "engineering_fixture_only"
        and x.get("witnessed") is True
        and x.get("native_accepted") is False
        and x.get("verified_new_real_knowledge") is False
        and x.get("can_write_causal_consequence") is False
        for x in answers]
    return supported.index(True) if supported.count(True) == 1 else None


def reward(phase, mode, action):
    require(all(type(x) is int and x in (0, 1)
                for x in (phase, mode, action)), "OUTCOME_DOMAIN")
    return int(action == mode) if phase == 0 else int(action != mode)


def witnessed_fit(seed, seed_index, phase):
    """Separate evaluator outcomes: no source-feature role index in rows."""
    _role, hidden, _features = synthetic_world(seed, seed_index, phase)
    return [(entity_subject(seed_index, entity), action,
             reward(phase, hidden[entity], action))
            for entity in range(FIT) for action in (0, 1)]


def public_training_rows(facts, observed, phase, feature):
    rows = []
    for q, action, outcome in observed:
        feature_value = public_bit(facts, q, phase, feature)
        if feature_value is None:
            return None
        rows.append([feature_value, action, outcome])
    return rows


def fit_native_role(facts, observed, phase, base_native):
    """Enumerate every candidate predicate under witnessed GF(2) consistency.

    No oracle role or simulator metadata is read. If multiple candidates fit,
    abstain rather than choose a source identity based on accidental ordering.
    """
    candidates = []
    for feature in range(len(PREDICATES)):
        rows = public_training_rows(facts, observed, phase, feature)
        if rows is None:
            continue
        try:
            child = base_native.stage_fit(
                phase, rows, digest(canonical(rows)), max_degree=1)
        except ValueError as err:
            if ("STOCHASTIC_OR_CONFLICTING_INPUT_MODEL_INADEQUATE" in str(err)
                    or "MODEL_CLASS_INADEQUATE" in str(err)):
                continue
            raise
        if all(child.predict(phase, value, action) == outcome
               for value, action, outcome in rows):
            candidates.append((feature, child))
    return candidates[0] if len(candidates) == 1 else None


def symbolic_role(facts, observed, phase):
    """Independent, fully fitted strongest conditional-count candidate search."""
    ranking = []
    for feature in range(len(PREDICATES)):
        rows = public_training_rows(facts, observed, phase, feature)
        if rows is None:
            continue
        groups = {}
        for mode, action, outcome in rows:
            groups.setdefault((mode, action), []).append(outcome)
        table = {k: Fraction(sum(v), len(v)) for k, v in groups.items()}
        loss = sum((table[(mode, action)] - outcome)**2
                   for mode, action, outcome in rows)
        ranking.append((loss, feature, table))
    if not ranking:
        return None
    low = min(item[0] for item in ranking)
    ties = [item for item in ranking if item[0] == low]
    return (ties[0][1], ties[0][2]) if len(ties) == 1 else None


def tree_role(facts, observed, phase):
    """Independent exhaustive depth-2 tree, all features and root orders."""
    candidates = []
    for feature in range(len(PREDICATES)):
        rows = public_training_rows(facts, observed, phase, feature)
        if rows is None:
            continue
        best = []
        for root in (0, 1):
            leaves = {}
            for a in (0, 1):
                for b in (0, 1):
                    bucket = [r[2] for r in rows
                              if r[root] == a and r[1-root] == b]
                    require(bucket, "TREE_FIT_CELL")
                    leaves[(a, b)] = Fraction(sum(bucket), len(bucket))
            loss = sum((leaves[(r[root], r[1-root])] - r[2])**2
                       for r in rows)
            best.append((loss, root, leaves))
        err, root, leaf = min(best, key=lambda x:(x[0],x[1]))
        candidates.append((err, feature, root, leaf))
    if not candidates:
        return None
    low = min(item[0] for item in candidates)
    tied = [x for x in candidates if x[0] == low]
    return (tied[0][1], tied[0][2], tied[0][3]) if len(tied)==1 else None


def blind_control(observed):
    counts = {action:[] for action in (0, 1)}
    for _q, action, outcome in observed:
        counts[action].append(outcome)
    return {k:Fraction(sum(v), len(v)) for k,v in counts.items()}


def score_held(facts, seed, seed_index, phase, native_role, symbolic, tree,
               blind):
    selected, native = native_role
    symbol_idx, symbolic_table = symbolic
    tree_idx, tree_root, tree_leaves = tree
    require(selected == symbol_idx == tree_idx, "CONTROL_ROLE_DISAGREEMENT")
    _private_idx, hidden, _features = synthetic_world(seed, seed_index, phase)
    losses = {k:Fraction(0) for k in
              ("native","symbolic","tree","blind","facts_only")}
    rewards = {k:0 for k in losses}
    readouts = []
    for entity in range(FIT, ENTITIES):
        q=entity_subject(seed_index,entity)
        bit=public_bit(facts,q,phase,selected)
        require(bit is not None, "HELD_FACT_NOT_GROUNDED")
        action_values={}
        for action in (0,1):
            prediction = native.predict(phase, bit, action)
            require(type(prediction) is int and prediction in (0,1),
                    "UNSUPPORTED_HELD_NATIVE")
            actual=reward(phase, hidden[entity], action)
            values={
                "native":Fraction(prediction),
                "symbolic":symbolic_table[(bit,action)],
                "tree":tree_leaves[(bit,action)[tree_root],(bit,action)[1-tree_root]],
                "blind":blind[action],
                "facts_only":Fraction(1,2),
            }
            for label, value in values.items():
                losses[label]+=(value-actual)**2
            action_values[action]=values
            readouts.append([q, bit, action, prediction])
        for label in rewards:
            pick = int(action_values[1][label] > action_values[0][label])
            rewards[label]+=reward(phase,hidden[entity],pick)
    require(len(readouts)==64, "HELD_COUNT")
    return {
        "readout_sha256":digest(canonical(readouts)),
        "selected_source_predicate":PREDICATES[selected],
        "held_actions":len(readouts),
        "brier":{k:[(v / len(readouts)).numerator,
                    (v / len(readouts)).denominator] for k,v in losses.items()},
        "correct_action_rewards":rewards,
    }


def read_fraction(value):
    return Fraction(value[0],value[1])


def prove(installed_session, joint_checkpoint):
    from yggdrasil.native_context_basis import NativeContextBasis
    from yggdrasil.native_context_basis import digest as native_digest
    from yggdrasil.native_cumulative_facts import CumulativeNativeFacts
    from yggdrasil.native_knowledge_activation import (
        open_installed_session, PINNED_ROWS, PINNED_PACKED_SHA)
    t0=time.monotonic()
    protocol=json.loads(Path(__file__).with_name("know12_protocol.json").read_bytes())
    require(protocol["schema"]==
            "yggdrasil.know12.blind-factual-predicate-role-selection-dev.v1"
            and protocol["seeds"] == list(SEEDS)
            and protocol["candidate_predicates"] == list(PREDICATES)
            and protocol["training_actions"][:4]=="both",
            "PREREG_DRIFT")
    original=Path(joint_checkpoint).read_bytes()
    require(digest(original)==JOINT_SHA, "HISTORICAL_AMALGAM_PIN")
    with open_installed_session(installed_session) as history:
        require(len(history._weights)==FACT_ROWS==PINNED_ROWS
                and PINNED_PACKED_SHA==IMAGE_SHA, "HISTORICAL_FACT_IMAGE")
        first,last=(tuple(history._weights.row_at(index))
                    for index in (0,FACT_ROWS-1))
        factual=CumulativeNativeFacts(history)
        frozen_fact_bytes=factual.checkpoint()
        results=[]
        correct_roles=0
        for seed_index,seed in enumerate(SEEDS):
            native=NativeContextBasis(context_bits=1)
            block={}
            for phase in (0,1):
                raw=bundle(seed,seed_index,phase)
                factual,receipt=factual.stage(raw,digest(raw))
                require(receipt["new_unique_facts"] == ENTITIES*len(PREDICATES),
                        "FACT_SOURCE_STAGE")
                witnessed=witnessed_fit(seed,seed_index,phase)
                candidate=fit_native_role(factual,witnessed,phase,native)
                symbolic=symbolic_role(factual,witnessed,phase)
                tree=tree_role(factual,witnessed,phase)
                require(candidate is not None and symbolic is not None and
                        tree is not None, "ROLE_NOT_UNIQUE")
                private_role,_,_=synthetic_world(seed,seed_index,phase)
                require(candidate[0] == private_role == symbolic[0] == tree[0],
                        "SELECTED_ROLE_WRONG")
                correct_roles+=1
                native=candidate[1]
                scored=score_held(factual,seed,seed_index,phase,candidate,
                                  symbolic,tree,blind_control(witnessed))
                require(read_fraction(scored["brier"]["native"])==0 and
                        read_fraction(scored["brier"]["symbolic"])==0 and
                        read_fraction(scored["brier"]["tree"])==0,
                        "EXACT_FITTED_CONTROL_PARITY")
                block["AB"[phase]] = scored
                if phase == 0:
                    original_A = scored["readout_sha256"]
                    original_A_native = candidate
                    original_A_symbolic = symbolic
                    original_A_tree = tree
                    original_A_blind=blind_control(witnessed)
            check_A=score_held(factual,seed,seed_index,0,
                               (original_A_native[0],native),
                               original_A_symbolic,original_A_tree,
                               original_A_blind)
            require(check_A["readout_sha256"]==original_A,
                    "SEPARATE_ADDRESS_READOUT_DRIFT")
            state=native.checkpoint()
            cold=NativeContextBasis.restore(state,native_digest(state))
            require(cold.checkpoint()==state,"NATIVE_COLD_RESTORE")
            for phase in (0,1):
                witnessed=witnessed_fit(seed,seed_index,phase)
                role,_,_=synthetic_world(seed,seed_index,phase)
                again=score_held(factual,seed,seed_index,phase,
                                 (role,cold),symbolic_role(factual,witnessed,phase),
                                 tree_role(factual,witnessed,phase),
                                 blind_control(witnessed))
                require(again==block["AB"[phase]],"COLD_READOUT")
            results.append({"seed":seed,"phase_results":block,
                            "native_candidate_checkpoint_sha256":native_digest(state),
                            "A_after_B_unchanged":True})
        stage_raw=factual.checkpoint()
        after_cold=CumulativeNativeFacts(history,stage_raw,
                                          checkpoint_sha256=factual.checkpoint_sha256)
        require(after_cold.checkpoint()==stage_raw and
                history.fact(*first)["witnessed"] and
                history.fact(*last)["witnessed"],"FACTS_COLD_RETENTION")
        for seed_index, seed in enumerate(SEEDS):
            for phase in (0,1):
                _,_,columns=synthetic_world(seed,seed_index,phase)
                for entity in range(ENTITIES):
                    for feature in range(len(PREDICATES)):
                        require(public_bit(after_cold,entity_subject(seed_index,entity),
                                           phase,feature)==columns[feature][entity],
                                "COLD_ROLE_FACT_LOSS")
        require(digest(Path(joint_checkpoint).read_bytes())==JOINT_SHA and
                history.fact(*first)["witnessed"] and
                history.fact(*last)["witnessed"],"HISTORICAL_MUTATION")
        total={key:Fraction(0) for key in
               ("native","symbolic","tree","blind","facts_only")}
        for entry in results:
            for phase in "AB":
                for key in total:
                    total[key]+=read_fraction(entry["phase_results"][phase]["brier"][key])
        means={k:[(v/6).numerator,(v/6).denominator] for k,v in total.items()}
        require(all(read_fraction(means[k])==0
                    for k in ("native","symbolic","tree"))
                and read_fraction(means["blind"])>0,
                "PRECOMMITTED_NULL_OR_PARITY")
        return {
            "schema":"yggdrasil.know12.source-role-identification-dev-result.v1",
            "classification":"SOURCE_FREE_SYNTHETIC_DEVELOPMENT",
            "frozen_seeds":list(SEEDS),
            "candidate_factual_rows":len(SEEDS)*2*ENTITIES*len(PREDICATES),
            "witnessed_synthetic_fit_actions":len(SEEDS)*2*FIT*2,
            "held_entity_action_forecasts":len(SEEDS)*2*(ENTITIES-FIT)*2,
            "identifiable_roles_on_fit":correct_roles,
            "selected_roles_grounded_in_interventions_not_source_metadata":True,
            "held_mean_brier_fraction":means,
            "no_role_oracle_passed_to_candidate":True,
            "native_tied_strongest_symbolic_and_tree":True,
            "A_after_B_unchanged_due_to_separate_slots":True,
            "old_historical_train_image_sha256":IMAGE_SHA,
            "original_archived_joint_sha256_unchanged":JOINT_SHA,
            "factual_and_native_candidate_cold_restore":True,
            "real_new_knowledge_learned":0,
            "original_world_source_first_uses":0,
            "canonical_model_trained":False,
            "scientific_pass":False,
            "development_decision":"DEV_NO_GO_STRONGEST_CONTROL_TIE",
            "deployment":"NONE",
            "case_receipts":results,
            "wall_seconds_excluding_download":round(time.monotonic()-t0,6),
        }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--installed-session",type=Path,required=True)
    p.add_argument("--joint-checkpoint",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    receipt=prove(args.installed_session,args.joint_checkpoint)
    args.output.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n",
                           encoding="utf-8")
    print("KNOW12_BLIND_ROLE_DEV="+json.dumps({
        "roles":receipt["identifiable_roles_on_fit"],
        "mean_brier":receipt["held_mean_brier_fraction"],
        "decision":receipt["development_decision"],
        "scientific_pass":False,
    },sort_keys=True),flush=True)


if __name__=="__main__":
    main()
