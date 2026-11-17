"""NCI-ACTIVE-A2: frozen-budget simulated do outcomes; no protected sources.

48 independently authored synthetic worlds; 32 real-class worlds and 16 shifted
family worlds. One explicit fabricated outcome per query, never an original do.
Policies receive only input masks and their actually selected public effects.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from yggdrasil.native_context_basis import NativeContextBasis, canonical, digest, feature_row

HERE = Path(__file__).resolve().parent
IN_SEEDS = tuple(range(100, 132))
SHIFT_SEEDS = tuple(range(200, 216))
BUDGET = 24
INITIAL = 8
HELD = 64
POLICIES = ("active", "random", "passive")
TERMS_DEGREE = 2

def require(condition, reason):
    if not condition:
        raise ValueError("NCI_ACTIVE_A2_" + reason)

def key(label, *parts):
    raw = "nci-active-a2:" + label + ":" + ":".join(str(x) for x in parts)
    return hashlib.sha256(raw.encode("ascii")).digest()

def split_inputs():
    masks = sorted(range(128), key=lambda m: key("held", m))
    held = tuple(sorted(masks[:HELD]))
    pool = tuple(sorted(masks[HELD:], key=lambda m: key("initial", m)))
    initial = pool[:INITIAL]
    available = pool[INITIAL:]
    require(len(set(held)) == 64 and len(set(pool)) == 64
            and len(set(held) & set(pool)) == 0 and len(available) == 56,
            "FROZEN_SPLIT")
    return held, pool, initial, available

def terms_for(seed, shifted=False):
    degree = 3 if shifted else 2
    candidates = [m for m in range(1, 128) if m.bit_count() <= degree]
    # Force an action-sensitive higher-order term; do not expose to policy.
    forced = min((m for m in candidates if (m & 64)
                  and m.bit_count() == degree), key=lambda m: key("forced", seed, m))
    selected = [forced]
    for term in sorted(candidates, key=lambda m: key("coef", seed, m)):
        if term not in selected:
            selected.append(term)
        if len(selected) == 7:
            break
    require(len(selected) == 7 and len(set(selected)) == 7, "SOURCE_TERMS")
    return tuple(selected)

class FabricatedWorld:
    __slots__ = ("seed", "shifted", "_terms", "_held", "_allowed",
                 "_evaluation_unlocked", "effect_calls")
    def __init__(self, seed, shifted, held, pool):
        self.seed = seed
        self.shifted = shifted
        self._terms = terms_for(seed, shifted)
        self._held = frozenset(held)
        self._allowed = frozenset(pool)
        self._evaluation_unlocked = False
        self.effect_calls = 0

    def _consequence(self, mask):
        return sum((mask & term) == term for term in self._terms) & 1

    def observe(self, mask):
        require(type(mask) is int and mask in self._allowed
                and mask not in self._held and not self._evaluation_unlocked,
                "PROTECTED_HELD_OR_LATE_EFFECT")
        self.effect_calls += 1
        return self._consequence(mask)

    def unlock_evaluation(self):
        self._evaluation_unlocked = True

    def held_outcome(self, mask):
        require(self._evaluation_unlocked and type(mask) is int
                and mask in self._held, "HELD_EARLY_ACCESS")
        return self._consequence(mask)

    @property
    def source_sha256(self):
        return digest(canonical({"seed": self.seed, "terms": self._terms,
                                 "shifted": self.shifted}))

def input_row(mask):
    """Input-derived feature support only, no outcome or hidden truth."""
    return feature_row(mask, TERMS_DEGREE)

def rank_add(basis, mask):
    value = input_row(mask)
    while value:
        pivot = value.bit_length() - 1
        if pivot not in basis:
            basis[pivot] = value
            return True
        value ^= basis[pivot]
    return False

def choose_inputs(policy, seed, initial, available):
    """Deterministic policy with NO access to consequence values or world."""
    require(policy in POLICIES, "POLICY")
    require(len(initial) == INITIAL and len(available) == 56, "POOL")
    started = time.perf_counter()
    if policy == "random":
        choice = sorted(available, key=lambda m: key("random", seed, m))[:BUDGET]
    elif policy == "passive":
        natural = sorted((m for m in available if (m >> 6) == (m & 1)),
                         key=lambda m: key("passive", seed, m))
        require(natural, "NATURAL_POLICY_EMPTY")
        choice = [natural[(i + (seed % len(natural))) % len(natural)]
                  for i in range(BUDGET)]
    else:
        order = sorted(available, key=lambda m: key("active", seed, m))
        basis = {}
        for m in initial:
            rank_add(basis, m)
        pending = list(order)
        choice = []
        for _ in range(BUDGET):
            selected = None
            for m in pending:
                # Test input-only support; copied basis does not use outcomes.
                if rank_add(dict(basis), m):
                    selected = m
                    break
            if selected is None:
                selected = pending[0]
            choice.append(selected)
            pending.remove(selected)
            rank_add(basis, selected)
    require(len(choice) == BUDGET
            and all(m in available for m in choice), "SELECTION")
    return tuple(choice), time.perf_counter() - started

def corrupt_labels(seed, masks, outcomes):
    require(len(masks) == len(outcomes), "SHUFFLE")
    unique = sorted(set(masks))
    by_mask = {}
    for m,y in zip(masks,outcomes):
        require(m not in by_mask or by_mask[m] == y, "NATURAL_DUPLICATE_TRUTH")
        by_mask[m] = y
    order = sorted(unique, key=lambda m: key("shuffle", seed, m))
    changed = {dest: by_mask[src] for dest,src in zip(unique,order)}
    return [changed[m] for m in masks]

def independent_predictions(masks, labels):
    """Independent GF(2) elimination, not calling NativeContextBasis."""
    def support(mask):
        row = 1
        sub = mask
        while sub:
            if sub.bit_count() <= 2:
                row |= 1 << sub
            sub = (sub - 1) & mask
        return row
    pivots = {}
    for m,y in zip(masks,labels):
        bits = support(m)
        val = y
        while bits:
            pivot = bits.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = (bits, val)
                break
            old, old_y = pivots[pivot]
            bits ^= old
            val ^= old_y
        else:
            if val:
                return [None] * 128
    answers = []
    for m in range(128):
        bits = support(m)
        value = 0
        while bits:
            pivot = bits.bit_length() - 1
            if pivot not in pivots:
                answers.append(None)
                break
            old, old_y = pivots[pivot]
            bits ^= old
            value ^= old_y
        else:
            answers.append(value)
    return answers

def native_predictions(masks, labels):
    rows = [[m & 63, m >> 6, y] for m,y in zip(masks,labels)]
    try:
        model = NativeContextBasis(6).stage_fit(
            0, rows, digest(canonical(rows)), max_degree=TERMS_DEGREE)
    except ValueError as exc:
        if str(exc) not in ("CKAD_NATIVE_MODEL_CLASS_INADEQUATE",
                            "CKAD_NATIVE_STOCHASTIC_OR_CONFLICTING_INPUT_MODEL_INADEQUATE"):
            raise
        return [None] * 128, None
    predictions = [model.predict(0, m & 63, m >> 6) for m in range(128)]
    raw = model.checkpoint()
    require(NativeContextBasis.restore(raw, digest(raw)).checkpoint() == raw,
            "SOURCE_PIN_COLD")
    return predictions, raw

def cart_predictions(seed, masks, labels):
    from sklearn.tree import DecisionTreeClassifier
    x = [[(m >> b) & 1 for b in range(7)] for m in masks]
    model = DecisionTreeClassifier(criterion="gini", random_state=seed,
                                   max_depth=None, min_samples_leaf=1)
    model.fit(x,labels)
    require(all(int(y) == int(z) for y,z in zip(model.predict(x),labels)),
            "CART_NOT_FULLY_FITTED")
    return [int(v) for v in model.predict(
        [[(m >> b) & 1 for b in range(7)] for m in range(128)])]

def metric(predictions, held, truth):
    values = [predictions[m] for m in held]
    correct = sum(p is not None and p == y for p,y in zip(values,truth))
    wrong = sum(p is not None and p != y for p,y in zip(values,truth))
    abstained = len(values) - correct - wrong
    return {"correct": correct, "wrong": wrong, "abstained": abstained,
            "questions":len(values), "answers_sha256":digest(canonical(values))}

def case(seed, shifted, shuffled, held, pool, initial, available):
    world = FabricatedWorld(seed,shifted,held,pool)
    prepared = {}
    for policy in POLICIES:
        selection, selection_seconds = choose_inputs(policy,seed,initial,available)
        observed = tuple(initial) + selection
        outcomes = [world.observe(m) for m in observed]
        fit_outcomes = corrupt_labels(seed,observed,outcomes) if shuffled else outcomes
        fit_start = time.perf_counter()
        native, checkpoint = native_predictions(observed,fit_outcomes)
        native_fit_seconds = time.perf_counter()-fit_start
        exact = independent_predictions(observed,fit_outcomes)
        require(native == exact, "INDEPENDENT_SYMBOLIC_PARITY")
        cart_start = time.perf_counter()
        cart = cart_predictions(seed,observed,fit_outcomes)
        cart_fit_seconds = time.perf_counter()-cart_start
        native_checkpoint = None if checkpoint is None else {
            "raw_ascii":checkpoint.decode("ascii"),
            "checkpoint_sha256":digest(checkpoint),
            "full_predictions_sha256":digest(canonical(native))}
        prepared[policy] = {"observed":list(observed),
            "observed_outcomes":list(fit_outcomes),
            "raw_outcomes_sha256":digest(canonical(outcomes)),
            "native_predictions":native,
            "independent_predictions":exact,
            "cart_predictions":cart,
            "checkpoint":native_checkpoint,
            "selection_seconds":selection_seconds,
            "fit_native_seconds":native_fit_seconds,
            "fit_cart_seconds":cart_fit_seconds}
    # All policy predictions are frozen before this world yields ANY held truth.
    require(world.effect_calls == len(POLICIES)*(INITIAL+BUDGET),
            "SOURCE_EFFECT_BUDGET")
    world.unlock_evaluation()
    truth = [world.held_outcome(m) for m in held]
    rows = []
    checkpoints = []
    for policy,p in prepared.items():
        native = p["native_predictions"]
        rows.append({"policy":policy, "observations":INITIAL+BUDGET,
            "unique_observed":len(set(p["observed"])),
            "observed_mask_sha256":digest(canonical(p["observed"])),
            "witnessed_inputs":p["observed"], "witnessed_outcomes":p["observed_outcomes"],
            "native":metric(native,held,truth),
            "independent":metric(p["independent_predictions"],held,truth),
            "cart":metric(p["cart_predictions"],held,truth),
            "native_rejected":p["checkpoint"] is None,
            "rank":len(set(p["observed"])),
            "timings":{"selection_seconds":p["selection_seconds"],
                       "native_fit_seconds":p["fit_native_seconds"],
                       "cart_fit_seconds":p["fit_cart_seconds"]}})
        if p["checkpoint"] is not None:
            checkpoints.append({"key":f"{seed}:{int(shifted)}:{int(shuffled)}:{policy}",
                                **p["checkpoint"]})
    return {"seed":seed, "shifted":shifted, "shuffled":shuffled,
            "source_sha256":world.source_sha256,
            "held_input_sha256":digest(canonical(held)),
            "held_truth_sha256":digest(canonical(truth)),
            "synthetic_effect_calls":world.effect_calls, "policies":rows},checkpoints

def bootstrap_lower(deltas):
    require(len(deltas) == 32, "PAIRED_N")
    means = []
    for iteration in range(1000):
        total = 0.0
        for slot in range(32):
            pick = int.from_bytes(key("bootstrap",iteration,slot)[:8],"big") % 32
            total += deltas[pick]
        means.append(total/32)
    return sorted(means)[24]

def calculate(out):
    held,pool,initial,available = split_inputs()
    started = time.perf_counter()
    cases = []
    bundle = []
    for shifted, seeds,shuffled_conditions in (
        (False, IN_SEEDS,(False,True)), (True,SHIFT_SEEDS,(False,))):
        for shuffled in shuffled_conditions:
            for seed in seeds:
                row,checkpoints = case(seed,shifted,shuffled,held,pool,initial,available)
                cases.append(row)
                bundle.extend(checkpoints)
    require(len(cases) == 80 and len(bundle) <= 240, "CASE_COUNTS")
    # Cold process uses ONLY serialized native state, no world generator, source or labels.
    checkpoint_file = out/'native-bundle.json'
    checkpoint_file.write_bytes(canonical({"schema":"nci-active-a2.native-bundle.v1",
        "models":bundle}))
    cold = """
