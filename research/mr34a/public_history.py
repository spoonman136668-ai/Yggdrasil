"""MR34A: genuinely source-native public-history information DEVELOPMENT audit.

Zero new world seeds, actors or cognitive hypotheses. Replay the ORIGINAL
already consumed MR32A cohort in unmodified source workers, verify its public
event digest, and compare frozen trained preaction probability forecasts on
previously consumed development seed partitions. No privileged evaluator fields
are read, no Yggdrasil coefficients are modified, no independent first use.
"""
from collections import OrderedDict, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
import time

import numpy as np

from research.mr15.public_view_delta import SOURCE_COMMIT, public_raw_view
from research.mr32a.original_native_cost import worker
from research.mr32a.isolated_worker import load_contract, peak_os_resident_bytes

FILE = Path(__file__).with_name("frozen_protocol.json")
SCHEMA = "yggdrasil.mr34a.public-history-information.dev.v1"
MODES = ("novelty", "contrast")
FAMILIES = ("DoorKeyEnv(size=8)", "EmptyEnv(size=8)")
SLOTS = 128
HORIZON = 2
PAD = bytes([255] + [0]*8)

def protocol():
    cfg = json.loads(FILE.read_text(encoding="utf-8"))
    original = load_contract()
    if (cfg["schema"] != SCHEMA or
        cfg["exact_parent_sha"] != "a7e85db2eefe975799acd2f2b23e981db0fcf91a" or
        cfg["independently_authored_original_source_sha"] != SOURCE_COMMIT or
        cfg["source_digest_previous_mr32a"] !=
            "cb12b87859c478fa1213bb0dbed3ec201f2ceff13b0de7ba988dc3a54747e729" or
        cfg["reuse_previously_consumed_mr32a_episodes"] != 96 or
        cfg["no_new_original_source_executions_or_seeds"] is not True or
        cfg["no_protected_first_use"] is not True or
        cfg["actor_modes"] != list(MODES) or
        cfg["training_reset_seeds"] !=
            {"DoorKey":[677,683,691,701], "Empty":[739,743]} or
        cfg["evaluation_reset_seeds_previously_consumed"] !=
            {"DoorKey":[709,719,727,733], "Empty":[751,757]} or
        cfg["original_stream_ids"] != [0,1,2,3] or
        cfg["native_max_original_steps_per_episode"] != 256 or
        cfg["max_cached_contexts_per_model"] != SLOTS or
        cfg["counts_prior_strength"] != 2 or
        cfg["no_validation_training_updates"] is not True or
        cfg["no_new_yggdrasil_parameters_or_model_changes"] is not True or
        original["development_door_seeds"] != [677,683,691,701,709,719,727,733] or
        original["development_empty_seeds"] != [739,743,751,757]):
        raise ValueError("MR34A_FROZEN_PROTOCOL_IDENTITY_DRIFT")
    return cfg

def digest_key(raw, action, hist, with_history):
    if len(raw) != 24 or type(action) is not int or not 0 <= action < 6:
        raise ValueError("MR34A_PUBLIC_INPUT_INVALID")
    if len(hist) != HORIZON or any(len(x) != 9 for x in hist):
        raise ValueError("MR34A_TEMPORAL_CONTEXT_INVALID")
    return sha256(raw + bytes([action]) +
                  (b"".join(hist) if with_history else b"")).digest()

def episodes(original_rows):
    grouped = defaultdict(list)
    for item in original_rows:
        # Only these source-PUBLIC fields are retained for inference:
        public = item["public"]
        action = item["action"]
        targets = item["targets"]
        if len(public) != 147 or len(targets) != 8:
            raise ValueError("MR34A_SOURCE_PUBLIC_FRAME_OR_TARGET_DRIFT")
        if any(x not in (0,1) for x in targets):
            raise ValueError("MR34A_NON_BINARY_PUBLIC_TARGET")
        grouped[(item["mode"], item["family"],
                 item["seed"], item["stream"])].append(
                     (item["step"], public, action, tuple(targets)))
    if len(grouped) != 96:
        raise ValueError("MR34A_ORIGINAL_EPISODE_COUNT_INVALID")
    result = {}
    for identity, rows in grouped.items():
        history = [PAD]*HORIZON
        samples = []
        for step, public, action, target in rows:
            if step != len(samples) or not 0 <= action < 6:
                raise ValueError("MR34A_SOURCE_CHRONOLOGY_DRIFT")
            current = bytes(public_raw_view(
                np.frombuffer(public,dtype=np.uint8).reshape((7,7,3))))
            samples.append((current, action, tuple(history), target))
            # Only AFTER recording the context may the public outcome update
            # the next step's history. No future action or world label enters.
            history = history[1:] + [bytes([action] + list(target))]
        result[identity] = samples
    return result

