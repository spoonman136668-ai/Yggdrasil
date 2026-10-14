"""Development-only source-consumption check; NEVER accesses heldout first-use seeds."""
import importlib.util, json
from pathlib import Path

p=Path(__file__).resolve().parent/"execute.py"
spec=importlib.util.spec_from_file_location("y076_fixed",p)
assert spec and spec.loader
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

SEED=9440
FAMILY=m.FAMILIES[0]
REPORT=[]
for pair,onset in (((5,12),1),((4,11),1),((5,12),4)):
    witness={"anchor_pair_checks":0}
    m.m.y58.install_transposition(onset,pair,witness)
    try:
        old=m.m.y64.dual_public_samples(SEED,FAMILY)
        new=m.new_public_samples(SEED,FAMILY)
        assert set(old)==set(new)=={0,1,3,5,7}
        assert all(set(old[e])=={"0","1"} and set(new[e])=={"0","1"} for e in (0,1,3))
        assert all(set(old[e])=={"2","4"} and set(new[e])=={"4","5"} for e in (5,7))
        assert sum(len(x) for x in old.values())==sum(len(x) for x in new.values())==10
        olddet=m.m.y59.detector(old)
        newdet=m.m.y59.detector(new)
        calls={"n":0}
        original=m.new_public_samples
        def tracked(s,f):
            calls["n"]+=1
            return original(s,f)
        m.new_public_samples=tracked
        try:
            candidate=m.new_candidate(SEED,FAMILY,"full",True)
        finally:
            m.new_public_samples=original
        assert calls["n"]>0, "NEW_SAMPLE_PATH_NOT_CONSUMED"
        assert candidate["public_scalar_reads"]==10
        record={"pair":pair,"onset":onset,"dev_seed":SEED,
                "new_sampler_calls":calls["n"],
                "old_detected":olddet["detected"],"new_detected":newdet["detected"],
                "read_addresses_old":{str(t):list(old[t]) for t in (5,7)},
                "read_addresses_new":{str(t):list(new[t]) for t in (5,7)},
                "sampled_late_values_differ":any(old[t]!=new[t] for t in (5,7)),
                "new_candidate_first":next((x["public_detected_swap_first_episode"]
                     for x in reversed(candidate["rows"])
                     if x["public_detected_swap_first_episode"] is not None),None)}
        REPORT.append(record)
    finally:
        m.m.y49.restore_environment()
assert len(REPORT)==3
print(json.dumps({"classification":"DEVELOPMENT_MECHANICAL_DIAGNOSTIC_ONLY",
                  "original_science_replayed":False,"sealed_seeds_consumed":False,
                  "report":REPORT},sort_keys=True))
