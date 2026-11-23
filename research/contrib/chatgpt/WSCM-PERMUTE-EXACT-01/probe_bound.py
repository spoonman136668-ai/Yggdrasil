"""Source-only exact symbolic action-permutation identification certificate.

No external environment is constructed. The only source-derived primitives are
Darkroom movement (0:row+1, 1:row-1, 2:col+1, 3:col-1, 4:no-op),
9x9 clipping and the five-action permutation in DarkroomPermuted.step().
No hidden permutation is furnished to the candidate policy.
This is a reference control / information bound, NOT a native WSCM learner.
"""
from functools import lru_cache
from itertools import permutations

SIDE = 9
NUM_ACTIONS = 5
PERMS = tuple(permutations(range(NUM_ACTIONS)))
FULL = (1 << len(PERMS)) - 1


def next_position(position, primitive):
    if (type(position) is not tuple or len(position) != 2
        or any(type(z) is not int or not 0 <= z < SIDE for z in position)
        or type(primitive) is not int or not 0 <= primitive < NUM_ACTIONS):
        raise ValueError("INVALID_PUBLIC_STATE_OR_ACTION")
    x, y = position
    if primitive == 0:
        x = min(SIDE - 1, x + 1)
    elif primitive == 1:
        x = max(0, x - 1)
    elif primitive == 2:
        y = min(SIDE - 1, y + 1)
    elif primitive == 3:
        y = max(0, y - 1)
    return x, y


def outcome_masks(position, public_action):
    """Strict validation BEFORE cached partition lookup; bool must not alias int."""
    if type(public_action) is not int or not 0 <= public_action < NUM_ACTIONS:
        raise ValueError("INVALID_ACTION")
    if (type(position) is not tuple or len(position) != 2
        or any(type(z) is not int or not 0 <= z < SIDE for z in position)):
        raise ValueError("INVALID_PUBLIC_STATE")
    return _outcome_masks(position, public_action)


@lru_cache(None)
def _outcome_masks(position, public_action):
    d = {}
    for i, perm in enumerate(PERMS):
        successor = next_position(position, perm[public_action])
        d[successor] = d.get(successor, 0) | (1 << i)
    return tuple(sorted(d.items()))


def branches(mask, position, action):
    return tuple((mask & possible, next_state)
                 for next_state, possible in outcome_masks(position, action)
                 if mask & possible)


@lru_cache(None)
def feasible(mask, position, remaining):
    """Can ALL remaining identities be distinguished in <= remaining steps?"""
    count = mask.bit_count()
    if count <= 1:
        return True
    if remaining <= 0 or count > NUM_ACTIONS ** remaining:
        return False
    for action in range(NUM_ACTIONS):
        parts = branches(mask, position, action)
        if len(parts) == 1 and parts[0] == (mask, position):
            continue  # absolutely no information or motion
        if all(feasible(child, next_state, remaining-1)
               for child, next_state in sorted(parts, key=lambda p: -p[0].bit_count())):
            return True
    return False


POLICY = {}

@lru_cache(None)
def min_total_cost(mask, position, remaining):
    """Minimum total probe count across remaining identities, cap=remaining.

    All possible hidden permutations are equiprobable. Every intervention is
    charged once. None of the hidden indices/roles are passed into the policy;
    the DP uses them only as a truth-space reference comparator.
    """
    count = mask.bit_count()
    if count <= 1:
        return 0
    if remaining <= 0 or count > NUM_ACTIONS ** remaining:
        return None
    best = None
    for action in range(NUM_ACTIONS):
        parts = branches(mask, position, action)
        if len(parts) == 1 and parts[0] == (mask, position):
            continue
        value = count
        for child, next_state in parts:
            cost = min_total_cost(child, next_state, remaining-1)
            if cost is None:
                break
            value += cost
        else:
            if best is None or value < best:
                best = value
                POLICY[(mask, position, remaining)] = action
    return best


def policy_action(mask, position, remaining):
    if min_total_cost(mask, position, remaining) is None:
        return None
    return POLICY.get((mask, position, remaining))


def certificate(start=(0, 0), cap=7):
    min_depth = next((k for k in range(cap + 1) if feasible(FULL, start, k)), None)
    total = min_total_cost(FULL, start, cap)
    return min_depth, total