class FrozenCounts:
    """Same 128 FIFO keys and eight event-counter vectors per model."""
    def __init__(self, with_history):
        self.with_history = with_history
        self.table = OrderedDict()
        self.gl_n = [0]*6
        self.gl_success = [[0]*8 for _ in range(6)]
        self.sealed = False

    def learn(self, sample):
        if self.sealed:
            raise ValueError("MR34A_LEAKED_EVALUATION_UPDATE")
        raw, action, history, y = sample
        key = digest_key(raw, action, history, self.with_history)
        if key not in self.table:
            if len(self.table) >= SLOTS:
                self.table.popitem(last=False)
            self.table[key] = [0,[0]*8]
        slot = self.table[key]
        slot[0] += 1
        self.gl_n[action] += 1
        for i, bit in enumerate(y):
            slot[1][i] += bit
            self.gl_success[action][i] += bit

    def seal(self):
        self.sealed = True
        if len(self.table) > SLOTS:
            raise ValueError("MR34A_MODEL_CAPACITY_DRIFT")

    def forecast(self, sample, ablate_history=False):
        if not self.sealed:
            raise ValueError("MR34A_NOT_FROZEN")
        raw, action, history, _ = sample
        if ablate_history:
            history = (PAD,)*HORIZON
        key = digest_key(raw, action, history, self.with_history)
        global_p = [(self.gl_success[action][i]+1)/
                    (self.gl_n[action]+2) for i in range(8)]
        value = self.table.get(key)
        if value is None:
            return global_p
        n, success = value
        return [(success[i]+2*global_p[i])/(n+2) for i in range(8)]

    def checkpoint_bytes(self):
        state = {
            "history":self.with_history,
            "table":[[key.hex(),value] for key,value in self.table.items()],
            "global_trials":self.gl_n,
            "global_success":self.gl_success,
        }
        return len(json.dumps(state,sort_keys=True,
                              separators=(",",":")).encode())

def loss(p, y):
    return sum((a-b)**2 for a,b in zip(p,y))/8

def score_by_family(cfg, contexts, mode, family):
    group = "DoorKey" if family == FAMILIES[0] else "Empty"
    training = set(cfg["training_reset_seeds"][group])
    evaluating = set(cfg["evaluation_reset_seeds_previously_consumed"][group])
    if training & evaluating:
        raise ValueError("MR34A_SOURCE_TRAIN_EVAL_SEED_OVERLAP")
    current = FrozenCounts(False)
    history = FrozenCounts(True)
    trained_steps = 0
    # No seed-dependent hyperparameter fitting, no evaluation outcome inputs.
    for (m,f,seed,stream), rows in sorted(contexts.items()):
        if m != mode or f != family or seed not in training:
            continue
        for sample in rows:
            current.learn(sample)
            history.learn(sample)
            trained_steps += 1
    current.seal()
    history.seal()
    by_seed = {}
    for (m,f,seed,stream), rows in sorted(contexts.items()):
        if m != mode or f != family or seed not in evaluating:
            continue
        rec = by_seed.setdefault(seed,{"steps":0,"current":0.0,
                                      "history":0.0,"ablated":0.0})
        for sample in rows:
            y=sample[3]
            rec["steps"] += 1
            rec["current"] += loss(current.forecast(sample),y)
            rec["history"] += loss(history.forecast(sample),y)
            rec["ablated"] += loss(history.forecast(sample,True),y)
    if len(by_seed) != len(evaluating) or trained_steps == 0:
        raise ValueError("MR34A_MISSING_SOURCE_SEED_COHORT")
    sums = {k:sum(v[k] for v in by_seed.values())
            for k in ("steps","current","history","ablated")}
    scored = {
        "trained_native_actions":trained_steps,
        "heldout_consumed_dev_native_actions":sums["steps"],
        "preaction_mean_eightbit_brier":{
            k:sums[k]/sums["steps"]
            for k in ("current","history","ablated")},
        "independent_eval_seed_cluster_count":len(by_seed),
        "independent_seed_clusters_history_beats_current":
            sum(x["history"]<x["current"] for x in by_seed.values()),
        "independent_seed_clusters_history_beats_ablation":
            sum(x["history"]<x["ablated"] for x in by_seed.values()),
        "source_seed_clusters":{
            str(k):{"native_actions":v["steps"],
                    "history_minus_current_brier":
                       (v["history"]-v["current"])/v["steps"],
                    "history_minus_ablated_brier":
                       (v["history"]-v["ablated"])/v["steps"]}
            for k,v in sorted(by_seed.items())
        },
        "frozen_model_cache_entries":{
            "current":len(current.table),"history":len(history.table)},
        "checkpoint_bytes":{
            "current":current.checkpoint_bytes(),
            "history":history.checkpoint_bytes()},
        "same_max_cache_key_capacity":SLOTS,
        "no_heldout_development_training_updates":True,
    }
    return scored

