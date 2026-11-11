"""WSP-33 preregistered unfamiliar-rule transfer assay; no learner receives rule IDs."""
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "WSP-32"))
from cumulative_model import CumulativeModel, PlasticNand, CONFIGS, context, SOURCE_KNOWN, PUBLIC, HIDDEN, MODES, BUDGETS, route_bits, address
sys.path.insert(0, str(ROOT.parent / "WSP-31"))
from control_baseline import FitCache, RAW, predict, feature_table, OPT_SOURCE
sys.path.insert(0, str(ROOT.parent / "WSP-30"))
from diagnostic import read_verified, validate_trace, RESULT_HASH, MODULE_HASH, truth_table
from routed import Routed

RULES = ("xor", "switch")
TARGETS = (3, 5, 6)

def canon(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":")).encode("ascii")

def target_rule(truth, name):
    if name not in RULES:
        raise ValueError("WSP33_UNKNOWN_RULE")
    if any(len(row) != 8 or any(type(y) is not int or y not in (0, 1) for y in row) for row in truth):
        raise ValueError("WSP33_BAD_SOURCE_TRUTH")
    if name == "xor":
        return tuple(truth[0][i] ^ truth[1][i] for i in range(8))
    return tuple(truth[(i & 1)][i] for i in range(8))

def expressible_in_old_language(truth, target):
    for cfg in CONFIGS:
        first, outer, inject = route_bits(cfg)
        f, o, j = first.index(1), outer.index(1), inject.index(1)
        outputs = []
        for i in range(8):
            x = list(context(i))
            x[j] = truth[f][i]
            outputs.append(truth[o][address(tuple(x))])
        if tuple(outputs) == tuple(target):
            return True
    return False

def symbolic(model, i):
    if model.target_known[i]:
        return model.target_labels[i]
    tables = model.effective_tables()
    first, outer, inject = model.first.index(1), model.outer.index(1), model.inject.index(1)
    x = list(context(i))
    x[inject] = tables[first][i]
    return tables[outer][address(tuple(x))]

def evidence_key(model, upstream):
    return canon([upstream, model.source_known, model.source_labels, model.target_known, model.target_labels])

