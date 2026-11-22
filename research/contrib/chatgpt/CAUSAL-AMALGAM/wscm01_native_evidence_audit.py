"""Read-only WSCM-01 audit of Yggdrasil's native episode evidence surface.

The v5/v6 episode ledger is *engineering_fixture_only* and does not retain
an independently authenticated charged-action / controlled-do proof or a
128-position probe-basis alignment. It MUST NOT be passed to WakeRoleRouter
as a certified causal intervention. No source-world access or learner changes.
"""

from typing import NamedTuple

MAX_LEDGER = 1152  # NativeEpisodeExperience.GROWN_MAX_EPISODES, pinned API review
SOURCE_CLASS = "engineering_fixture_only"


class NativeDevelopmentWitness(NamedTuple):
    identifier: str
    views: tuple
    first_action: int
    next_state: int
    second_action: int
    reward: int
    source_class: str
    charged_do_authenticated: bool
    basis_alignment_authenticated: bool


def _pin(value):
    return type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def _bit(value):
    return type(value) is int and value in (0, 1)


def _validated_event(event):
    if (type(event) is not tuple or len(event) != 6 or not _pin(event[0])
            or type(event[1]) is not tuple or len(event[1]) != 2
            or any(type(v) is not tuple or len(v) != 2
                   or not all(_bit(x) for x in v) for v in event[1])
            or not all(_bit(value) for value in event[2:])):
        raise ValueError('WSCM_NATIVE_LEDGER_CONTRACT')
    return event


def read_native_episode(learner, identifier):
    """Read one witnessed development episode; return a non-promotable record.

    Requires the NativeCumulativeLearner._episode_reader()._ledger shape.
    An untrusted caller cannot turn ledger entries into controlled probes.
    This is offline audit, not O(1) wake retrieval. The readback's integrity
    depends on the upstream checkpoint and episode custody verification.
    """
    if not _pin(identifier):
        raise ValueError('WSCM_NATIVE_IDENTIFIER')
    try:
        ledger = learner._episode_reader()._ledger
    except (AttributeError, TypeError) as exc:
        raise ValueError('WSCM_NATIVE_LEDGER_UNAVAILABLE') from exc
    if type(ledger) is not tuple or len(ledger) > MAX_LEDGER:
        raise ValueError('WSCM_NATIVE_LEDGER_CAPACITY')
    selected = None
    for event in ledger:
        event = _validated_event(event)
        if event[0] == identifier:
            if selected is not None:
                raise ValueError('WSCM_NATIVE_DUPLICATE_IDENTIFIER')
            selected = event
    if selected is None:
        raise ValueError('WSCM_NATIVE_EPISODE_MISSING')
    return NativeDevelopmentWitness(*selected, SOURCE_CLASS, False, False)


def require_qualifying_probe(witness):
    """Real source-first-use gate: current native ledger can never satisfy it."""
    if (not isinstance(witness, NativeDevelopmentWitness)
            or witness.source_class != SOURCE_CLASS
            or witness.charged_do_authenticated is not True
            or witness.basis_alignment_authenticated is not True):
        raise ValueError('WSCM_CHARGED_SOURCE_AUTHORITY_ABSENT')
    # Current native format is explicitly an engineering-only fixture;
    # avoid trusting injected positive fields even from a forged namedtuple.
    raise ValueError('WSCM_CHARGED_SOURCE_AUTHORITY_ABSENT')
