"""Gate27 frozen source: explicit causal-rule archive vs independent Bayesian controls.

Research contributor only; no native accepted model changes. All agent updates
receive public (feature vector, applied action, observed binary consequence).
No phase label, parent-pair identity or held outcome is exposed to learners.
"""
from __future__ import annotations
import hashlib
import json
import math

Q = 1000000
HYP = tuple((i, j, bias) for i in range(8) for j in range(i + 1, 8) for bias in (0, 1))
assert len(HYP) == 56
LOG9 = math.log(9)

def mix(*values):
    n = 0x81f53e67
    for i, val in enumerate(values):
        n ^= ((int(val) + 1) * (0x9e3779b1 + i * 0x23c4a9d7)) & 0xffffffff
        n ^= n >> 16
        n = (n * 0x7feb352d) & 0xffffffff
        n ^= n >> 15
        n = (n * 0x846ca68b) & 0xffffffff
        n ^= n >> 16
    return n & 0xffffffff

def permutation(seed):
    v = list(range(256))
    for i in range(255, 0, -1):
        j = mix(seed, i, 8827) % (i + 1)
        v[i], v[j] = v[j], v[i]
    return v

def hidden_world(seed, family, phase):
    a = mix(seed, 321, 1) % 8
    b = (a + 1 + mix(seed, 99, 2) % 7) % 8
    if phase == "B" and family == "shifted_A_B_A":
        aa = (a + 2 + mix(seed, 194, 1) % 5) % 8
        bb = (aa + 1 + mix(seed, 149, 1) % 7) % 8
        if tuple(sorted((a, b))) == tuple(sorted((aa, bb))):
            aa, bb = (a + 3) % 8, (b + 3) % 8
        a, b = aa, bb
    return (a, b, mix(seed, 271, 3 + (phase == "B" and family == "shifted_A_B_A")) & 1)

def preferred(seed, family, phase, x):
    i, j, bias = hidden_world(seed, family, phase)
    return ((x >> i) & 1) ^ ((x >> j) & 1) ^ bias

def reward(seed, family, phase, x, action, trial, domain):
    if family == "pure_noise":
        return mix(seed, x, action, trial, domain, 389) & 1
    want = preferred(seed, family, phase, x)
    draw = mix(seed, x, trial, domain, 7919) % 10
    return int(draw < (9 if action == want else 1))

def training_rows(seed, family, phase):
    offsets = {"A": (0, 96), "B": (96, 64), "R": (160, 64)}
    offset, count = offsets[phase]
    perm = permutation(seed)
    for k in range(count):
        tick = offset + k
        x = perm[mix(seed, tick, 157) % 128]
        action = mix(seed, tick, 204) & 1
        y = reward(seed, family, phase, x, action, tick, 44)
        yield (x, action, y)

def probes(seed, family, phase):
    perm = permutation(seed)
    block = 128 if phase == "B" else 160
    assert phase in ("B", "R")
    for index, x in enumerate(perm[block:block + 32]):
        yield (x, index)

def agrees(h, x, action):
    i, j, bias = h
    choice = ((x >> i) & 1) ^ ((x >> j) & 1) ^ bias
    return action == choice

def scores_add(scores, event):
    x, action, y = event
    for k, h in enumerate(HYP):
        expected = 1 if agrees(h, x, action) else 0
        scores[k] += (1 if y == expected else -1)

def from_rows(rows):
    scores = [0] * len(HYP)
    for event in rows:
        scores_add(scores, event)
    return scores

def posterior(scores):
    maximum = max(scores)
    weights = [math.exp((s - maximum) * LOG9) for s in scores]
    total = sum(weights)
    return [x / total for x in weights]

def forecast(scores, x, action):
    p = posterior(scores)
    yes = sum(weight for k, weight in enumerate(p) if agrees(HYP[k], x, action))
    return 0.1 + 0.8 * yes

def recent_prediction(history, x, action):
    return forecast(from_rows(history[-32:]), x, action) if len(history) >= 8 else 0.5

