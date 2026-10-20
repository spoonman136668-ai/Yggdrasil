"""NCI02-Y: source-free native-cell causal-link retention feasibility.

All causal edge slots and sign composition are supplied by the evaluator.
This is NOT native graph binding, learned composition, regeneration or official
scientific acceptance. No external model, first-use, or network dependency.
"""
import json
import os
from nativecognition.developmental import Colony

MASK = (1 << 32) - 1
SLOTS = (0, 2, 4, 6)


class RNG:
    def __init__(self, seed):
        self.state = (seed + 0x9E3779B9) & MASK

    def next(self):
        x = self.state
        x ^= (x << 13) & MASK
        x ^= x >> 17
        x ^= (x << 5) & MASK
        self.state = x & MASK
        return self.state


def episode(seed):
    rand = RNG(seed)
    signs = tuple(1 if rand.next() & 1 else -1 for _ in range(4))
    events = []
    for _ in range(3):
        for slot, sign in enumerate(signs):
            sample = 0.8 * sign
            if rand.next() % 10 == 0:
                sample = -sample
            events.append((slot, sample))
    return signs, events


def answer(signs, hops):
    p = 1
    for i in range(hops):
        p *= signs[i]
    return p


def signed(x):
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


class LocalOnly(Colony):
    """Equal three-scalar shared genome, but no lateral neighbor feature."""
    def _features(self, index, stimulus):
        own, _, signal = super()._features(index, stimulus)
        return own, own * own, signal


def new_colony(cls, rate, weights=None):
    c = cls(rate)
    if weights is not None:
        c.genome = list(weights)
    return c


def observe(c, events, train):
    for slot, sample in events:
        stimuli = [0.0] * c.CELLS
        stimuli[SLOTS[slot]] = sample
        # Targets are the present observed effect, not a withheld query answer.
        c.step(stimuli, stimuli if train else None)


def train_genome(cls):
    genome = None
    for seed in range(6000, 6032):
        c = new_colony(cls, 0.1, genome)
        _, events = episode(seed)
        observe(c, events, train=True)
        genome = c.genome.copy()
    return genome


def query(c, length):
    p = 1
    for slot in range(length):
        x = signed(c.state[SLOTS[slot]])
        if x == 0:
            return 0
        p *= x
    return p


def run_genome(cls, genome, e, length, erase=False, distract=False):
    c = new_colony(cls, 0.0, genome)
    observe(c, e[1], train=False)
    if erase:
        c.state = [0.0] * c.CELLS
    if distract:
        mixed = 0x80000000 + (e[0][0] + 2) * 97 + (e[0][1] + 2) * 59
        _, events = episode(mixed)
        observe(c, events, train=False)
    prediction = query(c, length)
    return prediction


def run_ema(rate, e, length, distract=False):
    cells = [0.0] * 8
    def inject(events):
        for slot, value in events:
            i = SLOTS[slot]
            cells[i] += rate * (value - cells[i])
    inject(e[1])
    if distract:
        seed = 0x80000000 + (e[0][0] + 2) * 97 + (e[0][1] + 2) * 59
        inject(episode(seed)[1])
    p = 1
    for slot in range(length):
        x = signed(cells[SLOTS[slot]])
        if x == 0:
            return 0
        p *= x
    return p


def select_ema():
    winner, best = 0.05, -1
    for rate in (0.05, 0.1, 0.2):
        score = 0
        for seed in range(6000, 6032):
            e = episode(seed)
            score += int(run_ema(rate, e, 2) == answer(e[0], 2))
        if score > best:
            winner, best = rate, score
    return winner


def score(genome, local_genome, rate, start, hops):
    totals = dict(candidate=0, trained_local_no_lateral=0, trained_ema=0,
                  phenotype_erased=0, after_interference=0)
    for seed in range(start, start + 32):
        e = episode(seed)
        truth = answer(e[0], hops)
        totals["candidate"] += int(run_genome(Colony, genome, e, hops) == truth)
        totals["trained_local_no_lateral"] += int(
            run_genome(LocalOnly, local_genome, e, hops) == truth)
        totals["trained_ema"] += int(run_ema(rate, e, hops) == truth)
        totals["phenotype_erased"] += int(run_genome(
            Colony, genome, e, hops, erase=True) == truth)
        totals["after_interference"] += int(run_genome(
            Colony, genome, e, hops, distract=True) == truth)
    return {k: v / 32 for k, v in totals.items()} | {
        "exact_symbolic_upper_bound": 1.0}


def run():
    genome = train_genome(Colony)
    local_genome = train_genome(LocalOnly)
    alpha = select_ema()
    dev = score(genome, local_genome, alpha, 6100, 2)
    stress = score(genome, local_genome, alpha, 6200, 3)
    gain = stress["candidate"] - stress["trained_ema"]
    lesion_loss = stress["candidate"] - stress["phenotype_erased"]
    interference_drop = stress["candidate"] - stress["after_interference"]
    passed = (gain >= 0.05 and stress["candidate"] >= 0.75
              and lesion_loss >= 0.1 and interference_drop <= 0.1)
    return {
        "schema": "nci02.yggdrasil.sourcefree-development-result.v1",
        "result": "PASS_PROXY_ONLY" if passed else "NEGATIVE",
        "genome_weights_train_only": genome,
        "local_no_lateral_genome_train_only": local_genome,
        "ema_rate_train_selected": alpha,
        "development_two_hop": dev,
        "unseen_three_hop_proxy": stress,
        "gain_vs_trained_ema": gain,
        "phenotype_erasure_loss": lesion_loss,
        "interference_drop": interference_drop,
        "candidate_cell_count": 8, "shared_genome_parameters": 3,
        "symbolic_composition_supplied": True,
        "entity_binding_learned": False, "native_composition_learned": False,
        "phenotype_regeneration_proven": False,
        "scientific_original_firstuse": 0,
        "learned_transfer_accepted": False,
        "train_seed_range": [6000, 6031],
        "development_seed_range": [6100, 6131],
        "stress_seed_range": [6200, 6231],
        "episodes_per_training_arm": 32,
        "observations_per_episode": 12,
        "candidate_cell_updates_per_eval_episode": 96,
    }


if __name__ == "__main__":
    a = run()
    b = run()
    if a != b:
        raise RuntimeError("NONDETERMINISTIC_RESEARCH_RESULT")
    content = json.dumps(a, sort_keys=True, indent=2) + "\n"
    if path := os.environ.get("NCI02_RESULT_PATH"):
        with open(path, "x", encoding="utf-8") as stream:
            stream.write(content)
    print("NCI02_YGGDRASIL_RESULT=" + content)
