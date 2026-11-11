"""WSP-34 one-shot preregistered public DEV evaluation on exact WSP-33 cohort."""
import hashlib
import json
import platform
import sys
import time
from pathlib import Path
from operator_layer import OperatorLayer

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "WSP-33"))
import run_dev as frozen
from cumulative_model import CumulativeModel, PlasticNand, context, SOURCE_KNOWN, PUBLIC
from diagnostic import read_verified, validate_trace, RESULT_HASH, MODULE_HASH, truth_table
from routed import Routed

TARGETS = (3, 5, 6)
RULES = ("xor", "switch")
PRIOR = {"xor": 988, "switch": 2196}
EXPECTED_PRIOR = 3184

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")

def learn_layer(model, linear_only=False):
    rows = model.effective_tables()
    # Only real observed target labels are used. Unknown target truth is not passed in.
    observations = (((rows[0][i], rows[1][i], i & 1), model.target_labels[i])
                    for i in PUBLIC)
    return OperatorLayer(observations, linear_only=linear_only)

def predict(model, layer, i):
    if model.target_known[i]:
        return model.target_labels[i]
    rows = model.effective_tables()
    return layer.predict((rows[0][i], rows[1][i], i & 1))

def run():
    start = time.perf_counter()
    prereg = json.loads((ROOT/"prereg.json").read_text(encoding="utf-8"))
    if prereg["exact_parent_sha"] != "d80a5a20714c10bae72e218798edb12dc94000b6":
        raise AssertionError("WSP34_PARENT_DRIFT")
    old = json.loads((ROOT.parent/"WSP-33/result.json").read_text(encoding="utf-8"))
    if old["by_rule"]["xor"]["source_two"] != 988 or old["by_rule"]["switch"]["source_two"] != 2196:
        raise AssertionError("WSP34_OLD_REFERENCE_DRIFT")
    records_root = ROOT.parent/"WSP-29"
    prior_results = json.loads(read_verified(records_root/"result.json", RESULT_HASH))
    validate_trace(prior_results["traces"])
    modules = json.loads(read_verified(records_root/"modules.json", MODULE_HASH))["records"]
    if len(modules) != 120:
        raise AssertionError("WSP34_SOURCE_COUNT")
    payloads, source_observations = [], []
    for rec in modules:
        raw = bytes.fromhex(rec["checkpoint_hex"])
        m = Routed.restore(raw)
        if m.snapshot() != raw:
            raise AssertionError("WSP34_BASE_CUSTODY")
        p = PlasticNand()
        p.rows = m.rows
        payloads.append(p.snapshot())
        source_observations.append(tuple((context(i), (rec["target"] >> j) & 1)
                                         for j, i in enumerate(SOURCE_KNOWN)))
    scores = {key:0 for key in ("new","linear_ablation","old")}
    rule_scores = {rule:{key:0 for key in scores} for rule in RULES}
    diagnostics = {"worlds":0,"actual_source_answers":0,"old_fact_checks":0,
                   "acquired_fact_checks":0,"operator_cold_restores":0,
                   "operator_zero_candidates":0,"eligible_candidates_sum":0,
                   "model_cold_restores":0,"source_banks_checked":0,
                   "negative_contradictions":0,"identity_checks":0}
    witnessed = {}
    trace = hashlib.sha256()
    max_checkpoint = 0
    for pair in range(60):
        banks = tuple(payloads[2*pair:2*pair+2])
        source = tuple(source_observations[2*pair:2*pair+2])
        for completion in range(16):
            truth = (truth_table(modules[2*pair]["target"], completion & 3),
                     truth_table(modules[2*pair+1]["target"], completion >> 2))
            for rule in RULES:
                target = frozen.target_rule(truth, rule)  # evaluator only
                observed = tuple((context(i), target[i]) for i in PUBLIC)
                model = CumulativeModel(banks, source, observed, "source_two")
                acquired = []
                for step in range(2):
                    question = model.query()
                    if question is None or question[0] != "s":
                        raise AssertionError("WSP34_MISSING_SOURCE_QUERY")
                    value = truth[question[1]][question[2]]  # actual selected source answer
                    model.answer(question, value)
                    acquired.append((question, value))
                    raw = model.snapshot()
                    model = CumulativeModel.restore(raw)
                    if model.snapshot() != raw or model.payloads() != banks:
                        raise AssertionError("WSP34_MODEL_COLD_DRIFT")
                    diagnostics["actual_source_answers"] += 1
                    diagnostics["model_cold_restores"] += 1
                if model.query() is not None:
                    raise AssertionError("WSP34_EXTRA_SOURCE_QUERY")
                for bank in range(2):
                    for i in SOURCE_KNOWN:
                        if model._source(bank, context(i)) != truth[bank][i]:
                            raise AssertionError("WSP34_OLD_SOURCE_LOST")
                        diagnostics["old_fact_checks"] += 1
                for i in PUBLIC:
                    if model.predict(context(i)) != target[i]:
                        raise AssertionError("WSP34_OLD_TARGET_LOST")
                    diagnostics["old_fact_checks"] += 1
                for q, v in acquired:
                    if model._source(q[1], context(q[2])) != v:
                        raise AssertionError("WSP34_ACQUIRED_SOURCE_LOST")
                    diagnostics["acquired_fact_checks"] += 1
                if model.payloads() != banks:
                    raise AssertionError("WSP34_BASE_CHANGED")
                diagnostics["source_banks_checked"] += 1
                layer, linear = learn_layer(model), learn_layer(model, linear_only=True)
                original = layer.snapshot()
                fresh = OperatorLayer.restore(original)
                if fresh.snapshot() != original:
                    raise AssertionError("WSP34_OPERATOR_COLD_DRIFT")
                diagnostics["operator_cold_restores"] += 1
                max_checkpoint = max(max_checkpoint, len(original))
                if tuple(predict(model, layer, i) for i in PUBLIC) != tuple(target[i] for i in PUBLIC):
                    raise AssertionError("WSP34_TARGET_RETENTION")
                if len(layer.observations) != len(PUBLIC):
                    raise AssertionError("WSP34_MISSING_KNOWN_FACT")
                survivors = sum(layer.eligible)
                diagnostics["eligible_candidates_sum"] += survivors
                diagnostics["operator_zero_candidates"] += int(survivors == 0)
                # Exact equal-evidence inputs must not encode hidden rule names.
                key = canonical([model.snapshot().hex(), layer.observations])
                predicted = tuple(predict(model, fresh, i) for i in TARGETS)
                if key in witnessed and witnessed[key] != predicted:
                    raise AssertionError("WSP34_HIDDEN_RULE_CONTAMINATION")
                witnessed[key] = predicted
                diagnostics["identity_checks"] += 1
                base = tuple(model.predict(context(i)) for i in TARGETS)
                ablate = tuple(predict(model, linear, i) for i in TARGETS)
                for name, values in (("new",predicted),("linear_ablation",ablate),("old",base)):
                    points = sum(values[j] == target[i] for j, i in enumerate(TARGETS))
                    scores[name] += points
                    rule_scores[rule][name] += points
                trace.update(canonical([pair,completion,rule,model.snapshot().hex(),
                                        original.hex(),predicted,base,ablate]))
                diagnostics["worlds"] += 1
        print("WSP34_PAIR %d/60"%(pair+1), file=sys.stderr,flush=True)
    exact = diagnostics["worlds"] == 1920 and diagnostics["actual_source_answers"] == 3840
    exact = exact and diagnostics["old_fact_checks"] == 32640 and diagnostics["acquired_fact_checks"] == 3840
    exact = exact and diagnostics["operator_cold_restores"] == diagnostics["source_banks_checked"] == 1920
    exact = exact and scores["old"] == EXPECTED_PRIOR
    exact = exact and all(rule_scores[r]["old"] == PRIOR[r] for r in RULES)
    delta = scores["new"] - EXPECTED_PRIOR
    no_rule_regression = all(rule_scores[r]["new"] >= PRIOR[r] for r in RULES)
    if not exact:
        classification = "INVALID"
    elif delta >= 58 and no_rule_regression:
        classification = "DEV_SUPPORTED"
    elif delta > 0:
        classification = "MIXED"
    else:
        classification = "SCIENTIFIC_NEGATIVE"
    result = {
        "schema":"wsp34.operator-construction-dev.v1",
        "engineering":"PASS" if exact else "FAIL",
        "classification":classification,
        "scores_of5760":scores,
        "scores_by_rule_of2880":rule_scores,
        "gain_over_wsp33":delta,
        "strong_frozen_trained_controls":{"shared":3508,"full_source_head":3636},
        "beat_strong_control":scores["new"] >= 3636,
        "stats":diagnostics,
        "operator_static_coefficient_bits":2048,
        "operator_plastic_eligibility_bits":256,
        "max_operator_checkpoint_bytes":max_checkpoint,
        "trace_sha256":trace.hexdigest(),
        "seconds":time.perf_counter()-start,
        "environment":{"python":sys.version,"platform":platform.platform()},
        "limitations":"Preauthored 256 candidate polynomial circuits, original pretrained WSP29 source modules, WSP32 fact memory and Python simulator remain. No wholly programmed intelligence, independent science, or matched all-in cost."
    }
    print(json.dumps(result,sort_keys=True,indent=2))
    if not exact:
        raise SystemExit(1)
    return result

if __name__ == "__main__":
    run()
