"""Deterministic preregistered CASP-01 development measurement, no source action."""
from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
from capsule_memory_dev import CapsuleMemory, canonical, digest, rule_values

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / 'capsule_dev01_protocol.json'


class ConditionalBeta:
    def __init__(self, contextual):
        self.contextual = contextual
        self.counts = defaultdict(lambda: [0, 0])

    def predict(self, view, action):
        key = (tuple(view) if self.contextual else None, action)
        zeros, ones = self.counts[key]
        return Fraction(1 + ones, 2 + zeros + ones)

    def observe(self, view, action, outcome):
        key = (tuple(view) if self.contextual else None, action)
        self.counts[key][outcome] += 1


class IndependentRuleBayes:
    """Strong control with identical fixed hypothesis family and source budget."""
    def __init__(self):
        self.weights = {}

    def predict(self, view, action):
        w = self.weights.get(tuple(view))
        if w is None:
            return Fraction(1, 2)
        return Fraction(sum(weight * (15 if pred else 1)
                            for weight, pred in zip(w, rule_values(action))), 16 * sum(w))

    def observe(self, view, action, outcome):
        cue = tuple(view)
        old = self.weights.setdefault(cue, [1, 1, 1, 1])
        from math import gcd
        new = [w * (15 if pred == outcome else 1)
               for w, pred in zip(old, rule_values(action))]
        d = gcd(gcd(new[0], new[1]), gcd(new[2], new[3]))
        self.weights[cue] = [w // d for w in new]


def brier(probability, target):
    return (probability - target) ** 2


def labeled_outcome(cue, action):
    return action ^ cue[0] ^ cue[1]


def run_trial(protocol):
    if (protocol['schema'] != 'yggdrasil.amalgam.casp01.frozen-dev-protocol-v1' or
            protocol['parent_sha'] != '86264b41a08d49f558418c0fba367f3a2636befa' or
            protocol['phase_order'] != ['train_A', 'train_B', 'read_A', 'train_C',
                                        'read_A_again', 'held_D']):
        raise ValueError('CASP_PROTOCOL_DRIFT')
    observations = []
    for seed in protocol['seeds']:
        cue = {k: tuple(v) for k, v in protocol['contexts'].items()}
        models = {'capsule': CapsuleMemory(protocol['max_capsules'],
                                           protocol['max_events'], protocol['max_repairs']),
                  'global_beta': ConditionalBeta(False),
                  'context_beta': ConditionalBeta(True),
                  'context_rule_bayes': IndependentRuleBayes()}
        old_pin = None
        old_A = None
        scores = {}
        source_ids = set()
        for phase in protocol['phase_order']:
            if phase.startswith('train_'):
                key = phase[-1]
                c = cue[key]
                for i in range(protocol['training_per_context']):
                    action = (seed + i) & 1
                    outcome = labeled_outcome(c, action)
                    eid = sha256(canonical(['CASP01-FIT', seed, phase, i,
                                            list(c), action, outcome])).hexdigest()
                    if eid in source_ids:
                        raise AssertionError('SOURCE_ID_COLLISION')
                    source_ids.add(eid)
                    for name, model in models.items():
                        if name == 'capsule':
                            model.observe(eid, c, action, outcome)
                        else:
                            model.observe(c, action, outcome)
                if key == 'A':
                    old_pin = digest(models['capsule'].checkpoint())
                    old_A = tuple(models['capsule'].predict(cue['A'], a) for a in (0, 1))
            else:
                key = 'D' if phase == 'held_D' else 'A'
                c = cue[key]
                report = {}
                for name, model in models.items():
                    errors = [brier(model.predict(c, a), labeled_outcome(c, a))
                              for a in (0, 1)
                              for _ in range(protocol['read_each_action'])]
                    report[name] = float(sum(errors, Fraction(0)) / len(errors))
                scores[phase] = report
                if key == 'A':
                    assert tuple(models['capsule'].predict(c, a) for a in (0, 1)) == old_A
        memory = models['capsule']
        checkpoint = memory.checkpoint()
        restored = CapsuleMemory.restore(checkpoint, digest(checkpoint))
        if checkpoint != restored.checkpoint():
            raise AssertionError('COLD_RESTORE_MISMATCH')
        for c in cue.values():
            for action in (0, 1):
                if memory.predict(c, action) != restored.predict(c, action):
                    raise AssertionError('COLD_READOUT_MISMATCH')
        old_retention = brier(old_A[0], labeled_outcome(cue['A'], 0)) / 2 + brier(
            old_A[1], labeled_outcome(cue['A'], 1)) / 2
        return_retention = (brier(memory.predict(cue['A'], 0),
                                   labeled_outcome(cue['A'], 0)) +
                            brier(memory.predict(cue['A'], 1),
                                   labeled_outcome(cue['A'], 1))) / 2
        strong = min(scores['held_D'][n] for n in ('global_beta', 'context_beta',
                                                   'context_rule_bayes'))
        gained = strong - scores['held_D']['capsule']
        observations.append({
            'seed': seed,
            'training_actions': 3 * protocol['training_per_context'],
            'held_queries': 3 * 2 * protocol['read_each_action'],
            'original_A_sha256': old_pin,
            'final_checkpoint_sha256': digest(checkpoint),
            'checkpoint_bytes': len(checkpoint),
            'events': memory.info()['events'],
            'capsules': memory.info()['capsules'],
            'repairs': memory.info()['repairs'],
            'cold_restart_exact': True,
            'A_prediction_exact_retained': old_A == tuple(memory.predict(cue['A'], a) for a in (0, 1)),
            'A_return_delta_brier': float(return_retention - old_retention),
            'scores': scores,
            'D_advantage_vs_strongest': gained,
            'seed_go': (float(return_retention - old_retention) <= float(protocol['retention_max_brier_delta'])
                        and gained >= float(protocol['min_held_advantage_vs_strongest_control']))
        })
    return {'schema': 'yggdrasil.amalgam.casp01.dev-result.v1',
            'protocol_sha256': digest(PROTOCOL.read_bytes()),
            'world': 'source-free synthetic, deterministic, already-known generator',
            'rows': observations,
            'dev_go': all(row['seed_go'] for row in observations),
            'scientific_pass': False, 'owner_accepted': False,
            'protected_source_used': False,
            'note': 'Benchmark demonstrates retention mechanics; held-D novelty is not real-world transfer.'}


if __name__ == '__main__':
    plan = json.loads(PROTOCOL.read_text())
    print(json.dumps(run_trial(plan), indent=2, sort_keys=True))
