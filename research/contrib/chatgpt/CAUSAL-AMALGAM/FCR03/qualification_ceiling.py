"""FCR03 stopping certificate: action identifiability and forecast floor.

Read-only on original archived synthetic experiment. No new data, model updates,
policy dispatch, or scientific promotion. The separate positive toy is an algebra
sanity check, not a trial or evidence for an alternative learner.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product
from pathlib import Path
import json

from audit_identifiability import (audit, check_custody, transition_a,
    transition_b, reward_a, reward_b, SOURCE_GIT_BLOBS, TRIAL_RAW_SHA256)
from mechanism_recall import CONFIDENCE_LOW, CONFIDENCE_HIGH

HERE = Path(__file__).resolve().parent


def action_signatures(law_a, law_b, contexts=(0,1), actions=(0,1)):
    """Exact deterministic two-law signatures at visible exogenous contexts."""
    return {str(c): [int(law_a(c,a)!=law_b(c,a)) for a in actions] for c in contexts}


def audit_ceiling():
    original=check_custody()
    original_audit=audit()
    low = Fraction(str(CONFIDENCE_LOW))
    high = Fraction(str(CONFIDENCE_HIGH))
    assert low == Fraction(1,16) and high == Fraction(15,16)
    floor=low*low
    c_transition=Fraction(str(original['means']['mechanism_recall']['C_recombination']['transition']))
    control=Fraction(str(original['matched_best']['C_recombination']['transition']))
    if c_transition != floor or control != floor:
        raise ValueError('FCR03_EXPECTED_CEILING_DRIFT')

    stage_transition = action_signatures(transition_a, transition_b)
    # For reward, s2 and x1 are already observed public data; A/B distinguishability
    # is context alone, invariant across all admissible x1, s2, x2 values.
    stage_reward={str(c): sorted(set(int(reward_a(c,x1,s2,x2)!=reward_b(c,x1,s2,x2))
             for x1,s2,x2 in product((0,1), repeat=3))) for c in (0,1)}
    if stage_transition!={'0':[0,0], '1':[1,1]} or stage_reward!={'0':[0], '1':[1]}:
        raise ValueError('FCR03_ACTION_EQUIVALENCE_DRIFT')

    # Algebraic non-trivial positive control: supplied two-law witness functions
    # where c=0 requires action 1 and c=1 requires action 0 for discrimination.
    # This is intentionally NOT a model, prospective trial, or source use.
    contrast = action_signatures(lambda c,a: 0, lambda c,a: a ^ c)
    if contrast!={'0':[0,1], '1':[1,0]}:
        raise ValueError('FCR03_POSITIVE_CONTRAST_FAILED')
    best_aware=sum(max(v) for v in contrast.values())
    best_fixed=max(sum(contrast[str(c)][i] for c in (0,1)) for i in range(2))
    if not (best_aware==2 and best_fixed==1):
        raise ValueError('FCR03_ACTION_ADVANTAGE_SANITY_FAILED')

    result = {
      'schema':'yggdrasil.fcr03.qualification-ceiling.audit.v1',
      'classification':'SAME_FAMILY_ACTIVE_ACTION_AND_STRICT_TRANSITION_GAIN_STOP',
      'original_trial':'DEV_NO_GO',
      'source_mode':'read_only_existing_source_free_results',
      'new_trials':0,'new_seeds':[], 'scientific_gain_verified':False,
      'confidence_range':[str(low),str(high)],
      'deterministic_transition_brier_lower_bound':str(floor),
      'original_c_candidate_transition_brier':str(c_transition),
      'original_c_best_control_transition_brier':str(control),
      'strict_transition_brier_gain_possible_under_same_clip':False,
      'reward_transition_brier_tie_is_not_full_experiment_success':True,
      'action_distinguishability':{'transition':stage_transition,'reward':stage_reward},
      'same_action_information_per_context':True,
      'positive_control':{'contrast_signatures':contrast,
        'context_aware_information_witnesses':best_aware,
        'best_fixed_information_witnesses':best_fixed,
        'note':'hypothetical algebraic witness only; not tested learning, no scientific gain'},
      'recombined_context_one_count':original_audit['phase_coverage']['C_recombination']['informative_c1'],
      'recombined_context_total_count':original_audit['phase_coverage']['C_recombination']['total'],
      'source_blobs':SOURCE_GIT_BLOBS,
      'original_trial_raw_sha256':TRIAL_RAW_SHA256,
      'required_followup':'A future disjoint source-locked prospective task must have action-dependent expected diagnostic/decision utility, a real native admitted-learning seam, full equally trained conventional baseline and exact cold+resource acceptance. Do not rerun FCR03 same-family action policies.',
      'regression_status':'UNVERIFIED_TWO_OS',
      'native_custody_status':'UNVERIFIED',
      'deployment':'NONE'
    }
    return result


if __name__=='__main__':
    print(json.dumps(audit_ceiling(), sort_keys=True, indent=2))
