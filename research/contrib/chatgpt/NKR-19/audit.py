"""NKR19 frozen retrospective audit of consumed FKP26 public transcripts.

NEVER imports an external environment or performs reset/do actions. Scored
prediction uses only earlier public observations plus current state/action.
This is retrospective development, not pristine source-native science.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from yggdrasil.public_causal_cells import PublicCausalCells
from yggdrasil.native_relation_memory import NativeRelationMemory

SEEDS = (996100,996101,996102,996103)
PINS = (
"c8c151065c6bdd6f303ae28f995a55b33a910c1985c536b7cf30cdb360d89179",
"53b06c8cbdc22b8da399e75f60aa4d55a3179fba28f5284ddeb9012435f632df",
"9b63fbefe5dcfd98801b058277cac9141574a5bede072cea228a976ac69d7cca",
"34929d6cc2e1145a6a930b9e6e1542dc2733ac0366ea8c5be70fb76223e31676")
ZIP_PIN = "4c877a6df5685516cc7ba445b2b90c90afb3674537ab741fb67adb5453e5c9ef"
UPSTREAM = "c94e9a4cd3641588b6b8507e71ccee5c27032bdf"
ARMS = ("native_beta","exact_beta","empirical_mle","last_key","persistence","chance")
TARGETS = ("reward","after")
SCALES = (8,16,24)

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,
                      allow_nan=False).encode("ascii")

def sha(x):
    return hashlib.sha256(x).hexdigest()

def require(ok, reason):
    if not ok:
        raise ValueError("NKR19_"+reason)

def load_source(path):
    raw = Path(path).read_bytes()
    require(len(raw)<=65536 and sha(raw)==ZIP_PIN, "CACHED_ARCHIVE_SHA_OR_SIZE")
    reports = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        members = archive.infolist()
        require(len(members)<=32 and sum(m.file_size for m in members)<=262144,
                "ARCHIVE_MEMBER_BUDGET")
        for seed, pin in zip(SEEDS,PINS):
            matches = [m for m in members if
                       PurePosixPath(m.filename).name==f"seed-{seed}.json"]
            require(len(matches)==1, "MISSING_OR_DUPLICATE_PUBLIC_SEED")
            member = matches[0]
            require(member.file_size<=65536 and not member.flag_bits&1,
                    "PUBLIC_RECEIPT_MEMBER_LIMIT")
            d = json.loads(archive.read(member))
            require(d.get("schema")=="fkp24.native-public-mdp-transcript.v1"
                    and type(d.get("public_seed")) is int and d["public_seed"]==seed
                    and d.get("upstream_sha")==UPSTREAM
                    and d.get("counterfactuals_used") is False
                    and d.get("forbidden_info_passed_to_policy") is False
                    and d.get("physical_do_actions")==31, "SOURCE_RECEIPT_CONTRACT")
            rows = d.get("public_transitions")
            validate_rows(rows)
            require(sha(canon(rows))==pin==d.get("public_transitions_sha256"),
                    "ORDERED_PUBLIC_TRANSITION_SHA")
            reports[seed] = rows
    return reports

def validate_rows(rows):
    require(type(rows) is list and len(rows)==31, "PUBLIC_ROW_COUNT")
    keys = {"before","action","reward","after","terminated","truncated"}
    for i,row in enumerate(rows):
        require(type(row) is dict and set(row)==keys, "PUBLIC_ROW_FIELDS")
        require(all(type(row[k]) is int and row[k] in (0,1)
                    for k in ("before","action","reward","after")), "PUBLIC_BINARY_TYPES")
        require(all(type(row[k]) is bool for k in ("terminated","truncated")),
                "PUBLIC_END_TYPES")
        if i:
            require(row["before"]==rows[i-1]["after"], "PUBLIC_CHRONOLOGY")
        require((not row["terminated"] and not row["truncated"]) if i<30
                else (row["terminated"] or row["truncated"]), "PUBLIC_END_ORDER")

def address(slot):
    return (slot-7,True) if slot>=7 else (slot,False)

def slot(world,target,before):
    return world*4+target*2+before

def native_probability(bank,world,target,before,action):
    local, retained = address(slot(world,target,before))
    return Fraction(*bank.outcome_probability(local,action,retained=retained))

def update(bank,world,row):
    for target,name in enumerate(TARGETS):
        local,retained = address(slot(world,target,row["before"]))
        bank.observe(local,row["action"],row[name],retained=retained)

def conventional(prefix,row,name,mode):
    # Independent fully fitted saturated Bernoulli/bin lookup models.
    seen = [r[name] for r in prefix if r["before"]==row["before"]
            and r["action"]==row["action"]]
    if mode=="exact_beta":
        return Fraction(sum(seen)+1,len(seen)+2)
    if mode=="empirical_mle":
        return Fraction(sum(seen),len(seen)) if seen else Fraction(1,2)
    if mode=="last_key":
        return Fraction(seen[-1]) if seen else Fraction(1,2)
    if mode=="persistence":
        return Fraction(row["before"] if name=="after" else prefix[-1]["reward"])
    return Fraction(1,2)

def predict_all(bank,world,prefix,row):
    answers={}
    for arm in ARMS:
        answers[arm] = [
            native_probability(bank,world,t,row["before"],row["action"])
            if arm=="native_beta" else conventional(prefix,row,name,arm)
            for t,name in enumerate(TARGETS)]
    require(answers["native_beta"]==answers["exact_beta"],"EXACT_CONTROL_PARITY")
    return answers

def rational(q):
    return {"numerator":q.numerator,"denominator":q.denominator,"value":float(q)}

def empty_scores():
    return {arm:{name:[] for name in TARGETS} for arm in ARMS}

def add_score(scores,answers,row):
    for arm in ARMS:
        for t,name in enumerate(TARGETS):
            scores[arm][name].append((answers[arm][t]-row[name])**2)

def summarize(scores):
    out={}
    for arm,targets in scores.items():
        values=[q for group in targets.values() for q in group]
        out[arm]={name:rational(sum(group)/len(group)) for name,group in targets.items()}
        out[arm]["pooled"]=rational(sum(values)/len(values))
        out[arm]["scored_outputs"]=len(values)
    return out

def ratios(bank,slots):
    return [list(bank.outcome_probability(address(s)[0],a,retained=address(s)[1]))
            for s in slots for a in (0,1)]

def fixed_scale(data,k):
    clock=time.monotonic()
    bank=PublicCausalCells()
    previous=None
    retained_reads=0
    replay_skips=0
    for world,seed in enumerate(SEEDS):
        used=set()
        prefix=data[seed][:k]
        for i in range(24):
            index=i%k
            # Original event identity, never compare only state/action/outcome:
            # independent repeated physical outcomes count; replayed events don't.
            identity=(seed,index)
            if identity in used:
                replay_skips+=1
                continue
            used.add(identity)
            update(bank,world,prefix[index])
        cold=PublicCausalCells.restore(bank.snapshot())
        require(cold.snapshot()==bank.snapshot(),"COLD_SNAPSHOT_PARITY")
        if previous is not None:
            expected,oldslots=previous
            actual=ratios(cold,oldslots)
            require(actual==expected,"SEPARATE_ADDRESS_RETENTION")
            retained_reads+=len(actual)
        oldslots=range((world+1)*4)
        previous=(ratios(cold,oldslots),oldslots)
    training_seconds=time.monotonic()-clock
    before=bank.snapshot()
    scores=empty_scores()
    trace=[]
    for world,seed in enumerate(SEEDS):
        prefix=data[seed][:k]
        for index in range(24,31):
            row=data[seed][index]
            answers=predict_all(bank,world,prefix,row)
            # Target access is evaluator-only after each arm's prediction.
            add_score(scores,answers,row)
            trace.append([world,index,[[p.numerator,p.denominator]
                          for p in answers["native_beta"]]])
    require(bank.snapshot()==before,"HELDOUT_UPDATED_FROZEN_MODEL")
    # Each original event updates two target counters, not two source actions.
    import struct
    total=sum(struct.unpack(">"+"H"*64, before[4:-32]))
    require(total==4*k*2,"DUPLICATE_INFLATION_OR_LOST_UPDATE")
    return {"unique_training_events":4*k,"presentations":96,
            "replayed_presentations_skipped":replay_skips,
            "native_outcome_updates":total,"retained_probability_readouts":retained_reads,
            "retention_all_equal":True,"checkpoint_bytes":len(before),
            "checkpoint_sha256":sha(before),"scores":summarize(scores),
            "prediction_trace_sha256":sha(canon(trace)),
            "training_seconds":training_seconds}

def prequential(data):
    bank=PublicCausalCells()
    scores=empty_scores()
    trace=[]
    for world,seed in enumerate(SEEDS):
        prefix=[]
        for index,row in enumerate(data[seed]):
            if index>=8:
                answers=predict_all(bank,world,prefix,row)
                add_score(scores,answers,row)
                trace.append([world,index,[[p.numerator,p.denominator]
                              for p in answers["native_beta"]]])
            update(bank,world,row)
            prefix.append(row)
    cold=PublicCausalCells.restore(bank.snapshot())
    require(cold.snapshot()==bank.snapshot(),"PREQUENTIAL_COLD")
    return {"scores":summarize(scores),"scored_transitions":92,
            "checkpoint_sha256":sha(bank.snapshot()),"checkpoint_bytes":164,
            "prediction_trace_sha256":sha(canon(trace))}

def deterministic_audit(data):
    bank=NativeRelationMemory()
    groups={}
    rejected=0
    algebraic=0
    for world,seed in enumerate(SEEDS):
        for index,row in enumerate(data[seed]):
            for target,name in enumerate(TARGETS):
                key=(world,target,row["before"],row["action"])
                groups.setdefault(key,set()).add(row[name])
                local,retained=address(world*2+target)
                before=bank.checkpoint()
                try:
                    bank.observe_public(local,row["before"],row["action"],row[name],
                                        f"cached:{seed}:{index}:{name}",retained=retained)
                except ValueError as exc:
                    require(str(exc) in ("NATIVE_RELATION_CONFLICTING_DUPLICATE",
                            "NATIVE_RELATION_INCONSISTENT_CAUSAL_EVIDENCE"),
                            "UNEXPECTED_DETERMINISTIC_REJECTION")
                    require(bank.checkpoint()==before,"DETERMINISTIC_PARTIAL_WRITE")
                    rejected+=1
                    algebraic+=str(exc)=="NATIVE_RELATION_INCONSISTENT_CAUSAL_EVIDENCE"
    return {"observed_input_groups":len(groups),
            "groups_with_both_outcomes":sum(len(v)>1 for v in groups.values()),
            "rejected_deterministic_updates":rejected,
            "algebraic_rejections":algebraic,
            "accepted_unique_deterministic_pairs":bank.unique_observations,
            "interpretation":"Input aliasing, randomness and nonstationarity are not distinguished. Rejections do not make public measurements false."}

def stable(result):
    result=json.loads(json.dumps(result))
    for key in ("wall_seconds","environment","source_candidate_sha","setup"):
        result.pop(key,None)
    for item in result["scales"].values():
        item.pop("training_seconds",None)
    return result

def run(data):
    clock=time.monotonic()
    results={str(k):fixed_scale(data,k) for k in SCALES}
    top=results["24"]["scores"]
    native=Fraction(top["native_beta"]["pooled"]["numerator"],
                    top["native_beta"]["pooled"]["denominator"])
    controls=[Fraction(top[a]["pooled"]["numerator"],top[a]["pooled"]["denominator"])
              for a in ("chance","persistence")]
    gain=all(q-native>=Fraction(1,50) for q in controls)
    result={"schema":"yggdrasil.nkr19.cached-external-knowledge.result.v1",
            "classification":"DEV_FORECAST_GAIN" if gain else "DEV_NO_FORECAST_GAIN",
            "engineering_contract_pass":True,"scientific_pass":False,"accepted_native":False,
            "original_source_actions":0,"cached_original_source_actions":124,
            "cached_earned_rewards":sum(r["reward"] for rows in data.values() for r in rows),
            "source_zip_sha256":ZIP_PIN,"transition_sha256":list(PINS),
            "scales":results,"prequential":prequential(data),
            "deterministic_audit":deterministic_audit(data),
            "native_vs_strong_equivalent_control_brier_gain":0,
            "source_candidate_sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
            "environment":{"python":sys.version,"platform":platform.platform()},
            "wall_seconds":time.monotonic()-clock}
    require(result["cached_earned_rewards"]==66,"SOURCE_PUBLISHED_SUMMARY_DRIFT")
    require(result["wall_seconds"]<=120,"AUDIT_WALL_BUDGET")
    result["stable_result_sha256"]=sha(canon(stable(result)))
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-zip",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--verify-env",action="store_true")
    args=p.parse_args()
    data=load_source(args.source_zip)
    result=run(data)
    if args.verify_env:
        expected=json.loads(os.environ["NKR19_EXPECTED_RESULT"])
        require(stable(result)==stable(expected),"WINDOWS_REPLICATION_DRIFT")
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"],"a") as f:
            f.write("result="+json.dumps(result,separators=(",",":"),sort_keys=True)+"\n")
    print("NKR19_CACHED_EXTERNAL_KNOWLEDGE="+json.dumps(result,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
