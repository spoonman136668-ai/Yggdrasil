"""T14 Ygg source-only generator, no source born at import.
24-bit public node IDs admit 7B single edge (start,end,2-bit code + 4-bit length).
TRAIN and OPEN use different independent ordering regimes and late queries.
"""
import random
TRAIN=tuple(range(-42015,-41999))
OPEN=tuple(range(-42107,-42099))
def birth(seed):
    assert seed in TRAIN or seed in OPEN
    rng=random.Random(142679+abs(seed)*15427)
    seen=set()
    def node():
        while True:
            x=rng.randrange(1024,1<<24)
            if x not in seen:seen.add(x);return x
    paths=[tuple(node() for _ in range(9)) for _ in range(4)]
    core=[[(p[j],j%4,p[j+1]) for j in range(8)] for p in paths]
    noise=[(node(),rng.randrange(4),node()) for _ in range(40)]
    # TRAIN source order and OPEN topology/order shift are independently committed.
    if seed in TRAIN:
        public=[e for lane in core for e in lane]+noise
        rng.shuffle(public)
    else:
        head=[core[lane][idx] for lane in range(4) for idx in (0,2,4,6)]
        rest=[core[lane][idx] for lane in range(4) for idx in (1,3,5,7)]+noise
        rng.shuffle(rest)
        public=head+rest
    queries=tuple({"start":p[0],"ops":tuple((j%4,1) for j in range(8))} for p in paths)
    answers=tuple(p[-1] for p in paths)
    truth_edges=frozenset(e for lane in core for e in lane)
    assert len(public)==72 and len(queries)==4 and len(set(public))==72
    return tuple(public),queries,answers,truth_edges
