"""FKP-07 tokenless numeric causal relationship prior and exact matched controls.

No access to source owner internals; all learning uses public action/consequence tuples.
"""
from __future__ import annotations
from itertools import combinations
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import random
import zlib

N_BITS = 32
N_PAIRS = 496
N_LAWS = 107880
PRIOR_MULTIPLIER = 100000
PAIRS = tuple(combinations(range(N_BITS), 2))
PAIR_INDEX = {p:i for i,p in enumerate(PAIRS)}


def fkp06_module():
    path = Path(__file__).resolve().parents[1] / "FKP-06" / "fkp06.py"
    spec = importlib.util.spec_from_file_location("fkp06_frozen", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_historical_prior(histories):
    """Each of 512 historic worlds contributes exactly one vote, fractionally split."""
    if len(histories) != 512:
        raise ValueError("HISTORY_WORLD_COUNT_MISMATCH")
    counts = [0.0] * N_PAIRS
    evidence_hash = sha256()
    for seed, observations in histories:
        if len(observations) != 64 or len({a for a,_ in observations}) != 64:
            raise ValueError("HISTORICAL_EVIDENCE_COUNT_INVALID")
        evidence_hash.update(seed.to_bytes(4, "little"))
        compatible = []
        for idx,(a,b) in enumerate(PAIRS):
            if all((((action >> a) & 1) & ((action >> b) & 1)) == y
                   for action,y in observations):
                compatible.append(idx)
        if not compatible:
            raise ValueError("FOUNDATION_IMPOSSIBLE_OBSERVATION")
        mass = 1.0 / len(compatible)
        for idx in compatible:
            counts[idx] += mass
        for action,y in observations:
            evidence_hash.update(action.to_bytes(4,"little"))
            evidence_hash.update(bytes([y]))
    selected = tuple(sorted(sorted(range(N_PAIRS), key=lambda i: (-counts[i], i))[:4]))
    return tuple(counts), selected, evidence_hash.hexdigest()


def scrambled_pairs(indices):
    """Negative control: preserve four structural links but permute bit identity."""
    return tuple(sorted(PAIR_INDEX[tuple(sorted(((PAIRS[i][0]+1)%N_BITS,
                                                 (PAIRS[i][1]+1)%N_BITS)))]
                        for i in indices))


def priority_mask(hypotheses, selected_pair_indices):
    preferred = frozenset(PAIRS[i] for i in selected_pair_indices)
    acc = 0
    for i, (a,b,c,d) in enumerate(hypotheses):
        if tuple(sorted((a,b))) in preferred and tuple(sorted((c,d))) in preferred:
            acc |= 1 << i
    return acc


def mass(alive, hot_mask):
    return alive.bit_count() + PRIOR_MULTIPLIER * (alive & hot_mask).bit_count()


def predicted(alive, hot_mask, held_masks):
    total = mass(alive, hot_mask)
    if total == 0:  # Inconsistent with public family: abstain.
        return None, 0.0
    result = []
    confidence = 0.0
    for mask in held_masks:
        ones = mass(alive & mask, hot_mask)
        result.append(int(ones * 2 > total))
        confidence += max(ones, total-ones) / total
    return tuple(result), confidence / len(held_masks)


def learn_world(observe, public, public_masks, held_masks, hot_mask, policy, seed):
    alive = (1 << N_LAWS) - 1
    selected = []
    transcript = []
    rng = random.Random(1000+seed)
    random_order = rng.sample(range(len(public)), 12) if policy == "random" else ()
    for step in range(12):
        if policy == "random":
            idx = random_order[step]
        elif policy == "active" and alive == 0:
            idx = next(j for j in range(len(public)) if j not in selected)
        elif policy == "active":
            total = mass(alive, hot_mask)
            best, idx = -1, -1
            for j, mask in enumerate(public_masks):
                if j in selected:
                    continue
                one = mass(alive & mask, hot_mask)
                balance = min(one, total - one)
                if balance > best:
                    best,idx = balance,j
        else:
            raise ValueError("UNKNOWN_POLICY")
        if idx in selected:
            raise ValueError("REPEATED_INTERVENTION")
        selected.append(idx)
        y = observe(public[idx])
        transcript.append((public[idx], y))
        alive &= (public_masks[idx] if y else ~public_masks[idx])
        # Continue the exact paid budget even if an out-of-family negative
        # eliminates every known hypothesis. Zero posterior means abstention.
    pred,conf = predicted(alive, hot_mask, held_masks)
    return {"alive":alive, "prediction":pred, "confidence":conf,
            "actions":tuple(selected), "transcript":tuple(transcript),
            "remaining":alive.bit_count()}


@lru_cache(maxsize=1)
def independent_reference_fit(histories):
    """Separate conventional source learner: independently reconstruct pair counts."""
    if len(histories) != 512:
        raise ValueError("REFERENCE_HISTORIES_REQUIRED")
    scores = [0.] * len(PAIRS)
    for _, rows in histories:
        possibilities = []
        for i, (left, right) in enumerate(PAIRS):
            errors = 0
            for x, y in rows:
                outcome = ((x >> left) & 1) * ((x >> right) & 1)
                if outcome != y:
                    errors += 1
                    break
            if errors == 0:
                possibilities.append(i)
        if not possibilities:
            raise ValueError("REFERENCE_FOUNDATION_INCONSISTENT")
        for i in possibilities:
            scores[i] += 1 / len(possibilities)
    return tuple(sorted(sorted(range(len(PAIRS)),
                               key=lambda i:(-scores[i], i))[:4]))


def independent_bayes_reference(histories, transcript, held, hypotheses):
    """Independently refit historical counts, enumerate consistent laws, scalar vote.

    This matches the information and has no access to source hidden parameters.
    """
    learned = independent_reference_fit(histories)
    selected = frozenset(PAIRS[i] for i in learned)
    survivors = []
    for law in hypotheses:
        if all((((x >> law[0]) & (x >> law[1]) & 1) ^
                 ((x >> law[2]) & (x >> law[3]) & 1)) == y for x,y in transcript):
            weight = 1 + PRIOR_MULTIPLIER * int(
                tuple(sorted((law[0],law[1]))) in selected and
                tuple(sorted((law[2],law[3]))) in selected)
            survivors.append((law,weight))
    total = sum(weight for _, weight in survivors)
    if total == 0:
        return None
    predictions = []
    for action in held:
        yes = sum(w for (a,b,c,d),w in survivors
                  if (((action >> a) & (action >> b) & 1) ^
                      ((action >> c) & (action >> d) & 1)))
        predictions.append(int(2*yes > total))
    return tuple(predictions)


def checkpoint(contexts, foundation_digest, chosen_pairs):
    state = {"schema":"fkp07.versioned-causal-memory.v1",
             "foundation_sha256":foundation_digest,
             "chosen_pair_ids":list(chosen_pairs),
             "versions":[{"context":context,"version":version,
                          "alive_hex":format(obj["alive"],"x"),
                          "predicted_bits":"".join(str(x) for x in obj["prediction"])}
                         for (context,version), obj in sorted(contexts.items())]}
    serial = json.dumps(state,sort_keys=True,separators=(',',':')).encode("utf-8")
    zipped = zlib.compress(serial,9)
    raw = json.loads(zlib.decompress(zipped).decode("utf-8"))
    if raw != state:
        raise AssertionError("COLD_SNAPSHOT_MISMATCH")
    return zipped, sha256(zipped).hexdigest(), raw


def paired_ci(values):
    n = len(values)
    rng = random.Random(9090)
    samples = sorted(sum(values[rng.randrange(n)] for _ in range(n))/n
                     for _ in range(10000))
    return [samples[249],samples[9749]]
