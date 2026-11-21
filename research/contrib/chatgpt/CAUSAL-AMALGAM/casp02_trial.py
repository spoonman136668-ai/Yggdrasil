"""Execute CASP-02 frozen compositional fixture with strongest conventional controls."""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from time import perf_counter_ns
from math import gcd
import json

from capsule_memory_dev import CapsuleMemory, canonical, digest
from capsule_dev01_trial import ConditionalBeta, brier
from casp02_compositional import CompositionalCapsules, affine_outcome

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / 'casp02_protocol.json'


class ExactAffineGF2:
    """Conventional exact affine solver with abstention if public evidence ambiguous."""
    def __init__(self):
        self.rows = []

    def observe(self, cue, action, outcome):
        row = 1 | (action << 1) | (cue[0] << 2) | (cue[1] << 3)
        self.rows.append((row, outcome))

    def predict(self, cue, action):
        # Enumerate the full 16-rule hypothesis class and discard inconsistent
        # rules. This is exact GF2 feasibility, not oracle law access.
        consistent = [rule for rule in range(16)
                      if all(affine_outcome(rule, ((row >> 2) & 1, (row >> 3) & 1),
                                                (row >> 1) & 1) == y
                             for row, y in self.rows)]
        if not consistent:
            return Fraction(1, 2)
        return Fraction(sum(affine_outcome(rule, cue, action) for rule in consistent),
                        len(consistent))


class ExactAffineBayes:
    def __init__(self):
        self.weights = [1] * 16

    def observe(self, cue, action, outcome):
        ws = [w * (15 if affine_outcome(i, cue, action) == outcome else 1)
              for i, w in enumerate(self.weights)]
        g = 0
        for w in ws:
            g = gcd(g, w)
        self.weights = [w // g for w in ws]

    def predict(self, cue, action):
        numerator = sum(w * (15 if affine_outcome(i, cue, action) else 1)
                        for i, w in enumerate(self.weights))
        return Fraction(numerator, 16 * sum(self.weights))


def law(cue, action):
    return action ^ cue[0] ^ cue[1]


def check_plan(plan):
    if (plan['schema'] != 'yggdrasil.amalgam.casp02.frozen-dev-protocol.v1' or
            plan['parent_sha'] != '95637e3c0614327ac672bb480dfb88493bb99fc0' or
            plan['fit_context_order'] != ['A', 'B', 'C'] or
            plan['contexts'] != {'A': [0, 0], 'B': [1, 0], 'C': [0, 1], 'D': [1, 1]} or
            plan['training_events_per_context'] != 16 or
            plan['seeds'] != [101, 211, 307]):
        raise ValueError('CASP02_FROZEN_PROTOCOL_DRIFT')


def score(model, cue, fn, n):
    return float(sum((brier(model.predict(cue, a), fn(cue, a))
                      for a in (0, 1) for _ in range(n)), Fraction(0)) / (2 * n))


def run(plan):
    check_plan(plan)
    rows = []
    for seed in plan['seeds']:
        contexts = {k: tuple(v) for k, v in plan['contexts'].items()}
        systems = {'capsule01': CapsuleMemory(), 'capsule02': CompositionalCapsules(),
                   'context_beta': ConditionalBeta(True), 'global_beta': ConditionalBeta(False),
                   'exact_gf2': ExactAffineGF2(), 'exact_bayes16': ExactAffineBayes()}
        original_A = None
        before = None
        ids = []
        begin = perf_counter_ns()
        for key in plan['fit_context_order']:
            cue = contexts[key]
            for i in range(plan['training_events_per_context']):
                action = (seed + i) % 2
                outcome = law(cue, action)
                eid = sha256(canonical(['CASP02', seed, key, i, cue, action, outcome])).hexdigest()
                ids.append(eid)
                systems['capsule01'].observe(eid, cue, action, outcome)
                systems['capsule02'].observe(eid, cue, action, outcome)
                for name in ('context_beta', 'global_beta', 'exact_gf2', 'exact_bayes16'):
                    systems[name].observe(cue, action, outcome)
            if key == 'A':
                original_A = tuple(systems['capsule02'].predict(cue, a) for a in (0, 1))
                before = score(systems['capsule02'], cue, law, plan['held_queries_per_action'])
        fit_ns = perf_counter_ns() - begin
        assert len(ids) == len(set(ids)) == plan['max_fit_events']
        reference = systems['capsule02']
        saved = reference.checkpoint()
        cold = CompositionalCapsules.restore(saved, digest(saved))
        assert cold.checkpoint() == saved
        for cue in contexts.values():
            for action in (0, 1):
                assert cold.predict(cue, action) == reference.predict(cue, action)
        assert tuple(reference.predict(contexts['A'], a) for a in (0, 1)) == original_A
        retained = score(reference, contexts['A'], law, plan['held_queries_per_action'])
        same = {name: score(model, contexts['D'], law, plan['held_queries_per_action'])
                for name, model in systems.items()}
        adversarial = {name: score(model, contexts['D'], lambda cue, action: 0,
                                   plan['held_queries_per_action'])
                       for name, model in systems.items()}
        strongest = min(same[name] for name in ('context_beta', 'global_beta',
                                               'exact_gf2', 'exact_bayes16'))
        advantage = strongest - same['capsule02']
        begin = perf_counter_ns()
        for i in range(1000):
            reference.predict(contexts['D'], i & 1)
        inference_ns = perf_counter_ns() - begin
        rows.append({'seed': seed, 'fit_events': len(ids), 'retention_delta_brier': retained - before,
                     'old_A_predictions_identical': True, 'checkpoint_sha256': digest(saved),
                     'checkpoint_bytes': len(saved), 'cold_checkpoint_exact': True,
                     'brier_same_mechanism_held_D': same,
                     'brier_unannounced_changed_mechanism_held_D': adversarial,
                     'advantage_vs_best_equal_information_control': advantage,
                     'fit_process_ns_uncontrolled': fit_ns,
                     '1000_held_inference_process_ns_uncontrolled': inference_ns,
                     'go': (retained - before <= float(plan['retention_max_brier_delta']) and
                            advantage >= float(plan['minimum_held_Brier_gain_vs_strongest']))})
    return {'schema': 'yggdrasil.amalgam.casp02.result.v1',
            'protocol_sha256': digest(PROTOCOL.read_bytes()), 'rows': rows,
            'dev_go': all(row['go'] for row in rows), 'scientific_pass': False,
            'source_first_use': False, 'owner_accepted': False,
            'summary': 'A/B/C trained, never D, public cue only. Disclosed GF2 prior, known family, synthetic only.'}


if __name__ == '__main__':
    print(json.dumps(run(json.loads(PROTOCOL.read_bytes())), sort_keys=True, indent=2))
