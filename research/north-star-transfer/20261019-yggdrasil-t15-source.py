"""T15 Ygg source-only frozen independent negative-seed namespaces.
TRAIN: four disjoint 6-hop paths. OPEN: unseen braid topology with
shared midpoints. All queries arrive only after a one-pass 72-edge stream.
No source birth at import and no actual OPEN query enters online memory.
"""
import random
TRAIN=tuple(range(-52015,-51999))
OPEN=tuple(range(-52107,-52099))
def birth(seed):
    assert seed in TRAIN or seed in OPEN, "UNREGISTERED_T15_SEED"
    rng=random.Random(201506+abs(seed)*11381)
    used=set()
    def node():
        while True:
            v=rng.randrange(1024,1<<24)
            if v not in used:used.add(v);return v
    paths=[list(node() for _ in range(7)) for _ in range(4)]
    if seed in OPEN:
        # A fresh shared-junction braided grammar not used in TRAIN/T14.
        paths[1][3]=paths[0][3]
        paths[3][3]=paths[2][3]
    core=[[(p[j],j%4,p[j+1]) for j in range(6)] for p in paths]
    distractor=[(node(),rng.randrange(4),node()) for _ in range(48)]
    if seed in TRAIN:
        events=[edge for path in core for edge in path]+distractor
        rng.shuffle(events)
    else:
        prefix=[core[i][j] for i in range(4) for j in (0,2,4)]
        rest=[core[i][j] for i in range(4) for j in (1,3,5)]+distractor
        rng.shuffle(rest);events=prefix+rest
    queries=tuple({"start":p[0],"ops":tuple((j%4,1) for j in range(6))} for p in paths)
    answers=tuple(p[-1] for p in paths)
    assert len(events)==72 and len(set(events))==72 and len(queries)==4
    return tuple(events),queries,answers