import json,sys
from pathlib import Path
from yggdrasil.native_context_basis import NativeContextBasis,canonical,digest
p=json.loads(Path(sys.argv[1]).read_bytes())
for m in p['models']:
    raw=m['raw_ascii'].encode('ascii')
    assert digest(raw)==m['checkpoint_sha256']
    restored=NativeContextBasis.restore(raw,m['checkpoint_sha256'])
    vec=[restored.predict(0,x&63,x>>6) for x in range(128)]
    assert digest(canonical(vec))==m['full_predictions_sha256']
print('NCI_ACTIVE_A2_COLD_RESTORATION_PASS='+str(len(p['models'])))
"""
    cp=subprocess.run([sys.executable,"-B","-c",cold,str(checkpoint_file)],
        cwd=ROOT,capture_output=True,text=True,check=True,timeout=90,
        env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE="1"))
    require(cp.stdout.strip()==f"NCI_ACTIVE_A2_COLD_RESTORATION_PASS={len(bundle)}",
            "COLD_RESULT")
    def selected(condition):
        return [c for c in cases if condition(c)]
    def total(rows,policy,model,field):
        return sum(next(v for v in c["policies"] if v["policy"]==policy)[model][field]
                   for c in rows)
    families={"IN_FAMILY": selected(lambda c:not c["shifted"] and not c["shuffled"]),
              "SHIFT":selected(lambda c:c["shifted"]),
              "SHUFFLED":selected(lambda c:c["shuffled"])}
    summary = {}
    for name,part in families.items():
        summary[name]={"worlds":len(part),"arms":{
            policy:{"effects":sum(next(v for v in c["policies"] if v["policy"]==policy)["observations"]
                           for c in part),
                    "native":{metric:total(part,policy,"native",metric)
                              for metric in ("correct","wrong","abstained","questions")},
                    "cart":{metric:total(part,policy,"cart",metric)
                            for metric in ("correct","wrong","abstained","questions")}}
            for policy in POLICIES}}
    base=families["IN_FAMILY"]
    deltas=[]
    for row in base:
        arms={p["policy"]:p for p in row["policies"]}
        deltas.append((arms["active"]["native"]["correct"]-
                       arms["random"]["native"]["correct"])/HELD)
    gain=sum(deltas)/len(deltas)
    lower=bootstrap_lower(deltas)
    a=summary["IN_FAMILY"]["arms"]["active"]["native"]
    rng=summary["IN_FAMILY"]["arms"]["random"]["native"]
    gates={"gain_5pp":gain>=0.05,"paired_bootstrap_lower_positive":lower>0,
           "active_coverage_60pct":a["correct"]/a["questions"]>=0.60,
           "active_zero_wrong":a["wrong"]==0,
           "random_zero_wrong":rng["wrong"]==0,
           "effects_equal":all(arm["effects"]==32*len(base)
                               for arm in summary["IN_FAMILY"]["arms"].values()),
           "symbolic_parity":all(
               p["native"]==p["independent"]
               for c in cases for p in c["policies"])}
    return {"schema":"yggdrasil.nci-active-a2.result.v1",
        "classification":"ACTIVE_SOURCEFREE_DEVELOPMENT_SUPPORTED"
          if all(gates.values()) else "ACTIVE_SOURCEFREE_DEVELOPMENT_NO_GO",
        "gates":gates,"scientific_pass":False,"accepted_native":False,
        "original_source_effects":0,"new_original_source_actions":0,
        "original_source_factories":0,"held_label_access_before_prediction":0,
        "supplied_degree":TERMS_DEGREE,"effect_budget_per_arm":INITIAL+BUDGET,
        "held_per_world":HELD,"sourcefree_synthetic_effects":sum(c["synthetic_effect_calls"] for c in cases),
        "cold_models":len(bundle),"paired_gain":gain,"bootstrap_lower_95":lower,
        "summary":summary,"cases":cases,
        "whole_wall_seconds":time.perf_counter()-started}

def strip_timing(v):
    if isinstance(v,dict):
        return {k:strip_timing(x) for k,x in v.items()
                if k not in ("timings","whole_wall_seconds","environment","stable_sha256")}
    if isinstance(v,list):
        return [strip_timing(x) for x in v]
    return v

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--verify-stable")
    opts=parser.parse_args()
    opts.out.mkdir(parents=True,exist_ok=True)
    result=calculate(opts.out)
    result["environment"]={"platform":platform.platform(),"python":platform.python_version()}
    stable=digest(canonical(strip_timing(result)))
    result["stable_sha256"]=stable
    if opts.verify_stable:
        require(stable==opts.verify_stable,"CROSS_PLATFORM_DRIFT")
    (opts.out/"result.json").write_bytes(canonical(result))
    print("NCI_ACTIVE_A2_STABLE_SHA256="+stable,flush=True)
    print("NCI_ACTIVE_A2_SUMMARY="+canonical({
        "classification":result["classification"],"gates":result["gates"],
        "paired_gain":result["paired_gain"],"lower":result["bootstrap_lower_95"],
        "summary":result["summary"],"cold_models":result["cold_models"]}).decode("ascii"),flush=True)
    if os.getenv("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"],"a") as fh:
            fh.write("stable="+stable+"\n")