def main(source):
    cfg = protocol()
    start = time.process_time_ns()
    reports={}
    source_rows=[]
    episode_receipts=[]
    with tempfile.TemporaryDirectory(prefix="mr34a-previous-dev-") as folder:
        for mode in MODES:
            rows, ep, receipt = worker(source,mode,folder)
            reports[mode]=receipt
            source_rows.extend(rows)
            episode_receipts.extend(ep)
    if len(episode_receipts)!=96 or any(
        x["original_native_actions"] <= 0 for x in episode_receipts):
        raise ValueError("MR34A_MISSING_ORIGINAL_NATIVE_RECEIPTS")
    original_digest=sha256(json.dumps(
        [[mode,reports[mode]["native_source_history_sha256"]]
         for mode in MODES],sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if original_digest != cfg["source_digest_previous_mr32a"]:
        raise ValueError("MR34A_ORIGINAL_SOURCE_HISTORY_DIGEST_DRIFT")
    contexts=episodes(source_rows)
    results={mode:{
        family:score_by_family(cfg,contexts,mode,family)
        for family in FAMILIES} for mode in MODES}
    door = [results[mode][FAMILIES[0]] for mode in MODES]
    empty = [results[mode][FAMILIES[1]] for mode in MODES]
    candidate_go=(
        all(d["preaction_mean_eightbit_brier"]["history"] <
            d["preaction_mean_eightbit_brier"]["current"] and
            d["independent_seed_clusters_history_beats_current"] >= 3
            for d in door) and
        all(d["preaction_mean_eightbit_brier"]["history"] <=
            d["preaction_mean_eightbit_brier"]["current"]
            for d in empty) and
        all(v["preaction_mean_eightbit_brier"]["history"] <=
            v["preaction_mean_eightbit_brier"]["ablated"]
            for d in (door,empty) for v in d)
    )
    print("MR34A_PUBLIC_HISTORY_INFORMATION="+json.dumps({
        "exact_source_commit":SOURCE_COMMIT,
        "exact_frozen_precode_protocol_sha256":sha256(FILE.read_bytes()).hexdigest(),
        "previous_original_source_event_digest":original_digest,
        "replayed_previously_consumed_original_source_episodes":len(episode_receipts),
        "source_development_frozen_preaction_results":results,
        "precommitted_development_history_signal_go":candidate_go,
        "full_worker_cpu_ns_including_original_source_replay":
            time.process_time_ns()-start,
        "whole_process_peak_rss_bytes_including_native_source":
            peak_os_resident_bytes(),
        "two_source_families_independently_authored":False,
        "protected_scientific_first_use":False,
        "private_source_evaluator_truth_to_predictors":False,
        "native_yggdrasil_learner_modified":False,
        "g29_source_bound_atlas":"BLOCKED",
        "farama_original_external_license_conflict":"UNRESOLVED",
        "scientific_admission":"NO_GO"
    },sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr34a.public_history SOURCE")
    main(sys.argv[1])
