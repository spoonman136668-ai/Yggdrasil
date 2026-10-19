"""T16 Yggdrasil independent query-blind causal-memory source grammar.
24-bit true public nodes. TRAIN forward-arrival 6-hop path segments;
OPEN hostile alternating prefix/bridge order with novel shared junctions.
Only scorer sees after-stream answers; no private source truth to inference.
"""
import random
TRAIN=tuple(range(-62023,-61999))
OPEN=tuple(range(-62107,-62099))
def birth(seed):
    assert seed in TRAIN or seed in OPEN,"T16_NOT_PREREGISTERED"
    rng=random.Random(1616409+abs(seed)*10169)
    taken=set()
    def node():
        while True:
            v=rng.randrange(1024,1<<24)
            if v not in taken:taken.add(v);return v
    paths=[list(node() for j in range(7)) for _ in range(4)]
    if seed in OPEN:
        paths[1][2]=paths[0][2]
        paths[3][4]=paths[2][4]
    core=[[(p[j],j%4,p[j+1]) for j in range(6)] for p in paths]
    noise=[(node(),rng.randrange(4),node()) for i in range(48)]
    if seed in TRAIN:
        stream=[e for path in core for e in path]+noise
        rng.shuffle(stream)
    else:
        early=[core[i][j] for i in range(4) for j in (0,2,4)]
        middle=[core[i][j] for i in range(4) for j in (1,3,5)]
        rng.shuffle(middle);rng.shuffle(noise)
        stream=early+middle+noise
    queries=tuple({"start":p[0],"ops":tuple((j%4,1) for j in range(6))} for p in paths)
    answers=tuple(p[-1] for p in paths)
    assert len(stream)==72 and len(set(stream))==72 and len(queries)==4
    return tuple(stream),queries,answers
