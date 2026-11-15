#!/usr/bin/env python3
"""F50 source-only baseline fitting, checkpoint identity and resource receipts.

High-first (4096, 2048, 1024); source-law-disjoint FIT/VALIDATION; completely
separate from F50 target laws and sealed heldouts. No F50 scientific claims.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
from time import process_time

import numpy as np
import f50_worlds as world
import f50_conventional_controls as controls

SCHEMA = "yggdrasil.qtr01.f50.law-conditioned-source-fit.v1"
KINDS = controls.KINDS


class SourceFitRejected(controls.ConventionalRejected):
    pass


def _source_meta(kind,size,source_sha,source_receipt,train_receipt):
    if (kind not in KINDS or type(size) is not int or size not in world.BANK_SIZES
        or not re.fullmatch(r"[0-9a-f]{40}",source_sha)
        or source_receipt["size"]!=size
        or source_receipt["frozen_prereg_blob"]!=world.PREREG_BLOB
        or train_receipt.get("status")!="TRAINED_SOURCE_ONLY"
        or not train_receipt.get("source_training_complete")
        or train_receipt.get("scientific_pass") is not False):
        raise SourceFitRejected("F50_SOURCE_CHECKPOINT_UNQUALIFIED")
    return {"schema":SCHEMA,"kind":kind,"bank_size":size,
            "candidate_sha":source_sha,
            "frozen_prereg_blob":world.PREREG_BLOB,
            "source_data_sha256":source_receipt["source_data_sha256"],
            "source_fit_laws":source_receipt["fit_laws"],
            "source_validation_laws":source_receipt["validation_laws"],
            "episodes_per_law":world.TRAIN_EPISODES,
            "model_training":train_receipt,
            "no_target_first_use":True,"scientific_pass":False}


def _weight_arrays(kind,trained):
    if kind=="graph_conditioned_logistic":
        if type(trained) is not np.ndarray or trained.shape!=(controls.GRAPH_DIM+34+33+1,):
            raise SourceFitRejected("F50_WRONG_LOGISTIC_WEIGHTS")
        return {"coefficient":np.asarray(trained,dtype=np.float64)}
    torch,_,_=controls._torch()
    if not isinstance(trained,torch.nn.Module) or trained.kind!=kind:
        raise SourceFitRejected("F50_NEURAL_MODEL_KIND_MISMATCH")
    return {name:np.asarray(t.detach().cpu().numpy(),dtype=np.float32)
            for name,t in trained.state_dict().items()}


def _serialize_meta(meta):
    return np.frombuffer(json.dumps(meta,sort_keys=True,separators=(",",":"),
                                    allow_nan=False).encode("ascii"),dtype=np.uint8)


def write_checkpoint(path,kind,size,trained,source_sha,source_receipt,train_receipt):
    world.freeze()
    metadata=_source_meta(kind,size,source_sha,source_receipt,train_receipt)
    path=Path(path)
    if path.exists():
        raise SourceFitRejected("F50_REFUSE_SOURCE_CHECKPOINT_OVERWRITE")
    records=_weight_arrays(kind,trained)
    if not records or any(not np.isfinite(v).all() for v in records.values()):
        raise SourceFitRejected("F50_SOURCE_WEIGHTS_NONFINITE")
    packed={"metadata":_serialize_meta(metadata)}
    for name,value in records.items():
        packed["weight:"+name]=value
    np.savez_compressed(path,**packed)
    actual_sha=sha256(path.read_bytes()).hexdigest()
    cold,record=load_checkpoint(path,actual_sha,source_sha,
                                expected_kind=kind,expected_size=size)
    for name,value in records.items():
        restored=_weight_arrays(kind,cold)[name]
        if not np.array_equal(value,restored):
            raise SourceFitRejected("F50_SOURCE_WEIGHT_COLD_MISMATCH")
    if record!=metadata:
        raise SourceFitRejected("F50_SOURCE_METADATA_COLD_MISMATCH")
    return actual_sha,path.stat().st_size


def load_checkpoint(path,expected_digest,expected_source_sha,*,expected_kind,
                    expected_size):
    world.freeze()
    if (type(expected_digest) is not str or
        not re.fullmatch(r"[0-9a-f]{64}",expected_digest) or
        type(expected_source_sha) is not str or
        not re.fullmatch(r"[0-9a-f]{40}",expected_source_sha)
        or expected_kind not in KINDS
        or type(expected_size) is not int or expected_size not in world.BANK_SIZES):
        raise SourceFitRejected("F50_SOURCE_CHECKPOINT_PIN_INVALID")
    path=Path(path)
    if sha256(path.read_bytes()).hexdigest()!=expected_digest:
        raise SourceFitRejected("F50_SOURCE_CHECKPOINT_TAMPER")
    try:
        with np.load(path,allow_pickle=False) as archive:
            meta=json.loads(archive["metadata"].tobytes().decode("ascii"))
            if (meta["schema"]!=SCHEMA or
                meta["kind"]!=expected_kind or
                meta["bank_size"]!=expected_size or
                meta["candidate_sha"]!=expected_source_sha or
                meta["frozen_prereg_blob"]!=world.PREREG_BLOB or
                meta["episodes_per_law"]!=world.TRAIN_EPISODES or
                meta["no_target_first_use"] is not True or
                meta["scientific_pass"] is not False or
                not re.fullmatch(r"[0-9a-f]{64}",meta["source_data_sha256"])):
                raise ValueError("metadata drift")
            kind=meta["kind"]
            if kind=="graph_conditioned_logistic":
                expected={"coefficient":np.zeros(controls.GRAPH_DIM+34+33+1,
                                                dtype=np.float64)}
            else:
                expected=_weight_arrays(kind,controls.create_neural(kind))
            if set(archive.files)!={"metadata",*("weight:"+x for x in expected)}:
                raise ValueError("inventory drift")
            loaded={}
            for name,template in expected.items():
                actual=archive["weight:"+name]
                if (actual.shape!=template.shape or actual.dtype!=template.dtype
                    or not np.isfinite(actual).all()):
                    raise ValueError("invalid numeric array")
                loaded[name]=actual.copy()
            if kind=="graph_conditioned_logistic":
                result=loaded["coefficient"]
            else:
                torch,_,_=controls._torch()
                result=controls.create_neural(kind)
                result.load_state_dict({name:torch.from_numpy(val)
                                        for name,val in loaded.items()},strict=True)
            return result,meta
    except (KeyError,TypeError,ValueError,OSError,UnicodeError) as exc:
        raise SourceFitRejected("F50_SOURCE_CHECKPOINT_UNREADABLE") from exc


def run(size,output_dir,source_sha,*,budget_seconds=3600):
    """Fully fit all three source controls, or return a frozen resource stop."""
    world.freeze()
    world._check_bank_size(size)
    root=Path(output_dir)
    root.mkdir(parents=True,exist_ok=True)
    if any(root.iterdir()):
        raise SourceFitRejected("F50_SOURCE_OUTPUT_NOT_EMPTY")
    start=process_time()
    fit=controls.pretraining_dataset(size,validation=False)
    val=controls.pretraining_dataset(size,validation=True)
    receipt=controls.dataset_receipt(size,fit,val)
    fit_ids=tuple(sorted(fit))
    val_ids=tuple(sorted(val))
    report={"schema":SCHEMA,"source_commit":source_sha,
            "frozen_prereg_blob":world.PREREG_BLOB,
            "size":size,"source":receipt,
            "preprocessing_cpu_seconds":round(process_time()-start,6),
            "models":[],"target_outcomes":0,"scientific_pass":False}
    def save_receipt():
        target=root/"f50-source-fit-receipt.json"
        temporary=target.with_suffix(".partial")
        temporary.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",
                             encoding="utf-8")
        temporary.replace(target)
    save_receipt()
    for kind in KINDS:
        elapsed=process_time()-start
        # Frozen per-model ceiling: 60 minutes per 4096-law control,
        # regardless of the aggregate source-training budget.
        remaining=min(3600,budget_seconds-elapsed)
        if remaining<=0:
            report["status"]="RESOURCE_STOP"
            report["stopped_at"]=kind
            save_receipt()
            return report
        if kind=="graph_conditioned_logistic":
            model,details=controls.logistic_fit_source(
                fit,fit_ids,val,val_ids,budget_seconds=remaining)
        else:
            model,details=controls.train_neural_source(
                kind,fit,fit_ids,val,val_ids,budget_seconds=remaining)
        if model is None:
            report["status"]="RESOURCE_STOP"
            report["stopped_at"]=kind
            report["resource_receipt"]=details
            save_receipt()
            return report
        filename=f"f50-source-{size}-{kind}.npz"
        digest,nbytes=write_checkpoint(root/filename,kind,size,model,
                                        source_sha,receipt,details)
        report["models"].append({"kind":kind,"checkpoint":filename,
                                 "sha256":digest,"bytes":nbytes,
                                 "cold_restored":True,"fit":details})
        save_receipt()
        print(f"F50_SOURCE_FIT_COMPLETE_SIZE={size}_KIND={kind}",flush=True)
    report["status"]="ALL_THREE_SOURCE_ONLY_TRAINED"
    report["total_cpu_seconds"]=round(process_time()-start,6)
    save_receipt()
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-only",action="store_true")
    parser.add_argument("--source-commit",required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--bank",type=int,default=4096)
    parser.add_argument("--cpu-budget-seconds",type=int,default=10800)
    args=parser.parse_args()
    if not args.source_only:
        parser.error("F50_SOURCE_ONLY_REQUIRED_NO_DEV_TARGET_FIRST_USE")
    if args.cpu_budget_seconds>10800 or args.cpu_budget_seconds<1:
        parser.error("F50_SOURCE_BUDGET_OUTSIDE_FROZEN_BOUND")
    # High-first: all source banks must be pursued 4096->2048->1024,
    # with fail-closed resource stop and no changed seeds after seeing outcomes.
    if args.bank!=4096:
        parser.error("F50_HIGH_FIRST_BANK_4096_REQUIRED")
    record=run(args.bank,args.output,args.source_commit,
               budget_seconds=args.cpu_budget_seconds)
    print("F50_SOURCE_ONLY_STATUS="+record["status"],flush=True)
    print("F50_NO_DEV_TARGET_FIRST_USE=PASS",flush=True)


if __name__=="__main__":
    main()
