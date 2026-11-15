"""FKP-07 original, frozen public DEV experiment.

No independent scientific pass is possible: the exact equal-information Bayesian
reference is a strongest control, and public source parameters are inspectable.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import json
import statistics
import time
import source
import model

PATH = Path(__file__).resolve().parent


def exact_score(pred, truth):
    if pred is None:
        return 0.0
    if len(pred) != len(truth):
        raise ValueError("BAD_HELD_SIZE")
    return sum(int(p==t) for p,t in zip(pred, truth))/len(truth)


def run():
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    frozen = model.fkp06_module()
    laws = frozen.laws()
    public, held = map(tuple, frozen.inputs())
    assert len(laws) == model.N_LAWS and len(public)==128 and len(held)==256
    assert not set(public).intersection(held)
    masks = tuple(frozen.response_mask(x,laws) for x in public)
    held_masks = tuple(frozen.response_mask(x,laws) for x in held)

    histories = []
    for seed in source.HIST_SEEDS:
        actions = source.history_actions(seed)
        w = source.World(seed, "history", actions)
        obs = tuple((action,w.observe(action)) for action in actions)
        assert w.charged == 64
        histories.append((seed,obs))
    histories = tuple(histories)
    foundation_wall = time.perf_counter()-start_wall
    native_counts,hot_pairs,evidence_digest = model.build_historical_prior(histories)
    native_learning_wall = time.perf_counter()-start_wall-foundation_wall

    # Independently re-infer the same historical relationships for the strong control;
    # no true source pair or generator parameter is transmitted.
    conventional_counts,conventional_pairs, conventional_digest = model.build_historical_prior(histories)
    assert conventional_digest == evidence_digest
    assert tuple(hot_pairs)==tuple(conventional_pairs)
    assert len(native_counts)==len(conventional_counts)==496

    learned_mask = model.priority_mask(laws,hot_pairs)
    shuffled_mask = model.priority_mask(laws,model.scrambled_pairs(hot_pairs))
    assert learned_mask.bit_count()==6, "FOUNDATION_NOT_FOUR_DISJOINT_PARENT_PAIRS"
    assert shuffled_mask.bit_count()==6
    prior_masks = {"learned_active":learned_mask,"flat_active":0,
                   "learned_random":learned_mask,"shuffled_active":shuffled_mask}
    rows = []
    contexts = {}
    for seed in source.DEV_SEEDS:
        arms = {}
        worlds = {}
        for name,hot in prior_masks.items():
            w = source.World(seed,"new",public,laws)
            worlds[name] = w
            arms[name] = model.learn_world(w.observe, public,masks,held_masks,hot,
                                         "random" if name=="learned_random" else "active", seed)
            if w.charged!=12:
                raise AssertionError("PAID_BUDGET_MISMATCH")
        # Independent reference fits *exact same transcript* using a distinct
        # conventional scalar hypothesis enumeration, without source internals.
        reference = model.independent_bayes_reference(histories,
                         arms["learned_active"]["transcript"],held,laws)
        assert reference == arms["learned_active"]["prediction"], "STRONG_BAYES_MISMATCH"
        # No evaluator output was queried until all arms and conventional
        # reference had sealed their decisions.
        truth = worlds["learned_active"].held_truth_after_seal(held)
        scores = {name:exact_score(obj["prediction"],truth) for name,obj in arms.items()}
        scores["exact_bayes"] = exact_score(reference,truth)
        contexts[(seed,1)] = arms["learned_active"]
        rows.append({"seed":seed,"accuracy":scores,
                     "remaining":{name:obj["remaining"] for name,obj in arms.items()},
                     "query_indices":{name:list(obj["actions"]) for name,obj in arms.items()},
                     "confidence":{name:obj["confidence"] for name,obj in arms.items()},
                     "hidden_answer_exposed_to_learner":False})
    old_by_context = {(key[0],key[1]):tuple(obj["prediction"])
                      for key,obj in contexts.items()}
    revision_rows = []
    for seed in source.REV_SEEDS:
        world = source.World(seed,"revision",public,laws)
        updated = model.learn_world(world.observe,public,masks,held_masks,
                                    learned_mask,"active",seed)
        assert world.charged==12
        truth = world.held_truth_after_seal(held)
        contexts[(seed-40,2)]=updated
        revision_rows.append({"revision_seed":seed,"new_accuracy":exact_score(updated["prediction"],truth),
                              "original_context":seed-40,"version":2,
                              "remaining":updated["remaining"]})
    assert all(contexts[(key[0],1)]["prediction"]==pred
               for key,pred in old_by_context.items())
    stored,checkpoint_sha,restored = model.checkpoint(contexts,evidence_digest,hot_pairs)
    assert len(restored["versions"])==32
    raw_by_key={(v["context"],v["version"]):v for v in restored["versions"]}
    assert all(raw_by_key[key]["predicted_bits"]=="".join(map(str,pred))
               for key,pred in old_by_context.items())
    assert len(set((v["context"],v["version"]) for v in restored["versions"]))==32

    negatives = []
    for seed in source.NEG_SEEDS:
        world = source.World(seed,"negative",public)
        result = model.learn_world(world.observe,public,masks,held_masks,learned_mask,"active",seed)
        if world.charged != 12:
            raise AssertionError("NEGATIVE_BUDGET_MISMATCH")
        truth=world.held_truth_after_seal(held)
        accuracy=exact_score(result["prediction"],truth)
        negatives.append({"seed":seed,"accuracy":accuracy,"confidence":result["confidence"],
                          "remaining":result["remaining"],
                          "false_confident":result["confidence"]>=.90 and accuracy<.65})
    means={name:statistics.mean(r["accuracy"][name] for r in rows)
           for name in (*prior_masks.keys(),"exact_bayes")}
    diff_flat=[r["accuracy"]["learned_active"]-r["accuracy"]["flat_active"] for r in rows]
    diff_random=[r["accuracy"]["learned_active"]-r["accuracy"]["learned_random"] for r in rows]
    ci_flat=model.paired_ci(diff_flat);ci_random=model.paired_ci(diff_random)
    gain_flat=statistics.mean(diff_flat);gain_random=statistics.mean(diff_random)
    cold_ok = all(raw_by_key[key]["predicted_bits"]=="".join(map(str,p))
                  for key,p in old_by_context.items())
    neg_bad=sum(x["false_confident"] for x in negatives)/len(negatives)
    mechanism_pass=(gain_flat>=.05 and ci_flat[0]>0 and gain_random>=.05 and ci_random[0]>0
                    and means["learned_active"]>=.70 and cold_ok and neg_bad<=.05)
    bayes_tie=means["learned_active"] == means["exact_bayes"]
    return {
        "schema":"fkp07.dev-results.v1",
        "project":"Yggdrasil","research_only":True,
        "result":"MIXED_DEV_NO_NATIVE_INTEGRATION" if mechanism_pass else "DEV_NO_GO",
        "dev_mechanism_gate":mechanism_pass,
        "scientific_pass":False,
        "native_model_changed":False,
        "protected_sources_opened":False,
        "foundation_worlds":len(histories),"original_historical_observations":len(histories)*64,
        "history_sha256":evidence_digest,
        "foundation_pair_candidates":496,"learner_selected_pair_ids":list(hot_pairs),
        "learner_prior_favored_four_law_count":learned_mask.bit_count(),
        "novel_worlds":len(rows),"held_per_world":len(held),"paid_actions_per_arm":12,
        "exact_accuracy":means,"gain_vs_flat":gain_flat,"gain_vs_random":gain_random,
        "ci95_vs_flat":ci_flat,"ci95_vs_random":ci_random,
        "strong_equal_information_bayesian_tie":bayes_tie,
        "old_version_contexts_retained":sum(1 for key in old_by_context
                                           if raw_by_key[key]["predicted_bits"]=="".join(map(str,old_by_context[key]))),
        "original_contexts":len(old_by_context),
        "revision_worlds":len(revision_rows),
        "revision_exact_accuracy":statistics.mean(x["new_accuracy"] for x in revision_rows),
        "checkpoint_bytes":len(stored),"checkpoint_sha256":checkpoint_sha,"cold_restore_exact":cold_ok,
        "outside_family_worlds":len(negatives),"outside_family_false_confident_fraction":neg_bad,
        "whole_dev_wall_seconds":time.perf_counter()-start_wall,
        "whole_dev_cpu_seconds":time.process_time()-start_cpu,
        "history_source_wall_seconds":foundation_wall,
        "native_prior_learning_wall_seconds":native_learning_wall,
        "paired_bootstrap_draws":10000,
        "dev_rows":rows,"revision_rows":revision_rows,"negative_rows":negatives
    }


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
