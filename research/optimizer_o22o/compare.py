"""O22-O original source two-process FIT-only science receipt reconciliation.

Never treats future own-policy return as a counterfactual causal intervention.
"""
import hashlib
import json
import sys
from pathlib import Path
from research.native.itd02.r1.native_policy import canonical

HERE = Path(__file__).resolve().parent
P = json.loads((HERE / "PREREG.json").read_text())
D = Path(sys.argv[1])
runs = [json.loads((D / f"fit-{rep}.json").read_text()) for rep in (1,2)]

for r in runs:
    assert r["schema"] == P["schema"]
    assert r["source"] == P["upstream_original"]
    assert r["original_owner"] == P["original_native_owner_head"]
    assert r["protocol_sha256"] == hashlib.sha256((HERE/"PREREG.json").read_bytes()).hexdigest()
    assert r["source_original_motor_fit_sha256"] == P["original_selected_motor_fit_sha256"]
    assert r["source_original_motor_fit_rows"] == 12
    assert r["fit_role_only"] is True
    assert r["development_reset_count"] == r["protected_reset_count"] == 0
    assert len(r["episodes"]) == sum(len(v) for v in P["roles"]["fit_only"].values())
    assert all(r["resource"][k] >= 0 for k in (
        "cpu_original_motor_fit_s", "cpu_new_public_fit_s", "peak_rss_kib"))
    for e in r["episodes"]:
        assert e["family"] in P["roles"]["fit_only"]
        assert e["seed_public_fit_role"] in P["roles"]["fit_only"][e["family"]]
        assert e["n_selected_actions"] == len(e["rows"]) and e["rows"]
        assert e["rows_sha256"] == hashlib.sha256(canonical(e["rows"])).hexdigest()
        assert len(e["rows"]) <= P["source_max_actions_per_episode"]
        prev = None
        for i, row in enumerate(e["rows"]):
            assert row["source_step"] == i
            assert row["selected_action"] in (0, 1, 2)
            assert len(row["before"]) == len(row["returned_after"]) == 6
            assert row["before"][5] in (0,1) and row["returned_after"][5] in (0,1)
            assert type(row["terminated"]) is bool and type(row["truncated"]) is bool
            assert row["source_reward"] >= -1 and row["source_reward"] <= 1
            assert row["information_turn"] is False or row["selected_action"] in (0, 1)
            assert row["new_front_after_turn"] == (
                ("BLOCKED" if row["returned_after"][5] else "CLEAR")
                if row["information_turn"] else None)
            assert row["own_trajectory_discounted_future_reward"] == \
                row["own_trajectory_discounted_future_reward"]
            if prev is not None:
                assert row["before"] == prev, "ORIGINAL_NEXT_PUBLIC_CONTINUITY"
            if i + 1 < len(e["rows"]):
                assert not (row["terminated"] or row["truncated"])
            prev = row["returned_after"]

    count = {str(a):sum(int(row["selected_action"]==a)
                       for e in r["episodes"] for row in e["rows"])
             for a in (0,1,2)}
    assert count == r["selected_actions"]
    assert sum(count.values()) == sum(e["n_selected_actions"] for e in r["episodes"])
    for f, total in r["by_family"].items():
        rows = [row for e in r["episodes"] if e["family"] == f for row in e["rows"]]
        assert total["selected_left"] == sum(row["selected_action"]==0 for row in rows)
        assert total["selected_right"] == sum(row["selected_action"]==1 for row in rows)
        assert total["selected_forward"] == sum(row["selected_action"]==2 for row in rows)
        assert total["information_turn_revealed_blocked"] == sum(
            row["new_front_after_turn"]=="BLOCKED" for row in rows)
        assert total["information_turn_revealed_clear"] == sum(
            row["new_front_after_turn"]=="CLEAR" for row in rows)
        assert total["source_actions"] == len(rows)
        assert total["source_episodes"] == len(P["roles"]["fit_only"][f])
        assert total["actually_selected_information_turns"] == sum(
            row["information_turn"] for row in rows)

scientific_keys = (
    "schema", "source", "original_owner", "protocol_sha256",
    "source_original_motor_fit_sha256", "source_original_motor_fit_rows",
    "source_original_motor_fit_counts", "fit_role_only",
    "development_reset_count", "protected_reset_count", "policy",
    "by_family", "selected_actions", "episodes", "scientific_admission"
)
for k in scientific_keys:
    assert runs[0][k] == runs[1][k], ("INDEPENDENT_SOURCE_PROCESSES_DIFFER", k)

count = runs[0]["selected_actions"]
blocked = sum(v["information_turn_revealed_blocked"]
              for v in runs[0]["by_family"].values())
clear = sum(v["information_turn_revealed_clear"]
            for v in runs[0]["by_family"].values())
if any(v == 0 for v in count.values()):
    decision = "NO_GO_REAL_SOURCE_FIT_ACTION_COVERAGE"
elif blocked == 0 or clear == 0:
    decision = "NO_GO_REAL_SOURCE_FIT_INFORMATION_OUTCOME_COVERAGE"
else:
    decision = "FIT_ACTION_AND_INFORMATION_OUTCOME_COVERAGE_ONLY"
assert runs[0]["scientific_admission"] == decision
result = {
    "schema": "optimizer.o22o.original-source-selected-action-fit-reconcile.v1",
    "source": P["upstream_original"],
    "authentic_source_public_fit": True,
    "original_episodes_run_twice": len(runs[0]["episodes"]),
    "double_process_identical_science": True,
    "selected_action_counts": count,
    "original_selected_turn_information_blocked": blocked,
    "original_selected_turn_information_clear": clear,
    "no_original_development_or_protected_steps": True,
    "scientific_gate": decision,
    "limits": [
        "Source true selected FIT only, not valid or protected independent science.",
        "Return-to-go is own on-policy continuation, not causal alternative action value.",
        "No tested native local-cell novelty, no conventional winner, no transfer.",
    ],
}
blob = canonical(result)
(D/"comparison.json").write_bytes(blob + b"\n")
print("O22O_ORIGINAL_TWO_INDEPENDENT_FIT_PROCESSES=PASS")
print("O22O_SCIENTIFIC_SHA256=" + hashlib.sha256(blob).hexdigest())
print("O22O_FIT_QUALIFICATION=" + decision)
print("O22O_FIT_SELECTED_ACTIONS=" + json.dumps(count,sort_keys=True))
print("O22O_FIT_INFO_REVEALED_BLOCKED=" + str(blocked))
print("O22O_FIT_INFO_REVEALED_CLEAR=" + str(clear))
print("O22O_NEW_DEV_AND_PROTECTED_SOURCE_ACTIONS=ZERO")
