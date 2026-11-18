#!/usr/bin/env python3
"""Independent, read-only reaggregation of pinned, original CKAD21 native evidence."""
import hashlib
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINS = json.loads((HERE / "source_pins.json").read_text(encoding="utf-8"))
raw = (HERE / "original-CKAD21-result.json").read_bytes()
blob_hash = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()
assert blob_hash == PINS["source_result_git_blob_sha"], "SOURCE_BLOB_DRIFT"
j = json.loads(raw)
assert j["schema"] == PINS["result_schema"]
assert j["source_sha256"] == PINS["source_sha256"]
assert j["classification"] == "DEVELOPMENT_NO_GO"
assert j["development_pass"] is False
assert j["scientific_pass"] is False and j["accepted_native"] is False
assert j["deployment"] == "NONE"
seeds = [101, 202, 303]
assert [s["seed"] for s in j["seeds"]] == seeds
assert [x["seed"] for x in j["final_checkpoints"]] == seeds
for n, pin in enumerate(PINS["checkpoint_sources"]):
    checkpoint = HERE / ("original-" + pin["name"])
    raw_ckpt = checkpoint.read_bytes()
    assert len(raw_ckpt) == pin["size"], "CKPT_BYTES"
    assert hashlib.sha256(raw_ckpt).hexdigest() == pin["sha256"], "CKPT_SHA256"
    h = hashlib.sha1(b"blob " + str(len(raw_ckpt)).encode() + b"\x00" + raw_ckpt).hexdigest()
    assert h == pin["git_blob_sha"], "CKPT_GIT_BLOB"
    assert j["final_checkpoints"][n]["sha256"] == pin["sha256"]
arms = ("context_active", "context_random", "exact_mixture", "pooled_replay",
        "beta", "trailing_mle", "frozen_ckad20", "untrained")
phases = {"first": (0,), "late": (3,), "returning": (0, 3),
          "shifted": (1, 4), "novel": (5,)}
def aggregate(indexes):
    return {arm: sum(seed["sessions"][p]["evaluation"][arm]["reward_sum"]
                     for seed in j["seeds"] for p in indexes) for arm in arms}
actual = {name: aggregate(indexes) for name, indexes in phases.items()}
for seed in j["seeds"]:
    for phase, session in enumerate(seed["sessions"]):
        assert session["session"] == phase
        assert session["evaluation"]["context_active"]["episodes"] == 96
        for arm in arms:
            assert session["evaluation"][arm]["episodes"] == 96
            assert 0 <= session["evaluation"][arm]["reward_sum"] <= 96
            assert (session["evaluation"][arm]["view_disagreements"] == 0)
        assert session["parity"]["mismatches"] == 0
parity = {k: sum(session["parity"][k] for seed in j["seeds"]
                 for session in seed["sessions"])
          for k in ("forecasts", "decisions", "mismatches")}
assert parity == PINS["derived"]["parity"]
for name in phases:
    assert actual[name] == PINS["derived"][name], "AGGREGATION_DRIFT_" + name
assert actual["first"]["context_active"] == 251
assert actual["first"]["pooled_replay"] == 231
assert actual["late"]["context_active"] == actual["late"]["pooled_replay"] == 246
assert actual["returning"]["context_active"] == 497
assert actual["returning"]["pooled_replay"] == 477
assert actual["shifted"]["context_active"] == 485
assert actual["shifted"]["pooled_replay"] == 397
assert actual["novel"]["context_active"] == 162
assert actual["novel"]["pooled_replay"] == 77
assert j["development_gates"] == {
    "returning_reward": True, "returning_vs_mle": True,
    "returning_vs_pooled": False, "shifted_reward": True}
assert Fraction(*j["development_metrics"]["returning_delta_pooled"]) == Fraction(20, 576)
assert Fraction(*j["development_metrics"]["returning_reward"]) == Fraction(497, 576)
assert Fraction(*j["development_metrics"]["shifted_reward"]) == Fraction(485, 576)
assert Fraction(20,576) < Fraction(5,100)
assert actual["returning"]["context_active"] == actual["returning"]["exact_mixture"]
for p in range(6):
    assert all(seed["sessions"][p]["evaluation"]["context_active"]["reward_sum"] ==
               seed["sessions"][p]["evaluation"]["exact_mixture"]["reward_sum"]
               for seed in j["seeds"])
novel = [{"seed":s["seed"],
          "active":s["sessions"][5]["evaluation"]["context_active"]["reward_sum"],
          "pooled":s["sessions"][5]["evaluation"]["pooled_replay"]["reward_sum"]}
         for s in j["seeds"]]
assert novel == [{"seed":row["seed"],"active":row["novel_active"],"pooled":row["novel_pooled"]}
                 for row in PINS["derived"]["per_seed_novel"]]
print(json.dumps({"status":"PASS_RECOVERED_SOURCE", "source_git_blob":blob_hash,
                  "checkpoint_sha256_verified":len(seeds),"evaluation_sessions":18,
                  "total_per_arm":1728,"aggregated":actual,"parity":parity,
                  "returning_advantage_over_pooled":[20,576],
                  "later_return_advantage_over_pooled":[0,288],
                  "scientific_pass":False,"deployment":"NONE"},sort_keys=True))
