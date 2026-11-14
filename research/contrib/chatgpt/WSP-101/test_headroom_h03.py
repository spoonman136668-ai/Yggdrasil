"""H03 preregistered synthetic task-headroom study; no actual weight programming."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import time
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from headroom_h03_world import (
    DEV_IDS, SOURCE_ACTIONS, HELDOUT_ACTIONS, observer, public_source,
    public_passive, scoring_truth_only
)
from headroom_h03_symbolic import (
    GRAMMAR, ExactBayes, predicted, prior_predict, checked_source,
    global_alias_audit, actual_world_query_identifiable
)

FREEZE="078ed40f96ba2458f6bf2265b6fc564900288dd6"


def headroom_audit():
    started=time.perf_counter_ns()
    alias=global_alias_audit()
    source_digest=hashlib.sha256()
    static_correct=bayes_correct=zero_correct=raw_lookup=0
    identifiable=0
    passive_signature=None
    observed_flips=0
    for world in DEV_IDS:
        passive=public_passive(world)
        if passive_signature is None:
            passive_signature=passive
        if passive!=passive_signature:
            raise AssertionError("H03_PASSIVE_DIFFERS_BETWEEN_WORLDS")
        source=checked_source(public_source(world))
        source_digest.update(json.dumps(source,separators=(",",":"),sort_keys=True).encode("ascii"))
        model=ExactBayes(source)
        source_clean=tuple(scoring_truth_only(world,a) for a in SOURCE_ACTIONS)
        held_clean=tuple(scoring_truth_only(world,a) for a in HELDOUT_ACTIONS)
        observed_flips+=sum(y!=clean for (_,y),clean in zip(source,source_clean))
        identifiable+=int(actual_world_query_identifiable(source_clean,held_clean))
        known=set(a for a,_ in source)
        for action,correct in zip(HELDOUT_ACTIONS,held_clean):
            bayes_correct+=model.predict(action)==correct
            static_correct+=prior_predict(action)==correct
            zero_correct+=correct==0
            raw_lookup+=action in known
    nworlds,nqueries=len(DEV_IDS),len(DEV_IDS)*len(HELDOUT_ACTIONS)
    accuracy=bayes_correct/nqueries
    baseline=max(static_correct,zero_correct)/nqueries
    if identifiable<nworlds or alias["divergent_heldout_alias_classes"]>0:
        classification="DEV_SOURCE_UNDERIDENTIFIED"
    elif 0.62<=accuracy<=0.90 and accuracy-baseline>=0.10:
        classification="DEV_NONCEILING_HEADROOM"
    elif accuracy>0.90:
        classification="DEV_SYMBOLIC_CEILING"
    else:
        classification="DEV_CONTROLS_WEAK_OR_NO_SEPARATION"
    return {
        "schema":"yggdrasil.wsp101.h03.dev-headroom.v1",
        "freeze_commit":FREEZE,
        "classification":classification,
        "hypothesis_programs":alias["hypotheses"],
        "source_signature_equivalence_classes":alias["distinct_source_signatures"],
        "source_aliases_with_divergent_heldout":alias["divergent_heldout_alias_classes"],
        "worlds":nworlds,
        "identifiable_worlds":identifiable,
        "active_steps":nworlds*len(SOURCE_ACTIONS)*2,
        "heldout_questions":nqueries,
        "observed_source_flips":observed_flips,
        "symbolic_bayes_correct":bayes_correct,
        "symbolic_bayes_accuracy":accuracy,
        "prior_only_correct":static_correct,
        "fixed_zero_correct":zero_correct,
        "strongest_passive_or_fixed_baseline":max(static_correct,zero_correct),
        "raw_lookup_heldout_coverage":raw_lookup,
        "public_transcripts_sha256":source_digest.hexdigest(),
        "whole_process_wall_ns":time.perf_counter_ns()-started,
        "original_worlds_consumed":False,
        "model_weights_changed":False,
        "weight_programming_executed":False,
        "trained_conventional_baseline_executed":False,
        "scientific_pass":False,
        "important_limitation":"The strong symbolic solver has the correct full grammar and likelihood and is Bayes-optimal under those assumptions; high source identifiability does not establish learned transferable knowledge or superiority over Bayes."
    }


class H03Tests(unittest.TestCase):
    def test_frozen_custody(self):
        self.assertEqual(len(DEV_IDS),16)
        self.assertEqual(len(SOURCE_ACTIONS),22)
        self.assertEqual(len(HELDOUT_ACTIONS),24)
        self.assertFalse(set(SOURCE_ACTIONS)&set(HELDOUT_ACTIONS))
        self.assertEqual(len(GRAMMAR),546)

    def test_source_only_symbolic_separation(self):
        source=(HERE/"headroom_h03_symbolic.py").read_text("utf-8")
        for forbidden in ("from headroom_h03_world", "import headroom_h03_world",
                          "scoring_truth_only", "_secret", "_World"):
            self.assertNotIn(forbidden,source)

    def test_full_grammar_identifiability_without_worlds(self):
        result=global_alias_audit()
        self.assertEqual(result["hypotheses"],546)
        self.assertEqual(result["distinct_source_signatures"],449)
        self.assertEqual(result["divergent_heldout_alias_classes"],0)

    def test_public_and_independent_symbolic_grammar_agree(self):
        # Development negative: divergent equations must fail cross-check.
        from headroom_h03_world import _causal_effect
        for family,mask in GRAMMAR:
            for action in range(1,128):
                self.assertEqual(predicted(family,mask,action),
                                 _causal_effect(family,mask,action))

    def test_passive_has_zero_causal_information(self):
        values=[public_passive(i) for i in DEV_IDS]
        self.assertEqual(len(set(values)),1)
        self.assertEqual(set(values[0]),{(0,0)})

    def test_readout_is_delayed_and_bounded(self):
        endpoint=observer(0)
        self.assertEqual(set(endpoint.__slots__),{"reset","step"})
        self.assertEqual(endpoint.reset(),0)
        self.assertEqual(endpoint.step(SOURCE_ACTIONS[0]),{"observation":0,"reward":0})
        self.assertIn(endpoint.step(0)["observation"],(0,1))
        with self.assertRaises(ValueError):
            endpoint.step(0)

    def test_public_original_ids_unavailable(self):
        for val in (-1,16,101011,101101,101201,101301,True,None):
            with self.subTest(world=val),self.assertRaises(PermissionError):
                observer(val)

    def test_invalid_actions_and_source_tampering_rejected(self):
        o=observer(1)
        for invalid in (-1,128,True,1.0,"7",None):
            with self.subTest(a=invalid),self.assertRaises(ValueError):
                o.step(invalid)
        rows=public_source(1)
        with self.assertRaises(ValueError):
            checked_source(rows[:-1])
        with self.assertRaises(ValueError):
            checked_source(tuple((a,True) for a,_ in rows))
        with self.assertRaises(ValueError):
            checked_source((rows[1],rows[0])+rows[2:])

    def test_replay_determinism(self):
        self.assertEqual(public_source(9),public_source(9))
        self.assertEqual(public_passive(9),public_passive(9))

    def test_exact_bayes_posterior_and_prior(self):
        obj=ExactBayes(public_source(2))
        self.assertEqual(len(obj._weights),546)
        self.assertGreater(obj._normalizer,0)
        for action in HELDOUT_ACTIONS:
            self.assertIn(obj.predict(action),(0,1))
            self.assertIn(prior_predict(action),(0,1))

    def test_all_actual_development_worlds_query_identifiable(self):
        for world in DEV_IDS:
            s=tuple(scoring_truth_only(world,a) for a in SOURCE_ACTIONS)
            h=tuple(scoring_truth_only(world,a) for a in HELDOUT_ACTIONS)
            self.assertTrue(actual_world_query_identifiable(s,h))

    def test_preregistered_dev_classification_no_scientific_success(self):
        r=headroom_audit()
        self.assertIn(r["classification"],(
            "DEV_NONCEILING_HEADROOM","DEV_SYMBOLIC_CEILING",
            "DEV_CONTROLS_WEAK_OR_NO_SEPARATION","DEV_SOURCE_UNDERIDENTIFIED"
        ))
        self.assertFalse(r["scientific_pass"])
        self.assertFalse(r["weight_programming_executed"])
        self.assertFalse(r["original_worlds_consumed"])
        print("WSP101_H03_DEV_RESULT="+json.dumps(r,sort_keys=True,separators=(",",":")),flush=True)


if __name__=="__main__":
    unittest.main()
