"""ENERGY-01: synthetic, source-free CRAM-inspired causal-chain development.

Not a CRAM reproduction, not native Yggdrasil integration, not scientific first-use.
Numerical binary variables are not text tokens. The two learned relation weights are
shared by all arms. Recurrent is a propagation proxy, not trained HRM/TRM.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import random
import statistics
import time
import tracemalloc
from collections import deque
from pathlib import Path

SEEDS = (101, 202, 303, 404, 505)
SIZES = (12, 20)
TRAIN_PER_TYPE = 512
TEST_PER_SIZE = 100
MAX_ROUNDS = 64
RESTARTS = 8


def rng(*parts):
    key = ":".join(map(str, parts)).encode("ascii")
    return random.Random(int.from_bytes(hashlib.sha256(key).digest()[:16], "big"))


def fit(seed):
    """Estimate two signed pairwise couplings from intervened parent/child pairs."""
    beginning_wall, beginning_cpu = time.perf_counter_ns(), time.process_time_ns()
    couplings = []
    for edge_type in (0, 1):
        r = rng("train", seed, edge_type)
        observations = []
        for i in range(TRAIN_PER_TYPE):
            # Distinct synthetic do(parent=bit) consequences; no test labels read.
            parent = r.randrange(2)
            child = parent ^ edge_type
            observations.append((parent, child))
        # All observations, rather than a hard-coded sign, determine the weights.
        couplings.append(sum(1 if a == b else -1 for a, b in observations) / len(observations))
    return tuple(couplings), time.perf_counter_ns() - beginning_wall, time.process_time_ns() - beginning_cpu


def make_graph(seed, n, index):
    r = rng("test", seed, n, index)
    edges = []
    truth = [r.randrange(2)]
    for v in range(1, n):
        u = r.randrange(v)
        kind = r.randrange(2)
        edges.append((u, v, kind))
        truth.append(truth[u] ^ kind)
    return tuple(edges), truth[0], tuple(truth)


def parity(coupling):
    if coupling == 0:
        raise ValueError("unidentified edge mechanism")
    return int(coupling < 0)


def graph_layout(n, edges, couplings):
    neighbours = [[] for _ in range(n)]
    for u, v, t in edges:
        p = parity(couplings[t])
        neighbours[u].append((v, p))
        neighbours[v].append((u, p))
    return neighbours


def mismatch(states, neighbours):
    return sum(states[u] ^ states[v] != p for u, contacts in enumerate(neighbours)
               for v, p in contacts if u < v)


def energy_descent(edges, root, couplings, seed, n, index):
    """Coordinate descent on learned signed-pair energy; retain lowest-energy state."""
    neighbours = graph_layout(n, edges, couplings)
    best, best_errors = None, n + 1
    # Work = number of factor comparisons; group into local neighbour checks.
    work = 0
    for repeat in range(RESTARTS):
        r = rng("energy", seed, n, index, repeat)
        state = [root] + [r.randrange(2) for _ in range(n - 1)]
        for sweep in range(MAX_ROUNDS):
            nodes = list(range(1, n))
            r.shuffle(nodes)
            changed = False
            for u in nodes:
                local = neighbours[u]
                # Evaluate whether flipping u strictly lowers the full pairwise energy.
                before = sum(state[u] ^ state[v] != p for v, p in local)
                work += len(local)
                if 2 * before > len(local):
                    state[u] ^= 1
                    changed = True
            errors = mismatch(state, neighbours)
            work += len(edges)
            if errors == 0 or not changed:
                break
        errors = mismatch(state, neighbours)
        work += len(edges)
        if errors < best_errors:
            best, best_errors = tuple(state), errors
        if best_errors == 0:
            break
    assert best is not None and best[0] == root
    return best, work, best_errors


def looped_propagation(edges, root, couplings, n):
    """Fixed-weight iterative relation propagation; not a deep neural model."""
    state = [None] * n
    state[0] = root
    work = 0
    for step in range(MAX_ROUNDS):
        after = list(state)
        for u, v, t in edges:
            p = parity(couplings[t])
            work += 1
            if state[u] is not None and state[v] is None:
                after[v] = state[u] ^ p
            elif state[v] is not None and state[u] is None:
                after[u] = state[v] ^ p
        if after == state:
            break
        state = after
    return tuple(state), work


def exact_propagation(edges, root, couplings, n):
    """Strong exact graph algorithm, with the same learned couplings."""
    neighbours = graph_layout(n, edges, couplings)
    state = [None] * n
    state[0] = root
    queue = deque([0])
    work = 0
    while queue:
        u = queue.popleft()
        for v, p in neighbours[u]:
            work += 1
            if state[v] is None:
                state[v] = state[u] ^ p
                queue.append(v)
    return tuple(state), work


def evaluate():
    tracemalloc.start()
    report = []
    names = ("energy", "looped", "exact", "shuffled_energy")
    for seed in SEEDS:
        couplings, fit_wall, fit_cpu = fit(seed)
        assert couplings == (1.0, -1.0)
        for size in SIZES:
            scores = {a: {"exact": 0, "bits_correct": 0, "wall_ns": 0,
                          "cpu_ns": 0, "work": 0, "verified_energy_zero": 0}
                      for a in names}
            digests = {a: hashlib.sha256() for a in names}
            for index in range(TEST_PER_SIZE):
                edges, root, truth = make_graph(seed, size, index)
                wrong = (-couplings[0], -couplings[1])
                def timed(method, *args):
                    w0, c0 = time.perf_counter_ns(), time.process_time_ns()
                    output = method(*args)
                    return output, time.perf_counter_ns()-w0, time.process_time_ns()-c0
                trials = {
                    "energy": timed(energy_descent, edges, root, couplings, seed, size, index),
                    "looped": timed(looped_propagation, edges, root, couplings, size),
                    "exact": timed(exact_propagation, edges, root, couplings, size),
                    "shuffled_energy": timed(energy_descent, edges, root, wrong, seed, size, index),
                }
                for arm, (raw, wall, cpu) in trials.items():
                    if arm in ("energy", "shuffled_energy"):
                        prediction, work, residual = raw
                        assert residual == mismatch(prediction, graph_layout(size, edges, couplings if arm == "energy" else wrong))
                        if residual == 0:
                            scores[arm]["verified_energy_zero"] += 1
                    else:
                        prediction, work = raw
                    s = scores[arm]
                    s["exact"] += int(prediction == truth)
                    s["bits_correct"] += sum(p == q for p, q in zip(prediction, truth))
                    s["work"] += work
                    s["wall_ns"] += wall
                    s["cpu_ns"] += cpu
                    digests[arm].update(bytes(2 if p is None else p for p in prediction))
            for arm in names:
                s=scores[arm]
                s["graph_exact_accuracy"] = s.pop("exact") / TEST_PER_SIZE
                s["per_bit_accuracy"] = s.pop("bits_correct") / (TEST_PER_SIZE * size)
                s["inference_wall_ms"] = s.pop("wall_ns") / 1e6
                s["inference_cpu_ms"] = s.pop("cpu_ns") / 1e6
                s["whole_wall_ms"] = s["inference_wall_ms"] + fit_wall / 1e6
                s["whole_cpu_ms"] = s["inference_cpu_ms"] + fit_cpu / 1e6
                s["prediction_sha256"] = digests[arm].hexdigest()
            report.append({"seed":seed,"size":size,"train_per_relation":TRAIN_PER_TYPE,
                           "test_graphs":TEST_PER_SIZE,"learned_couplings":couplings,
                           "fit_wall_ms":fit_wall/1e6,"fit_cpu_ms":fit_cpu/1e6,
                           "arms":scores})
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    classifications=[]
    for case in report:
        arms=case["arms"]
        e, l, x=arms["energy"],arms["looped"],arms["exact"]
        classifications.append(e["graph_exact_accuracy"] >= .99 and e["graph_exact_accuracy"] >= l["graph_exact_accuracy"] and e["per_bit_accuracy"] >= l["per_bit_accuracy"] and e["whole_wall_ms"] <= .5*l["whole_wall_ms"] and e["whole_wall_ms"] <= .5*x["whole_wall_ms"])
    grouped={}
    for size in SIZES:
        cases=[row for row in report if row["size"]==size]
        grouped[str(size)]={arm:{"graph_exact_mean": statistics.mean(c["arms"][arm]["graph_exact_accuracy"] for c in cases),
                                 "graph_exact_min": min(c["arms"][arm]["graph_exact_accuracy"] for c in cases),
                                 "median_whole_wall_ms_per_100_graphs": statistics.median(c["arms"][arm]["whole_wall_ms"] for c in cases),
                                 "median_work_per_100_graphs":statistics.median(c["arms"][arm]["work"] for c in cases)}
                           for arm in names}
    return {"schema":"yggdrasil.energy01.source-free-development.v1",
            "classification":"DEVELOPMENT_CANDIDATE_ONLY" if all(classifications) else "DEVELOPMENT_NO_GO",
            "claims":{"native_yggdrasil":False,"cram_reproduction":False,"looped_h_rm_trm_comparison":False,
                       "scientific_first_use":False,"accepted":False,"integration":False},
            "seeds":SEEDS,"sizes":SIZES,"train_per_relation":TRAIN_PER_TYPE,
            "graphs_per_seed_per_size":TEST_PER_SIZE,"max_rounds":MAX_ROUNDS,
            "energy_restarts":RESTARTS,"local_peak_traced_bytes":peak,
            "summary":grouped,"runs":report}


def smoke():
    c,_,_=fit(101)
    edges=((0,1,0),(1,2,1),(2,3,0))
    truth=(1,1,0,0)
    for a in (energy_descent(edges,1,c,101,4,0)[0],looped_propagation(edges,1,c,4)[0],exact_propagation(edges,1,c,4)[0]):
        assert a==truth, (a,truth)
    wrong=energy_descent(edges,1,(-c[0],-c[1]),101,4,0)[0]
    assert wrong!=truth
    assert make_graph(101,12,0)==make_graph(101,12,0)
    return {"smoke":"PASS","learned_couplings":c,"root_anchored":True,"negative_control":True}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--output", type=Path)
    args=p.parse_args()
    result=smoke() if args.smoke else evaluate()
    if args.output:
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result if args.smoke else {"classification":result["classification"],"summary":result["summary"],"peak_bytes":result["local_peak_traced_bytes"]},indent=2))

if __name__=="__main__":
    main()
