"""MR34I2: development TRAINING-only original S4C1 first Adam-update fingerprints.

This diagnostic mirrors the arithmetic of the exact pinned S4C1 trainer.
No original source code, training inputs, hyperparameters or first-use are changed.
"""
import json, math, subprocess, sys, time
from pathlib import Path
from hashlib import sha256
import numpy as np

FILE=Path(__file__).with_name("frozen_protocol.json")
PARENT="8e1561eb1a542e21307bac669c42435cf48e59bd"
SRC={"FaramaMiniGridDoorKey8":"7f5853792ea7f04f75614661006d87fcf949f26d",
     "DeepMindPycolabApprehend":"6504c8065dd5322438f23a2a9026649904f3322a"}
SEEDS=(1861,1867,1871,1873,1877,1879,1889,1901,1907,1913,
       1931,1933,1949,1951,1973,1979,1987,1993,1997,1999)

def sha(b):return sha256(b).hexdigest()
def canonical(o):return json.dumps(o,sort_keys=True,separators=(",",":"))
def pair(a):return sha(b"".join(x.tobytes() for x in a))
def git(path,expected):
    path=Path(path).resolve()
    sha_actual=subprocess.check_output(["git","-C",str(path),"rev-parse","HEAD"],text=True).strip()
    dirty=subprocess.check_output(["git","-C",str(path),"status","--porcelain"],text=True).strip()
    if sha_actual!=expected or dirty:raise ValueError("MR34I2_EXACT_ORIGINAL_SOURCE_DRIFT")
    return path

def frozen():
    p=json.loads(FILE.read_text())
    q=p["original_training_algorithm"]
    if (p["schema"]!="yggdrasil.mr34i2.original_s4c1_train_only_first_optimizer_divergence.v1"
        or p["exact_original_Ygg_S4C1_git_sha"]!=PARENT
        or p["original_upstream_source_commits"]!=SRC
        or p["reused_only_consumed_S4C1_training_seeds"]!=list(SEEDS)
        or q["observed_only_first_n_epochs"]!=2
        or q["source_episodes_per_epoch"]!=20
        or q["adam_lr"]!=.035 or q["beta1"]!=.9 or q["beta2"]!=.999
        or q["epsilon"]!=1e-8 or q["l2"]!=.0002 or q["clip_l2"]!=5
        or p["no_old_held_cohort_read"] is not True
        or p["no_new_source_first_use"] is not True):
        raise ValueError("MR34I2_FROZEN_PROTOCOL_DRIFT")
    return p

