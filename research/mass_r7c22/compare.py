"""Mass R7-C22 dual-process exact public-source reconciliation."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from research.native.itd02.r1.native_policy import canonical
HERE=Path(__file__).resolve().parent
P=json.loads((HERE/"PREREG.json").read_text())
D=Path(sys.argv[1])
receipts={}
for arm in P["arms"]:
    trials=[json.loads((D/f"{arm}-{r}.json").read_text()) for r in (1,2)]
    for row in trials:
        assert row["schema"]==P["schema"] and row["arm"]==arm
        assert row["upstream"]==P["source"].split("@")[-1]
        assert row["native_head"]==P["original_native"].split()[-1]
        assert row["protocol_sha256"]==hashlib.sha256((HERE/"PREREG.json").read_bytes()).hexdigest()
        assert row["fit_rows"]==12
        assert len(row["episodes"])==len(P["fresh_public_dynamic_dev_seeds"])
        assert row["max_process_rss_kib"]>0
        assert row["fit_cpu_seconds"]>=0 and row["dev_cpu_seconds"]>=0
        assert row["totals"]["episodes"]==len(P["fresh_public_dynamic_dev_seeds"])
        for episode in row["episodes"]:
            assert episode["seed"] in P["fresh_public_dynamic_dev_seeds"]
            assert episode["actions"]==len(episode["trace"])
            assert hashlib.sha256(canonical(episode["trace"])).hexdigest()==episode["trace_sha256"]
    for metric in ("fit_sha256","fit_rows","fit_counts","totals","episodes","max_checkpoint_bytes"):
        assert trials[0][metric]==trials[1][metric],("NONDETERMINISM",arm,metric)
    receipts[arm]=trials[0]
assert len({receipts[a]["fit_sha256"] for a in P["arms"]})==1
results={arm:receipts[arm]["totals"] for arm in P["arms"]}
c=results["conventional"];m=results["native_sensor_memory"];g=results["guard_only"];o=results["original"]
if m["wins"] < c["wins"] or m["collision_terminated"] > c["collision_terminated"]:
    verdict="NO_GO_NATIVE_DYNAMIC_DISADVANTAGE"
elif m["wins"]==c["wins"] and m["collision_terminated"]==c["collision_terminated"]:
    verdict="NO_NATIVE_DYNAMIC_SUPERIORITY"
else:
    verdict="DEVELOPMENT_ONLY_NATIVE_DYNAMIC_GAIN_REQUIRES_EXTERNAL_INDEPENDENT_CONFIRMATION"
if (m["wins"]<o["wins"] or m["collision_terminated"]>o["collision_terminated"]):
    verdict="NO_GO_NATIVE_DYNAMIC_REGRESSION"
report={"schema":"mass.r7c22.two-process-reconciled-original-dynamic-v1",
    "source":P["source"],"source_dynamic_class_blob":P["dynamic_class_source_blob"],
    "prereg_sha256":hashlib.sha256((HERE/"PREREG.json").read_bytes()).hexdigest(),
    "fit_sha256":receipts[P["arms"][0]]["fit_sha256"],
    "new_dynamic_source_episodes_per_arm":len(P["fresh_public_dynamic_dev_seeds"]),
    "two_fresh_process_repetitions_equal":True,"owner_R3_changed":False,
    "protected_scientific_first_use":False,"scientific_decision":verdict,
    "totals":results,
    "resources":{a:{k:receipts[a][k] for k in
    ("fit_cpu_seconds","dev_cpu_seconds","max_process_rss_kib","max_checkpoint_bytes")} for a in P["arms"]}}
blob=canonical(report)
(D/"comparison.json").write_bytes(blob+b"\n")
print("R7C22_TWO_INDEPENDENT_SOURCE_PROCESS_RUNS=PASS")
print("R7C22_REPORT_SHA256="+hashlib.sha256(blob).hexdigest())
print("R7C22_SCIENTIFIC_DECISION="+verdict)
print("R7C22_PUBLIC_DYNAMIC_TOTALS="+json.dumps(results,sort_keys=True))
