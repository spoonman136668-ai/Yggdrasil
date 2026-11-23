"""Research-only epistemic gate for an unknown Grid5 causal-law family.

Neither a known 120-permutation fixture prior nor a fitted displacement is
source authentication. This observer never provides an actionable forecast.
It does not update native state, change planning, or grant first-use authority.
"""

SCHEMA = "yggdrasil.wscm.epistemic-guard.dev.v1"


def unfamiliar_family_readout(evidence, state, action, *, episode_id):
    """Separate historical evidence and *conditional* predictions from actions.

    `evidence` is the original NativeGrid5Evidence API. Its validators are
    deliberately used directly; invalid states/actions/episode pins fail closed.
    No boolean caller override can assert that an unfamiliar law is certified.
    """
    historical = evidence.public_forecast(state, action, episode_id=episode_id)
    role = evidence.public_role_forecast(state, action, episode_id=episode_id)
    delta = evidence.public_learned_delta_forecast(
        state, action, episode_id=episode_id)
    return {
        "schema": SCHEMA,
        "source_mode": "engineering_fixture_only",
        "status": "ABSTAIN_UNVERIFIED_FAMILY",
        "actionable_next_state": None,
        "action_admissible": False,
        "historical_witness_next_state": historical,
        "role_family_scope": "CONDITIONAL_FIXED_GRID5_120_PERMUTATIONS_DEV",
        "role_family_status": role["status"],
        "role_survivors": role["surviving_permutations"],
        "delta_family_scope": "PROVISIONAL_OBSERVED_INTERIOR_TRANSLATION_DEV",
        "delta_family_status": delta["status"],
        "delta_support": delta["support"],
        "family_authenticated": False,
    }
