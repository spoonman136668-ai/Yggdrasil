"""MR34I3: source-original local BPTT primitive trace, TRAIN-only.

Pinned original model methods execute unmodified. A debugger line observer
snapshots float64 expressions at the first MR34I2 mismatching source update.
Plain-before, observed, and plain-after gradients reveal observer sensitivity.
No heldout or unfamiliar source is executed.
"""
from hashlib import sha256
from pathlib import Path
import json, subprocess, sys, time
import numpy as np
from research.mr34f.prospective_controls import episodes
from research.nci04_s4c1.native_predictive_quotient import NativePredictiveQuotient45
from research.nci04_s4c1.original_native_predictive_state import TRAIN,protocol as s4c1_protocol

FILE=Path(__file__).with_name("frozen_protocol.json")
TARGETS={"FaramaMiniGridDoorKey8":(3,1871),"DeepMindPycolabApprehend":(8,1901)}
ORIGINS={"FaramaMiniGridDoorKey8":"7f5853792ea7f04f75614661006d87fcf949f26d",
         "DeepMindPycolabApprehend":"6504c8065dd5322438f23a2a9026649904f3322a"}
PARENT="8e1561eb1a542e21307bac669c42435cf48e59bd"

def h(v):return sha256(v).hexdigest()
def enc(obj):return json.dumps(obj,sort_keys=True,separators=(",",":"))
def combined(a):return h(b"".join(v.tobytes() for v in a))
def verify(root,sha):
    root=Path(root).resolve()
    if (subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()!=sha
        or subprocess.check_output(["git","-C",str(root),"status","--porcelain"],text=True).strip()):
        raise ValueError("MR34I3_EXACT_SOURCE_PIN_OR_DIRTY")
    return root

def contract():
    q=json.loads(FILE.read_text())
    if (q["schema"]!="yggdrasil.mr34i3.original-local-analytic-gradient-primitive-observer.v1"
        or q["exact_MR34I2_parent_sha"]!="d12e3ba781c0e03bc277c4e58c1263662f00c9a9"
        or q["exact_S4C1_original_sha"]!=PARENT
        or q["sources"]!=ORIGINS
        or q["training_only_previously_consumed_source_seeds"]!=list(TRAIN)
        or q["excluded_held_dev_seeds"]!=[2003,2011,2017,2027,2029,2039,2053,2063]
        or q["original_training_algorithm"]!={"lr":.035,"l2":.0002,"clip":5,"beta1":.9,"beta2":.999,
            "epsilon":1e-8,"epochs_traced":1,
            "first_number_source_updates_per_family":{
              "FaramaMiniGridDoorKey8":3,"DeepMindPycolabApprehend":8}}
        or q["scientific_admission"]!="NO_GO"):
        raise ValueError("MR34I3_PREREGISTRATION_DRIFT")
    return q

def raw(v):
    if isinstance(v,np.ndarray):return v.tobytes(order="C")
    if isinstance(v,(float,int,np.number)):
        return np.float64(v).tobytes()
    raise ValueError("MR34I3_NONNUMERIC_OBSERVER_FIELD")

def observed_gradient(model,episode):
    """Read original stack frames but never write their locals or parameters."""
    bptt=NativePredictiveQuotient45.analytic_bptt.__code__
    forward=NativePredictiveQuotient45.forward.__code__
    f_at={98:("read","read"),99:("u","u"),100:("p","p"),101:("ns","next_s")}
    b_at={129:("dz","dz"),130:("du","du"),
          131:("dg0","dg"),132:("dg1","dg"),133:("dg2","dg"),
          134:("dr0","dr"),135:("dr1","dr"),136:("dr2","dr")}
    observations=[]
    def watcher(frame,event,arg):
        if frame.f_code not in (bptt,forward):return None
        if event=="line":
            stages=f_at if frame.f_code is forward else b_at
            stage=stages.get(frame.f_lineno)
            if stage:
                label,field=stage
                if field not in frame.f_locals:
                    raise ValueError("MR34I3_ORIGINAL_PRIMITIVE_UNAVAILABLE_"+label)
                step=(len(frame.f_locals.get("forecasts",[])) if
                    frame.f_code is forward else int(frame.f_locals["t"]))
                observations.append([("forward" if frame.f_code is forward else "backward"),
                                     step,label,h(raw(frame.f_locals[field]))])
        return watcher
    if sys.gettrace() is not None:
        raise ValueError("MR34I3_UNEXPECTED_EXISTING_TRACER")
    sys.settrace(watcher)
    try:
        gradient=model.analytic_bptt(episode)
    finally:
        sys.settrace(None)
    return gradient,observations

