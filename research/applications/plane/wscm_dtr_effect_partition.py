"""Retrospective effect-equivalence compression of the pinned, consumed DTR FIT cache.
No simulator, new source access, model mutation or scientific qualification.
"""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = "WSCM-DTR-EFFECT-PARTITION-01"
CACHE = "research/contrib/chatgpt/CKAD-16/source_public_fit.json"
SHA = "016bf254ade33b936386abf7829ff90d765da71105e2beebcb130c95febe7d1d"
PREFIX = "de6e2bb77d8b378d6c776a9b011129b6e4e6298953f1f66379f4f4e84955f571"


def check(ok, msg):
    if not ok:
        raise RuntimeError(msg)


def digest(b):
    return hashlib.sha256(b).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def load():
    raw = (ROOT / CACHE).read_bytes()
    check(digest(raw) == SHA, "SOURCE_SHA_DRIFT")
    for path, blob in ((CACHE, "724dae2143e5f1ce2e2e405b7687ae61ff85b72e"),
                       ("yggdrasil/native_dtr_history.py", "6b9617cf8e0839000783b9d3aa5b60de5ce0a6d0")):
        actual = subprocess.check_output(["git", "hash-object", "--no-filters", path],
                                         cwd=ROOT, text=True).strip()
        check(actual == blob, "GIT_BLOB_DRIFT:" + path)
    d = json.loads(raw)
    check(d["schema"] == "mass.dtr02.fit-public-traces.v1" and len(d["replicas"]) == 3,
          "SOURCE_SCHEMA")
    fit, held, packed = [], [], []
    for replica, part in enumerate(d["replicas"]):
        check(part["index"] == replica and len(part["fit"]) == 256, "REPLICA_SHAPE")
        row_bytes = []
        for i, r in enumerate(part["fit"]):
            check(set(r) == {"seed", "s1", "x1", "s2", "x2", "y"} and
                  r["seed"] == 1100000 + 10000 * replica + i and
                  all(type(r[k]) is int and r[k] in (0, 1) for k in ("s1","x1","s2","x2","y")) and
                  r["x1"] == (i % 4) // 2 and r["x2"] == i % 2, "SOURCE_ROW")
            c = r["s1"] + 2 * r["x1"] + 4 * r["s2"]
            a, y = r["x2"], r["y"]
            if i < 192:
                fit.append((c, a, y, replica))
                row_bytes.append(c + 8 * a + 16 * y)
            else:
                held.append((c, a, y, replica))
        packed.append(bytes(row_bytes).hex())
    check(digest(canonical({"rows_hex": packed, "stop": 192})) == PREFIX, "NATIVE_PREFIX_DRIFT")
    check(len(fit) == 576 and len(held) == 192, "COHORT_DRIFT")
    return fit, held


def norm(groups):
    return tuple(sorted(tuple(sorted(g)) for g in groups))


def partitions(xs):
    if not xs:
        yield ()
    else:
        head, *tail = xs
        for p in partitions(tail):
            yield norm(((head,),) + p)
            for i in range(len(p)):
                yield norm(p[:i] + (p[i] + (head,),) + p[i+1:])


def counts_for(rows):
    counts = [[[0, 0] for _ in range(2)] for _ in range(8)]
    for c, a, y, _ in rows:
        counts[c][a][y] += 1
    return counts


def group_counts(counts, group, action):
    actions = (0, 1) if action is None else (action,)
    return tuple(sum(counts[c][a][y] for c in group for a in actions) for y in (0, 1))


def logbeta(z, o):
    # Exact factorial-based beta integral evaluated in the log domain.
    return math.lgamma(z+1) + math.lgamma(o+1) - math.lgamma(z+o+2)


def evidence(counts, p, uses_action=True):
    return math.fsum(logbeta(*group_counts(counts, g, a))
                     for g in p for a in ((0, 1) if uses_action else (None,)))


def probability(counts, p, uses_action=True):
    out = [[0.0, 0.0] for _ in range(8)]
    for g in p:
        for a in range(2):
            z, o = group_counts(counts, g, a if uses_action else None)
            for c in g:
                out[c][a] = (o+1)/(z+o+2)
    return out


def greedy(counts):
    p = norm((c,) for c in range(8))
    trace = []
    while len(p) > 1:
        old = evidence(counts, p)
        proposals = []
        for i, j in itertools.combinations(range(len(p)), 2):
            nxt = norm(tuple(g for k, g in enumerate(p) if k not in (i,j)) + (p[i]+p[j],))
            proposals.append((evidence(counts, nxt), nxt))
        value, nxt = min(proposals, key=lambda x: (-x[0], x[1]))
        if value <= old + 1e-12:
            break
        trace.append({"groups": len(nxt), "log_evidence_gain": value-old})
        p = nxt
    return p, trace


def mix(counts, models):
    scored = [(evidence(counts, p, a), p, a) for p, a in models]
    top = max(s[0] for s in scored)
    weights = [math.exp(s[0]-top) for s in scored]
    den = math.fsum(weights)
    probs = [probability(counts,p,a) for _,p,a in scored]
    out = [[math.fsum(w*q[c][a] for w,q in zip(weights,probs))/den
            for a in range(2)] for c in range(8)]
    inv_mass = math.fsum(w for w,(_,_,a) in zip(weights,scored) if not a)/den
    return out, inv_mass


def feature_partitions():
    result = []
    for mask in range(8):
        groups = {}
        for c in range(8):
            groups.setdefault(c & mask, []).append(c)
        result.append(norm(groups.values()))
    return result


def brier(prob, rows):
    return math.fsum((prob[c][a]-y)**2 for c,a,y,_ in rows)/len(rows)


def run():
    fit, held = load()
    counts = counts_for(fit)
    ps = tuple(sorted(set(partitions(list(range(8))))))
    check(len(ps) == 4140, "BELL_COUNT")
    p, trace = greedy(counts)
    best = min(ps, key=lambda q: (-evidence(counts,q),q))
    joint, _ = mix(counts, [(q,True) for q in ps])
    subset, invariant_mass = mix(counts, [(q,a) for q in feature_partitions()
                                         for a in (False,True)])
    all_single = norm((c,) for c in range(8))
    all_one = (tuple(range(8)),)
    forecasts = {
        "greedy_effect_partition": probability(counts,p),
        "full_native_style_beta": probability(counts,all_single),
        "action_invariant_full_context": probability(counts,all_single,False),
        "exact_partition_bma": joint,
        "feature_subset_bma": subset,
        "constant_beta": probability(counts,all_one,False),
    }
    score = {name: {"pooled": brier(q,held),
                    "replicas": [brier(q,[r for r in held if r[3]==i]) for i in range(3)]}
             for name,q in forecasts.items()}
    controls = [k for k in score if k != "greedy_effect_partition"]
    candidate = score["greedy_effect_partition"]
    pooled_gap = candidate["pooled"]-min(score[k]["pooled"] for k in controls)
    replica_gaps = [candidate["replicas"][i]-min(score[k]["replicas"][i] for k in controls)
                    for i in range(3)]
    # Reverse context labels. Refit solely on renamed FIT contexts; compare
    # objectives and probabilities after mapping back; ties in optimal
    # partitions are not reported as unique causal classes.
    rename = [7-c for c in range(8)]
    perm_counts = counts_for([(rename[c],a,y,r) for c,a,y,r in fit])
    rp, _ = greedy(perm_counts)
    back = norm(tuple(7-c for c in g) for g in rp)
    relabel_same = p == back
    relabel_evidence = abs(evidence(counts,p)-evidence(counts,back)) < 1e-9
    check(relabel_evidence, "RELABEL_OBJECTIVE_DRIFT")
    check(len(fit)==576 and len(held)==192 and
          all(0<=q[c][a]<=1 for q in forecasts.values() for c in range(8) for a in range(2)),
          "FIT_OR_PROBABILITY_CONTRACT")
    gates = {"at_most_four_groups":len(p)<=4, "pooled_gap_le_0_005":pooled_gap<=.005,
             "replica_gaps_le_0_01":all(x<=.01 for x in replica_gaps)}
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,
            "status":"ARCHIVED_EFFECT_PARTITION_COMPLETE","scientific_pass":False,
            "scientific_gain_verified":False,"source_first_use":False,
            "metrics":{"disposition":"RETROSPECTIVE_COMPRESSION_SIGNAL" if all(gates.values()) else "RETROSPECTIVE_NO_GO",
                       "gates":gates,"fit_episodes":576,"historical_evaluation_episodes":192,
                       "original_source_actions":0,"source_cache_sha256":SHA,
                       "native_prefix_sha256":PREFIX,"exact_partition_count":len(ps),
                       "greedy_partition":p,"exact_map_partition":best,
                       "greedy_log_evidence":evidence(counts,p),
                       "exact_map_log_evidence":evidence(counts,best),
                       "greedy_probability_cells":2*len(p),"full_probability_cells":16,
                       "greedy_merge_trace":trace,"scores":score,"pooled_gap":pooled_gap,
                       "replica_gaps":replica_gaps,"feature_subset_action_invariant_posterior_mass":invariant_mass,
                       "fit_counts_zero_one":counts,"greedy_forecasts":forecasts["greedy_effect_partition"],
                       "full_context_action_posterior_differences":[forecasts["full_native_style_beta"][c][1]-
                                                                  forecasts["full_native_style_beta"][c][0] for c in range(8)],
                       "relabel_partition_same":relabel_same,"relabel_objective_same":relabel_evidence,
                       "held_used_to_fit":False,"new_family_transfer_verified":False,
                       "causal_policy_value_identified":False,"full_final_regression":"NOT_RUN"}}


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    out=Path(args.out)
    result=run()
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(canonical(result)+b"\n")