def run():
    started = time.perf_counter()
    prior = ROOT.parent / "WSP-29"
    old = json.loads(read_verified(prior / "result.json", RESULT_HASH))
    validate_trace(old["traces"])
    modules = json.loads(read_verified(prior / "modules.json", MODULE_HASH))["records"]
    if len(modules) != 120:
        raise AssertionError("WSP33_MODULE_COUNT")
    payloads, source_observations = [], []
    for rec in modules:
        raw = bytes.fromhex(rec["checkpoint_hex"])
        m = Routed.restore(raw)
        if m.snapshot() != raw:
            raise AssertionError("WSP33_UPSTREAM_CUSTODY")
        p = PlasticNand()
        p.rows = m.rows
        payloads.append(p.snapshot())
        source_observations.append(tuple((context(i), (rec["target"] >> j) & 1) for j, i in enumerate(SOURCE_KNOWN)))
    provenance = {
        "wsp32_learner": hashlib.sha256((ROOT.parent / "WSP-32/cumulative_model.py").read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
        "wsp31_controls": hashlib.sha256((ROOT.parent / "WSP-31/control_baseline.py").read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
        "optimizer": OPT_SOURCE
    }
    scores = {a: {k: 0 for k in ("native", "shared_gradient", "full_gradient")} for a in MODES}
    by_rule = {r: {a: 0 for a in MODES} for r in RULES}
    by_pair = {str(i): {a: 0 for a in MODES} for i in range(60)}
    by_expressibility = {str(k).lower(): {a: 0 for a in MODES} for k in (True, False)}
    expressibility_counts = {str(k).lower(): 0 for k in (True, False)}
    counts = {k: 0 for k in ("worlds", "answers", "phase_checks", "old_fact_checks", "acquired_fact_checks", "cold_restores", "replays", "base_checks", "source_locality_checks", "symbolic_checks", "question_invariance_checks", "output_invariance_checks")}
    cache = FitCache()
    questions_seen, outputs_seen = {}, {}
    trace_hash = hashlib.sha256()
    for pair in range(60):
        banks = tuple(payloads[2 * pair: 2 * pair + 2])
        source = tuple(source_observations[2 * pair: 2 * pair + 2])
        upstream = [hashlib.sha256(p).hexdigest() for p in banks]
        for completion in range(16):
            truth = (truth_table(modules[2 * pair]["target"], completion & 3),
                     truth_table(modules[2 * pair + 1]["target"], completion >> 2))
            for rule in RULES:
                target = target_rule(truth, rule)
                expressible = str(expressible_in_old_language(truth, target)).lower()
                expressibility_counts[expressible] += 1
                observed = tuple((context(i), target[i]) for i in PUBLIC)
                row = [pair, completion, rule, expressible]
                for mode in MODES:
                    model = CumulativeModel(banks, source, observed, mode)
                    acquired = []
                    for step in range(BUDGETS[mode] + 1):
                        if step:
                            question = model.query()
                            if question is None or question[0] != "s":
                                raise AssertionError("WSP33_BAD_QUERY")
                            before = model.effective_tables()
                            actual = truth[question[1]][question[2]]
                            model.answer(question, actual)
                            acquired.append((question, actual))
                            counts["answers"] += 1
                            after = model.effective_tables()
                            for b in range(2):
                                for i in range(8):
                                    if (b, i) != (question[1], question[2]) and before[b][i] != after[b][i]:
                                        raise AssertionError("WSP33_NONLOCAL_EDIT")
                                    counts["source_locality_checks"] += 1
                        for b in range(2):
                            for x, y in source[b]:
                                if model._source(b, x) != y:
                                    raise AssertionError("WSP33_OLD_SOURCE_LOST")
                                counts["old_fact_checks"] += 1
                        for x, y in observed:
                            if model.predict(x) != y:
                                raise AssertionError("WSP33_OLD_TARGET_LOST")
                            counts["old_fact_checks"] += 1
                        for q, y in acquired:
                            if model._source(q[1], context(q[2])) != y:
                                raise AssertionError("WSP33_ACQUIRED_FACT_LOST")
                            counts["acquired_fact_checks"] += 1
                        for i in range(8):
                            if symbolic(model, i) != model.predict(context(i)):
                                raise AssertionError("WSP33_NUMERIC_SYMBOLIC_MISMATCH")
                            counts["symbolic_checks"] += 1
                        raw = model.snapshot()
                        cold = CumulativeModel.restore(raw)
                        if cold.snapshot() != raw or cold.payloads() != banks:
                            raise AssertionError("WSP33_COLD_BANK_DRIFT")
                        if tuple(cold.predict(context(i)) for i in range(8)) != tuple(model.predict(context(i)) for i in range(8)):
                            raise AssertionError("WSP33_COLD_PREDICTION_DRIFT")
                        for q, y in acquired:
                            model.answer(q, y)
                            if model.snapshot() != raw:
                                raise AssertionError("WSP33_REPLAY_MUTATION")
                            counts["replays"] += 1
                        counts["cold_restores"] += 1
                        counts["base_checks"] += 1
                        counts["phase_checks"] += 1
                        model = cold
                        if step < BUDGETS[mode]:
                            key = canon([evidence_key(model, upstream).decode(), mode])
                            selected = model.query()
                            if key in questions_seen and questions_seen[key] != selected:
                                raise AssertionError("WSP33_HIDDEN_RULE_TO_QUESTION")
                            questions_seen[key] = selected
                            counts["question_invariance_checks"] += 1
                    if model.query() is not None:
                        raise AssertionError("WSP33_QUERY_BUDGET")
                    native = tuple(model.predict(context(i)) for i in range(8))
                    known = {"upstream": upstream, "source_known": model.source_known,
                             "source_labels": model.source_labels, "target_known": model.target_known,
                             "target_labels": model.target_labels, "provenance": provenance}
                    gradient_tables = []
                    for b in range(2):
                        train = tuple((RAW[i], model.source_labels[b][i]) for i in range(8) if model.source_known[b][i])
                        weights = cache.fit(train, 8, {**known, "representation": "source8hot", "slot": b})
                        gradient_tables.append(tuple(predict(weights, RAW[i]) for i in range(8)))
                    gradients = []
                    for kind, tables in (("shared", model.effective_tables()), ("full", gradient_tables)):
                        features = feature_table(tables)
                        train = tuple((features[i], model.target_labels[i]) for i in range(8) if model.target_known[i])
                        weights = cache.fit(train, 20, {**known, "representation": kind + "20head"})
                        gradients.append(tuple(predict(weights, features[i]) for i in range(8)))
                    same_key = canon(known)
                    out = (native, tuple(gradients))
                    if same_key in outputs_seen and outputs_seen[same_key] != out:
                        raise AssertionError("WSP33_HIDDEN_RULE_TO_OUTPUT")
                    outputs_seen[same_key] = out
                    counts["output_invariance_checks"] += 1
                    for name, outputs in zip(("native", "shared_gradient", "full_gradient"), (native, *gradients)):
                        scores[mode][name] += sum(outputs[i] == target[i] for i in TARGETS)
                    correct = sum(native[i] == target[i] for i in TARGETS)
                    by_rule[rule][mode] += correct
                    by_pair[str(pair)][mode] += correct
                    by_expressibility[expressible][mode] += correct
                    row.append([mode, list(native), [list(v) for v in gradients], hashlib.sha256(model.snapshot()).hexdigest()])
                trace_hash.update(canon(row))
                counts["worlds"] += 1
        print("WSP33_PAIR %d/60" % (pair + 1), file=sys.stderr, flush=True)
    required = (counts["worlds"] == 1920 and counts["answers"] == 9600 and
                counts["phase_checks"] == counts["cold_restores"] == counts["base_checks"] == 17280 and
                counts["old_fact_checks"] == 293760 and counts["acquired_fact_checks"] == counts["replays"] == 13440 and
                counts["source_locality_checks"] == 153600 and counts["symbolic_checks"] == 138240 and
                counts["question_invariance_checks"] == 9600 and counts["output_invariance_checks"] == 7680 and
                cache.logical_fits == 30720 and cache.max_BCE <= .01 and
                sum(expressibility_counts.values()) == 1920)
    gains = {a: scores["source_two"]["native"] - scores[a]["native"]
             for a in ("source_one", "no_query", "source_first_two")}
    controlled = {k: scores["source_two"]["native"] - scores["source_two"][k]
                  for k in ("shared_gradient", "full_gradient")}
    supported = (required and gains["source_one"] >= 58 and gains["no_query"] >= 116 and
                 gains["source_first_two"] >= 0 and all(v >= -57 for v in controlled.values()))
    result = {
        "schema": "wsp33.unfamiliar-rule-transfer.v1",
        "engineering": "PASS" if required else "FAIL",
        "scientific_dev": "DEV_SUPPORTED" if supported else ("SCIENTIFIC_NEGATIVE" if required else "INVALID"),
        "scores_of5760": scores, "gains_native": gains, "gains_vs_yoked_gradient": controlled,
        "by_rule": by_rule, "by_source_pair": by_pair, "by_expressibility": by_expressibility,
        "expressibility_world_counts": expressibility_counts, "counters": counts,
        "gradient_cache": {"logical_fits": cache.logical_fits, "fresh_fits": cache.fresh_fits,
                           "hits": cache.hits, "updates": cache.updates, "max_BCE": cache.max_BCE},
        "target_rule_oracle_correct": 5760,
        "trace_sha256": trace_hash.hexdigest(), "source_hashes": provenance,
        "seconds": time.perf_counter() - started,
        "environment": {"python": sys.version, "platform": platform.platform()},
        "limitations": "Authored out-of-language DEV only, no learner operator discovery; differing priors/cost; no independent science, complete training or deployment."
    }
    print(json.dumps(result, sort_keys=True, indent=2), flush=True)
    if not required:
        raise SystemExit(1)
    return result

if __name__ == "__main__":
    run()