def normalize_counts(weights):
    total = sum(weights)
    floor = [(w * Q) // total for w in weights]
    left = Q - sum(floor)
    order = sorted(range(len(weights)), key=lambda i: (-(weights[i] * Q) % total, i))
    # Deterministic largest-remainder allocation using exact integer numerators.
    order = sorted(range(len(weights)), key=lambda i: (-(weights[i] * Q - floor[i] * total), i))
    for i in order[:left]:
        floor[i] += 1
    assert sum(floor) == Q
    return floor

def likelihood(h, x, action, y):
    return 9 if y == int(agrees(h, x, action)) else 1

def hazard_predict(q, x, action):
    yes = sum(q[i] for i, h in enumerate(HYP) if agrees(h, x, action))
    return 0.1 + 0.8 * yes / Q

def hazard_update(q, event):
    x, action, y = event
    prior = [63 * count * len(HYP) + Q for count in q]
    return normalize_counts([prior[i] * likelihood(h, x, action, y) for i, h in enumerate(HYP)])

def init(source_rows):
    assert len(source_rows) == 96
    scores = from_rows(source_rows)
    weights = posterior(scores)
    q = normalize_counts([max(1, round(x * Q)) for x in weights])
    return {"schema": 27, "source": scores, "stream": [], "evidence": [],
            "hmm": q, "expert_source_q": 500000, "work": 0, "source_digest": source_digest(scores)}

def source_digest(scores):
    raw = json.dumps(scores, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()

def native_agent_forecast(state, x, action):
    src = forecast(state["source"], x, action)
    history = state["stream"]
    if len(history) < 8:
        return src
    recent = recent_prediction(history, x, action)
    weight = 1 / (1 + math.exp(-max(-12, min(12, sum(state["evidence"]) / 128))))
    return weight * src + (1 - weight) * recent

def forecasts(state, x, action):
    src = forecast(state["source"], x, action)
    recent = recent_prediction(state["stream"], x, action)
    if len(state["stream"]) < 8:
        recent = src
    mix_q = state["expert_source_q"]
    hm = hazard_predict(state["hmm"], x, action)
    all_rows = state["stream"]
    all_score = state["source"].copy()
    for row in all_rows:
        scores_add(all_score, row)
    return {"archive": native_agent_forecast(state, x, action),
            "hazard": hm, "source_recent_bayes": (mix_q * src + (Q - mix_q) * recent) / Q,
            "rolling": recent, "source": src,
            "all_history": forecast(all_score, x, action),
            "no_archive": recent_prediction(state["stream"], x, action),
            "null": 0.5}

def update(state, event):
    x, action, y = event
    src = forecast(state["source"], x, action)
    recent = recent_prediction(state["stream"], x, action)
    if len(state["stream"]) >= 8:
        observed_s = src if y else 1 - src
        observed_r = recent if y else 1 - recent
        ratio = math.log(max(1e-9, observed_s) / max(1e-9, observed_r))
        state["evidence"].append(max(-255, min(255, round(128 * ratio))))
        state["evidence"] = state["evidence"][-16:]
    p_recent = recent if len(state["stream"]) >= 8 else src
    src_lik = src if y else 1 - src
    rec_lik = p_recent if y else 1 - p_recent
    prior_s = (63 * state["expert_source_q"] + (Q - state["expert_source_q"])) // 64
    source_w = prior_s * src_lik
    recent_w = (Q - prior_s) * rec_lik
    state["expert_source_q"] = round(Q * source_w / (source_w + recent_w))
    state["hmm"] = hazard_update(state["hmm"], event)
    state["stream"].append(list(event))
    assert len(state["stream"]) <= 128 and state["source_digest"] == source_digest(state["source"])
    state["work"] += len(HYP) * 3

def archive_weight(state):
    if len(state["stream"]) < 8:
        return 1.0
    return 1 / (1 + math.exp(-max(-12, min(12, sum(state["evidence"]) / 128))))

def canonical_bytes(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()

def pack(state):
    data = canonical_bytes(state)
    envelope = {"payload": state, "sha256": hashlib.sha256(data).hexdigest()}
    result = canonical_bytes(envelope)
    assert len(result) <= 20000
    return result

def unpack(b):
    assert isinstance(b, bytes) and len(b) <= 20000
    obj = json.loads(b)
    data = canonical_bytes(obj["payload"])
    if hashlib.sha256(data).hexdigest() != obj["sha256"]:
        raise ValueError("G27_CHECKPOINT_INTEGRITY_FAIL")
    v = obj["payload"]
    if v["schema"] != 27 or len(v["source"]) != 56 or len(v["hmm"]) != 56:
        raise ValueError("G27_CHECKPOINT_SCHEMA_FAIL")
    if source_digest(v["source"]) != v["source_digest"] or sum(v["hmm"]) != Q:
        raise ValueError("G27_CHECKPOINT_SEMANTIC_FAIL")
    return v
