"""Read-only exact short-history check for native history-Beta loss of hazard variance.

No source data, simulator calls, native learner mutation or trial sampling.
The Bayesian comparison deliberately assumes the same artificial hidden-site prior
used by CKAD25-AB/AC; it is not an independently discovered physical law.
"""
from fractions import Fraction as F
from itertools import product
import json
from hashlib import sha256

HOT = F(3, 4)
COLD = F(1, 12)
ACTIONS = tuple(range(4))
OBSERVATIONS = tuple(product(ACTIONS, (0, 1)))
NATIVE_SOURCE_GIT_BLOB = '3f33f32c7919bba5297fbf79ff561ef9e85c7255'
NATIVE_CKAD25_AB_HEAD = '791c67f0afee62a3b9de695277c625783b099da5'
CKAD25_AC_HEAD = '0fdf138e02f2058366088025472ab339d3d36ec1'


def likelihood(hidden_hot, action, observed):
    if action not in ACTIONS or observed not in (0, 1) or type(observed) is not int:
        raise ValueError('PUBLIC_WITNESS')
    p = HOT if action == hidden_hot else COLD
    return p if observed else (1 - p)


def posterior(history):
    if type(history) not in (list, tuple):
        raise ValueError('HISTORY')
    mass = [F(1, 4)] * 4
    for action, outcome in history:
        mass = [weight * likelihood(hidden_hot, action, outcome)
                for hidden_hot, weight in zip(ACTIONS, mass)]
    evidence = sum(mass)
    if evidence <= 0:
        raise ValueError('ZERO_EVIDENCE')
    return tuple(x / evidence for x in mass), evidence


def bayes_risk(history):
    weights, _ = posterior(history)
    return tuple(sum(weights[z] * (HOT if z == a else COLD)
                     for z in ACTIONS) for a in ACTIONS)


def native_beta_risk(history):
    # Literal CKAD25-AB native source rule for point-source contradiction y.
    # Native method computes (1 + faults[mask]) / (2 + counts[mask]).
    result = []
    for action in ACTIONS:
        observed = [outcome for a, outcome in history if a == action]
        result.append(F(1 + sum(observed), 2 + len(observed)))
    return tuple(result)


def choose_two(risk):
    return tuple(sorted(ACTIONS, key=lambda a: (-risk[a], a))[:2])


def expected_detection(risk, selected):
    # One anomalous address per *future* world, so two distinct probe hazards sum.
    if len(selected) != 2 or len(set(selected)) != 2:
        raise ValueError('ACTION_BUDGET')
    return sum((risk[x] for x in selected), F(0))


def ratio(value):
    return f'{value.numerator}/{value.denominator}'


def analyse():
    witness = ((2, 0), (2, 1))
    risks = bayes_risk(witness)
    native = native_beta_risk(witness)
    b = choose_two(risks)
    n = choose_two(native)
    advantage = expected_detection(risks, b) - expected_detection(risks, n)
    if (b, n, advantage) != ((2, 0), (0, 1), F(8, 45)):
        raise ValueError('COUNTEREXAMPLE_DRIFT')
    positive = []
    ties = 0
    for history in product(OBSERVATIONS, repeat=2):
        true_risk = bayes_risk(history)
        native_choice = choose_two(native_beta_risk(history))
        bayes_choice = choose_two(true_risk)
        delta = expected_detection(true_risk, bayes_choice) - expected_detection(true_risk, native_choice)
        if delta < 0:
            raise ValueError('BAYES_OPTIMALITY_VIOLATION')
        if delta:
            positive.append({'history': [[a,y] for a,y in history],
                             'expected_detection_gain': ratio(delta),
                             'witness_evidence_probability': ratio(posterior(history)[1])})
        else:
            ties += 1
    first_positive = ((2, 1),)
    assert choose_two(native_beta_risk(first_positive)) == choose_two(bayes_risk(first_positive))
    assert choose_two(native_beta_risk(())) == choose_two(bayes_risk(()))
    return {
        'schema': 'yggdrasil.ckad25.exact_role_evidence_risk_variance.v1',
        'scope': 'source_free_exact_analytic_64_ordered_two_witness_histories_no_new_trial',
        'source_native_blob': NATIVE_SOURCE_GIT_BLOB,
        'source_ckad25_ab': NATIVE_CKAD25_AB_HEAD,
        'source_ckad25_ac': CKAD25_AC_HEAD,
        'prespecified_unchanged_bounded_law': {'latent_role_count':4,'hot':ratio(HOT),'other':ratio(COLD),
            'unknown_role_mapping_prior':'uniform over 24 bijections; same marginal as 4 uniform hot identities'},
        'case_history': [[2,0],[2,1]],
        'case_history_probability': ratio(posterior(witness)[1]),
        'case_posterior_hot_identity': [ratio(v) for v in posterior(witness)[0]],
        'case_native_empirical_risks': [ratio(v) for v in native],
        'case_exact_bayes_predictive_risks': [ratio(v) for v in risks],
        'case_native_selected': list(n), 'case_bayes_selected': list(b),
        'case_native_expected_detection': ratio(expected_detection(risks,n)),
        'case_bayes_expected_detection': ratio(expected_detection(risks,b)),
        'case_conditional_expected_detection_gain': ratio(advantage),
        'length_two_histories_enumerated': len(OBSERVATIONS)**2,
        'length_two_histories_strict_bayes_gain_count': len(positive),
        'length_two_histories_ties_count': ties,
        'strict_gain_examples': positive,
        'scientific_gain_verified':False, 'actual_new_source_actions':0,
        'native_full_runner_test':'NOT_RUN', 'accepted_model_changed':False,
        'note':'Conditional expected next-world detection under a frozen toy hazard model, NOT empirically measured policy gain. Native Beta matches an independent conventional empirical Beta estimator; the Bayes control uses extra supplied prior structure; compare equal-knowledge fully trained controls before any science claim.'
    }

if __name__ == '__main__':
    print(json.dumps(analyse(),sort_keys=True,indent=2))
