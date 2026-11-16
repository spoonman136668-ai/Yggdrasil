"""AAI-12V single frozen mechanical evaluation. Reserved independent science disarmed."""
import argparse
import hashlib
import json
import time
import world
import learner

def evaluate():
    if len(world.GROUPS)!=20 or len(world.FIXTURES)!=2:raise AssertionError("frozen source count changed")
    results={a:{k:[] for k in ("reuse","changed","novel","familiar")} for a in learner.ARMS}
    durations={a:0. for a in learner.ARMS}
    chosen={a:[] for a in learner.ARMS};trace=[];cold_count=0
    for fix in world.FIXTURES:
        for gi,(kind,*_) in enumerate(world.GROUPS):
            donor=world.train_rows(fix,gi,"donor")
            interfere=world.train_rows(fix,gi,"interference")
            initial=world.train_rows(fix,gi,"receiver")
            tests=world.heldout(fix,gi)
            observed_x={tuple(r["x"]) for r in initial}
            assert len(tests)==128 and not observed_x.intersection(x for x,y in tests)
            for arm in learner.ARMS:
                start=time.perf_counter()
                seed=f"AAI12V|{fix}|{gi}|RANDOM".encode("ascii")
                masks,obs,selected=learner.fit(donor,interfere,initial,arm,seed)
                probe=world.make_pair(fix,gi,"receiver",selected)
                # Sham probing revisits an already observed code, but is still a real do action.
                if arm!="sham_probe":
                    obs2=learner.public_events(probe,1)
                    assert selected not in obs
                    obs.update(obs2)
                elif learner.public_events(probe,1)[selected]!=obs[selected]:
                    raise AssertionError("sham outcome inconsistent")
                snap=learner.cold(masks,obs,tuple(initial[0]["ports"]),arm)
                restored=learner.restore(snap)
                preds=[learner.predict(*restored,x) for x,y in tests]
                durations[arm]+=time.perf_counter()-start
                cold_count+=1
                correct=[int(y==p) for p,(_,y) in zip(preds,tests)]
                results[arm][kind].extend(correct)
                chosen[arm].append(selected)
                trace.append([fix,gi,arm,selected,correct])
    if any(sum(len(x) for x in v.values())!=5120 for v in results.values()) or cold_count!=200:
        raise AssertionError("budget drift")
    accuracies={a:{k:round(sum(x)/len(x),9) for k,x in v.items()} for a,v in results.items()}
    for arm in learner.ARMS:
        accuracies[arm]["all"]=round(sum(map(sum,results[arm].values()))/5120,9)
    cand=accuracies["information_gain"];entropy=accuracies["predictive_entropy"]
    random=accuracies["random_probe"];fixed=accuracies["fixed_probe"]
    checks={
        "all_gain_vs_entropy_ge_0_02":cand["all"]>=entropy["all"]+.02-1e-10,
        "changed_gain_vs_entropy_ge_0_06":cand["changed"]>=entropy["changed"]+.06-1e-10,
        "novel_gain_vs_entropy_ge_0_04":cand["novel"]>=entropy["novel"]+.04-1e-10,
        "reuse_accuracy_ge_0_95":cand["reuse"]>=.95-1e-10,
        "familiar_accuracy_ge_0_90":cand["familiar"]>=.90-1e-10,
        "all_gain_vs_random_ge_0_03":cand["all"]>=random["all"]+.03-1e-10,
        "all_gain_vs_fixed_ge_0_03":cand["all"]>=fixed["all"]+.03-1e-10,
        "changed_noninferior_best_ge_minus_0_02":cand["changed"]>=max(v["changed"] for a,v in accuracies.items() if a!="information_gain")-.02-1e-10,
        "novel_noninferior_best_ge_minus_0_02":cand["novel"]>=max(v["novel"] for a,v in accuracies.items() if a!="information_gain")-.02-1e-10,
        "cost_ratio_to_entropy_le_2":durations["information_gain"]<=2*durations["predictive_entropy"],
    }
    return {"schema":"yggdrasil.aai12v.source-dev.v1",
      "classification":"DEV_ADMITTED_SCIENCE_UNVERIFIED" if all(checks.values()) else "DEV_NO_GO_NO_SCIENCE",
      "accuracies":accuracies,"checks":checks,"selected_code_trace":{a:chosen[a] for a in learner.ARMS},
      "model_fit_probe_cold_predict_seconds":{a:round(t,6) for a,t in durations.items()},
      "trace_sha256":hashlib.sha256(json.dumps(trace,separators=(",",":")).encode()).hexdigest(),
      "cold_roundtrips":cold_count,"source_only":True,"scientific_first_use":0,"native_modified":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dev",action="store_true")
    p.add_argument("--primary",action="store_true")
    a=p.parse_args()
    if a.primary:p.error("AAI12V SCIENTIFIC FIRST USE DISARMED")
    if not a.source_dev:p.error("only source-only mechanical --source-dev permitted")
    print("AAI12V_DEV="+json.dumps(evaluate(),sort_keys=True))
if __name__=="__main__":main()