def local_audit(name,root,p):
    s4c1_protocol()
    original,receipts=episodes(root,name,TRAIN)
    source=h(enc(receipts).encode())
    if source!=p["source_provenance_first_gradient_MR34I2"][name]["source_event_sha"]:
        raise ValueError("MR34I3_SOURCE_RECEIPT_DRIFT")
    model=NativePredictiveQuotient45()
    if h(model.snapshot().encode())!=p["source_provenance_first_gradient_MR34I2"][name]["initial_native_model_snapshot_sha"]:
        raise ValueError("MR34I3_NATIVE_INITIALIZATION_DRIFT")
    # Original trainer calls this numerical check before ANY source updates.
    # The extra original analytic probe mirrors MR34I2 final qualification.
    before_finite_difference=model.analytic_bptt(original[0])
    finite_difference=model.source_gradient_finite_difference(original[0])
    a=[np.zeros_like(w) for w in model.params()]
    b=[np.zeros_like(w) for w in model.params()]
    expected_step,expected_seed=TARGETS[name]
    target=None
    started=time.process_time_ns()
    for idx,episode in enumerate(original[:expected_step]):
        step=idx+1
        pre=h(b"".join(x.tobytes() for x in model.params()))
        if step==expected_step:
            untraced_before=model.analytic_bptt(episode)
            traced,stages=observed_gradient(model,episode)
            untraced_after=model.analytic_bptt(episode)
            if len(stages)<len(episode)*8:
                raise ValueError("MR34I3_INCOMPLETE_ORIGINAL_PRIMITIVE_TRACE")
            target={
                "source_seed":TRAIN[idx],
                "source_45_weight_before_gradient_sha":pre,
                "source_original_episode_action_count":len(episode),
                "untraced_before_shared_sha":h(untraced_before[0].tobytes()),
                "untraced_before_local_sha":h(untraced_before[1].tobytes()),
                "original_debug_traced_shared_sha":h(traced[0].tobytes()),
                "original_debug_traced_local_sha":h(traced[1].tobytes()),
                "untraced_after_shared_sha":h(untraced_after[0].tobytes()),
                "untraced_after_local_sha":h(untraced_after[1].tobytes()),
                "observer_changes_original_analytic_gradient":not (
                    combined(untraced_before)==combined(traced)==combined(untraced_after)),
                "source_original_forward_backward_stage_sequence":stages,
            }
            if TRAIN[idx]!=expected_seed:
                raise ValueError("MR34I3_TARGET_NATIVE_SEED_DRIFT")
        # Original training arithmetic is kept unchanged, with first
        # unobserved gradient used once for a single original Adam update.
        gradients=list(model.analytic_bptt(episode))
        grads=[g+(.0002*w if w.ndim==2 else 0.)
               for g,w in zip(gradients,model.params())]
        norm=float(np.sqrt(sum(float(np.sum(g*g)) for g in grads)))
        factor=min(1.,5/max(norm,1e-12))
        for i,(w,g) in enumerate(zip(model.params(),grads)):
            g=g*factor
            a[i]=.9*a[i]+(1.-.9)*g
            b[i]=.999*b[i]+(1.-.999)*g*g
            m=a[i]/(1.-.9**step)
            v=b[i]/(1.-.999**step)
            w-=.035*m/(np.sqrt(v)+1e-8)
        model.train_updates+=1
    if target is None:raise ValueError("MR34I3_TARGET_NOT_EXECUTED")
    return {
        "original_source_git_sha":ORIGINS[name],
        "source_training_episode_receipts_sha":source,
        "native_training_seeds":list(TRAIN),
        "original_finite_difference_grad_check_passed":finite_difference["passed"],
        "pre_finite_difference_gradient_sha":combined(before_finite_difference),
        "target_original_training_update":expected_step,
        "exact_original_native_source_primitive_evidence":target,
        "after_target_update_native_weight_sha":combined(model.params()),
        "source_training_only_native_primitive_CPU_ns":time.process_time_ns()-started,
    }

def main(parent,farama,pycolab):
    p=contract()
    verify(parent,PARENT)
    roots={name:verify(root,ORIGINS[name]) for name,root in
           zip(ORIGINS,(farama,pycolab))}
    sys.path.insert(0,str(Path(parent).resolve()))
    for root in roots.values():sys.path.insert(0,str(root))
    from research.mr27.natural_memory import source_guard
    source_guard(roots["FaramaMiniGridDoorKey8"])
    started=time.process_time_ns()
    out={name:local_audit(name,root,p) for name,root in roots.items()}
    for name,root in roots.items():verify(root,ORIGINS[name])
    verify(parent,PARENT)
    import psutil
    info=psutil.Process().memory_info()
    peak=getattr(info,"peak_wset",None)
    if not peak:
        import resource
        peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
    print("MR34I3_LOCAL_GRADIENT_PRIMITIVE_AUDIT="+enc({
       "frozen_protocol_sha256":h(FILE.read_bytes()),
       "original_unchanged_S4C1_source_sha":PARENT,
       "source_training_only_primitives":out,
       "full_original_source_and_tracing_cpu_ns":time.process_time_ns()-started,
       "full_original_process_peak_OS_RSS_bytes":int(peak),
       "held_and_third_original_source_first_use_consumed":False,
       "trained_model_portable_checkpoint_admission":"NO_GO",
       "qualified_scientific_transfer":"NO_GO",
       "G29_and_final_OS_regression":"BLOCKED"
    }))

if __name__=="__main__":
    if len(sys.argv)!=4:raise SystemExit("Supply original S4C1, Farama, Pycolab checkouts")
    main(*sys.argv[1:])