def audit(name,root,protocol):
    from research.mr34f.prospective_controls import episodes
    from research.nci04_s4c1.original_native_predictive_state import (
        TRAIN,protocol as original_contract)
    from research.nci04_s4c1.native_predictive_quotient import NativePredictiveQuotient45
    if tuple(TRAIN)!=SEEDS:raise ValueError("MR34I2_ORIGINAL_COHORT_DRIFT")
    original_contract()
    native,receipts=episodes(root,name,SEEDS)
    source_digest=sha(canonical(receipts).encode())
    custody=protocol["source_input_custody_requirements"]
    if source_digest!=custody["previous_MR34I1_source_event_shas"][name]:
        raise ValueError("MR34I2_ORIGINAL_SOURCE_EPISODE_DRIFT")
    model=NativePredictiveQuotient45()
    initial=model.snapshot()
    if sha(initial.encode())!=custody["original_native_initializer_sha"]:
        raise ValueError("MR34I2_SOURCE_INITIAL_MODEL_DRIFT")
    finite_diff=model.source_gradient_finite_difference(native[0])
    moments1=[np.zeros_like(w) for w in model.params()]
    moments2=[np.zeros_like(w) for w in model.params()]
    traces=[]
    for epoch in (1,2):
        for j,episode in enumerate(native):
            t=len(traces)+1
            pre=pair(model.params())
            raw=list(model.analytic_bptt(episode))
            rawsha=[sha(g.tobytes()) for g in raw]
            if t==1 and (rawsha[0]!=custody["original_first_gradient_3x7_sha"][name]
                or rawsha[1]!=custody["original_first_gradient_8x3_sha"][name]):
                raise ValueError("MR34I2_ORIGINAL_FIRST_GRADIENT_DRIFT")
            reg=[g+(.0002*w if w.ndim==2 else 0.)
                 for g,w in zip(raw,model.params())]
            norm=float(np.sqrt(sum(float(np.sum(g*g)) for g in reg)))
            factor=min(1.,5/max(norm,1e-12))
            clipped=[g*factor for g in reg]
            adjusted1=[];adjusted2=[];changes=[]
            for i,(w,g) in enumerate(zip(model.params(),clipped)):
                moments1[i]=.9*moments1[i]+(1-.9)*g
                moments2[i]=.999*moments2[i]+(1-.999)*g*g
                m=moments1[i]/(1-.9**t)
                v=moments2[i]/(1-.999**t)
                delta=.035*m/(np.sqrt(v)+1e-8)
                adjusted1.append(m)
                adjusted2.append(v)
                changes.append(delta)
                w-=delta
            model.train_updates+=1
            traces.append({
                "epoch":epoch,"source_reset_seed":SEEDS[j],"adam_step":t,
                "pre45":pre,"raw_3x7":rawsha[0],"raw_8x3":rawsha[1],
                "regularized_45":pair(reg),
                "norm":sha(np.float64(norm).tobytes()),
                "clip_factor":sha(np.float64(factor).tobytes()),
                "clipped_45":pair(clipped),
                "adam_m1_45":pair(moments1),"adam_m2_45":pair(moments2),
                "adam_biascorrected_m1_45":pair(adjusted1),
                "adam_biascorrected_m2_45":pair(adjusted2),
                "weight_delta45":pair(changes),"post45":pair(model.params())})
    if len(traces)!=40:raise ValueError("MR34I2_NOT_40_REAL_UPDATES")
    return {"original_event_sha":source_digest,
            "original_training_source_actions":sum(len(e) for e in native),
            "initial_45_snapshot_sha":sha(initial.encode()),
            "original_native_first_gradient_finite_difference":finite_diff,
            "sequential_exact_original_adam_stage_hashes":traces,
            "after_two_epochs_model_snapshot_sha":sha(model.snapshot().encode())}

def main(ygg,farama,pycolab):
    cfg=frozen()
    originals={key:git(path,SRC[key]) for key,path in
               zip(SRC,(farama,pycolab))}
    git(ygg,PARENT)
    sys.path.insert(0,str(Path(ygg).resolve()))
    for path in originals.values():sys.path.insert(0,str(path))
    from research.mr27.natural_memory import source_guard
    source_guard(originals["FaramaMiniGridDoorKey8"])
    start=time.process_time_ns()
    rows={name:audit(name,path,cfg) for name,path in originals.items()}
    git(ygg,PARENT)
    for name,path in originals.items():git(path,SRC[name])
    import psutil
    info=psutil.Process().memory_info()
    peak=getattr(info,"peak_wset",None)
    if not peak:
        import resource
        peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
    print("MR34I2_FIRST_ADAM_UPDATE_AUDIT="+canonical({
        "protocol_sha256":sha(FILE.read_bytes()),
        "original_S4C1_git_sha":PARENT,
        "per_original_source":rows,
        "source_and_model_process_cpu_ns":time.process_time_ns()-start,
        "source_and_model_process_peak_resident_bytes":int(peak),
        "protected_original_unfamiliar_first_use_consumed":False,
        "cross_OS_exact_native_model_acceptance":"PENDING_INDEPENDENT_SHA_COMPARISON",
        "scientific_transfer_admission":"NO_GO"}))

if __name__=="__main__":
    if len(sys.argv)!=4:raise SystemExit("Supply original S4C1, Farama and Pycolab paths")
    main(*sys.argv[1:])
