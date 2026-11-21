"""KNOW12 strictly synthetic fixture/negative controls; no source first-use."""
from fractions import Fraction
import unittest

from blind_fact_role_dev import (
    SEEDS, PREDICATES, ENTITIES, FIT, canonical, digest,
    synthetic_world, entity_subject, feature_object, public_bit,
    reward, witnessed_fit, fit_native_role, symbolic_role,
    tree_role, blind_control, score_held,
)


class FakeFacts:
    def __init__(self, entries=(), *, mode="engineering_fixture_only"):
        self.entries=set(entries)
        self.mode=mode

    def fact(self,subject,predicate,obj):
        good=(subject,predicate,obj) in self.entries
        return {
            "classification":"DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED"
            if good else "UNKNOWN_ABSTAIN",
            "source_mode":self.mode,
            "witnessed":good,
            "native_accepted":False,
            "verified_new_real_knowledge":False,
            "can_write_causal_consequence":False,
        }


class FakeBasis:
    def __init__(self,memory=None):
        self.memory=dict(memory or {})
    def stage_fit(self,phase,rows,pin,*,max_degree=None):
        if pin != digest(canonical(rows)) or max_degree != 1:
            raise ValueError("SOURCE_OR_DEGREE_INVALID")
        evidence={}
        for context,action,outcome in rows:
            key=(context,action)
            if key in evidence and evidence[key] != outcome:
                raise ValueError("CKAD_NATIVE_STOCHASTIC_OR_CONFLICTING_INPUT_MODEL_INADEQUATE")
            evidence[key]=outcome
        next_memory=dict(self.memory)
        next_memory[phase]=evidence
        return FakeBasis(next_memory)
    def predict(self,phase,mode,action):
        return self.memory[phase].get((mode,action))


def facts_for(seed,seed_index,phase):
    _hidden, _mode, features=synthetic_world(seed,seed_index,phase)
    entries={(entity_subject(seed_index,entity),PREDICATES[feature],
              feature_object(phase,feature,features[feature][entity]))
             for entity in range(ENTITIES)
             for feature in range(len(PREDICATES))}
    return FakeFacts(entries)


class Know12Tests(unittest.TestCase):
    def test_frozen_cohorts_balanced_and_all_nuisance_roles_nonidentifying(self):
        self.assertEqual(SEEDS,(404,505,606))
        for seed_index,seed in enumerate(SEEDS):
            for phase in (0,1):
                correct,truth,features=synthetic_world(seed,seed_index,phase)
                self.assertEqual(correct,(seed_index+phase)%4)
                self.assertEqual(features[correct],truth)
                for segment in (0,1):
                    self.assertEqual(sum(truth[segment*FIT:(segment+1)*FIT]),16)
                    for f in range(4):
                        if f==correct:continue
                        for true_mode in (0,1):
                            values=[features[f][idx]
                                    for idx in range(segment*FIT,(segment+1)*FIT)
                                    if truth[idx]==true_mode]
                            self.assertEqual((len(values),sum(values)),(16,8))

    def test_role_selected_from_witness_rows_not_private_role_argument(self):
        for seed_index,seed in enumerate(SEEDS):
            for phase in (0,1):
                f=facts_for(seed,seed_index,phase)
                observed=witnessed_fit(seed,seed_index,phase)
                native=fit_native_role(f,observed,phase,FakeBasis())
                symbolic=symbolic_role(f,observed,phase)
                tree=tree_role(f,observed,phase)
                self.assertIsNotNone(native)
                self.assertIsNotNone(symbolic)
                self.assertIsNotNone(tree)
                correct=(seed_index+phase)%4
                self.assertEqual((native[0],symbolic[0],tree[0]),(correct,)*3)
                held=score_held(f,seed,seed_index,phase,native,
                                symbolic,tree,blind_control(observed))
                self.assertEqual(held["held_actions"],64)
                for arm in ("native","symbolic","tree"):
                    self.assertEqual(held["brier"][arm],[0,1])
                self.assertEqual(held["brier"]["blind"],[1,4])
                self.assertEqual(held["brier"]["facts_only"],[1,4])

    def test_aliasing_two_candidate_predicates_requires_abstention(self):
        seed,seed_index,phase=SEEDS[0],0,0
        f=facts_for(seed,seed_index,phase)
        correct,truth,features=synthetic_world(seed,seed_index,phase)
        other=(correct+1)%4
        for entity in range(FIT):
            q=entity_subject(seed_index,entity)
            f.entries.remove((q,PREDICATES[other],
                              feature_object(phase,other,features[other][entity])))
            f.entries.add((q,PREDICATES[other],
                           feature_object(phase,other,truth[entity])))
        observed=witnessed_fit(seed,seed_index,phase)
        self.assertIsNone(fit_native_role(f,observed,phase,FakeBasis()))
        self.assertIsNone(symbolic_role(f,observed,phase))
        self.assertIsNone(tree_role(f,observed,phase))

    def test_missing_conflicting_and_wrongly_typed_source_refuse_context(self):
        seed,seed_index,phase=SEEDS[0],0,0
        f=facts_for(seed,seed_index,phase)
        role,truth,features=synthetic_world(seed,seed_index,phase)
        q=entity_subject(seed_index,40)
        expected=features[role][40]
        item=(q,PREDICATES[role],feature_object(phase,role,expected))
        self.assertEqual(public_bit(f,q,phase,role),expected)
        f.entries.remove(item)
        self.assertIsNone(public_bit(f,q,phase,role))
        f.entries.add(item)
        f.entries.add((q,PREDICATES[role],feature_object(phase,role,1-expected)))
        self.assertIsNone(public_bit(f,q,phase,role))
        self.assertIsNone(public_bit(FakeFacts({item},mode="spoofed_real_source"),
                                         q,phase,role))

    def test_forecast_phase_is_not_intervention_identification(self):
        # The two synthetic laws cancel if phase/address is withheld.
        # An equally informed phase-aware exact model achieves 0 Brier;
        # phase-blind probability 0.5 has minimum mean Brier 1/4.
        outcomes=[]
        for mode in (0,1):
            for action in (0,1):
                outcomes += [reward(phase,mode,action) for phase in (0,1)]
        self.assertEqual(sum(outcomes),4)
        self.assertEqual(sum((Fraction(1,2)-y)**2
                             for y in outcomes)/len(outcomes),Fraction(1,4))

    def test_truth_rule_no_boolean_or_invalid_action_leak(self):
        for phase in (0,1):
            for mode in (0,1):
                for action in (0,1):
                    self.assertEqual(reward(phase,mode,action),
                                     int(action==mode) if phase==0 else int(action!=mode))
        for val in (True,2,-1):
            with self.assertRaisesRegex(ValueError,"OUTCOME_DOMAIN"):
                reward(0,0,val)

    def test_published_source_interface_has_no_owner_model_actions(self):
        import blind_fact_role_dev as app
        for unsafe in ("activate","deploy","merge","schedule",
                       "modify_owner","promote_canonical","observe_experience"):
            self.assertFalse(hasattr(app,unsafe))
        self.assertEqual(digest(b"source-only"),
                         __import__("hashlib").sha256(b"source-only").hexdigest())


if __name__=="__main__":
    unittest.main()
