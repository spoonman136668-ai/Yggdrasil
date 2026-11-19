"""WSP189 separately frozen authentic physical light-tunnel study.

Reuse exact WSP187 learned latent state, full autoregressive / residual controls
and frozen negative WSP187 source admission; no copy or update of the learner.
WSP188 independently measured original public source counts/hashes only.
No new physical original actions; OFFLINE DEVELOPER evidence, not SCIENTIFIC_PASS.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import sys
import time
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"WSP-187"))
import light_state as prior

DATASET="lt_walks_v1"
SOURCE="juangamella/causal-chamber@967d59a42956872f37463cc561ecf6e9ceab9364"
MD5="dcad019186661a56de7a2d1db97fc2f0"
ZIP_SHA256="21fb3d0b2fad7d8ba544289ee7880785d1c35ae0b5d7f9302c794ca34d205a19"
SHA={
    "actuators_white":"5f220699e4090fa6e723e5a369434b58647a84c179a12903e1f550f0a988c670",
    "color_mix":"b9088d72f079ce320d6958025c7930d124b2d89919bfa4aa8c618c84cf50846f",
    "smooth_polarizers":"0bb0c193c44d73e7ad51b2519daf5f112d4b57904434b9e89d03f63ff95cae1d"
}
ROWS={"actuators_white":20000,"color_mix":10000,"smooth_polarizers":10000}
FIT_STOP=14000
SCHEMA="yggdrasil.wsp189.original-physical-light-latent-dev.v1"


def parse_original(blob:bytes,name:str):
    reader=csv.DictReader(io.StringIO(blob.decode("utf-8-sig"),newline=""))
    header=reader.fieldnames
    if not header or len(header)!=len(set(header)) or not set(prior.INPUTS+prior.OUTPUTS).issubset(header):
        raise ValueError("WSP189_ORIGINAL_COLUMNS")
    points=[]
    for row in reader:
        x=tuple(prior.read_float(row[k]) for k in prior.INPUTS)
        y=tuple(prior.read_float(row[k]) for k in prior.OUTPUTS)
        points.append((x,y))
        if len(points)>ROWS[name]:
            raise ValueError("WSP189_ROW_BUDGET")
    if len(points)!=ROWS[name]:
        raise ValueError("WSP189_ORIGINAL_ROWS")
    return points


def admit(path:Path):
    if not path.is_file() or not 0<path.stat().st_size<=prior.MAX_ARCHIVE:
        raise ValueError("WSP189_ZIP_LIMIT")
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=ZIP_SHA256 or hashlib.md5(raw).hexdigest()!=MD5:
        raise ValueError("WSP189_SOURCE_ZIP_HASH")
    data={}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        members={}
        total=0
        for info in z.infolist():
            name=PurePosixPath(info.filename)
            if name.is_absolute() or ".." in name.parts:
                raise ValueError("WSP189_ARCHIVE_TRAVERSAL")
            total+=info.file_size
            if info.file_size>prior.MAX_MEMBER or total>prior.MAX_EXPANDED:
                raise ValueError("WSP189_EXPANSION_BUDGET")
            if info.is_dir() or name.stem not in SHA:
                continue
            if name.suffix!=".csv" or name.stem in members:
                raise ValueError("WSP189_SOURCE_DUPLICATE")
            members[name.stem]=info
        if set(members)!=set(SHA):
            raise ValueError("WSP189_ORIGINAL_ROSTER")
        for name in SHA:
            with z.open(members[name]) as stream:
                blob=stream.read(prior.MAX_MEMBER+1)
            if len(blob)>prior.MAX_MEMBER or hashlib.sha256(blob).hexdigest()!=SHA[name]:
                raise ValueError("WSP189_ORIGINAL_MEMBER_HASH")
            data[name]=parse_original(blob,name)
    return data,{"archive_sha256":ZIP_SHA256,"archive_md5":MD5,
                 "source_members_sha256":dict(SHA),
                 "actual_original_rows":dict(ROWS)}


def run(path:Path):
    start=time.process_time()
    data,source=admit(path)
    base=data["actuators_white"]
    model=prior.fit(base[:FIT_STOP])
    wire=prior.frozen_core(model)
    old_sha=hashlib.sha256(wire).hexdigest()
    validation=prior.score(base,model,start=FIT_STOP)
    best_valid=min(prior.CONTROLS,
                   key=lambda name:(validation["mean_normalized_rmse"][name],name))
    dev={name:prior.score(data[name],model)
         for name in ("color_mix","smooth_polarizers")}
    if validation["rows"]!=ROWS["actuators_white"]-FIT_STOP:
        raise ValueError("WSP189_VALID_CUSTODY")
    if any(dev[name]["rows"]!=9999 for name in dev):
        raise ValueError("WSP189_PUBLIC_DEV_CUSTODY")
    if wire!=prior.frozen_core(model):
        raise ValueError("WSP189_FROZEN_CORE_DRIFT")

    comparisons={}
    for name,scored in dev.items():
        best=tuple(min(scored["normalized_rmse"][ctl][k]
                       for ctl in prior.CONTROLS) for k in range(3))
        candidate=scored["normalized_rmse"]["gated"]
        gains=tuple((best[k]-candidate[k])/best[k] if best[k]>0 else 0.
                    for k in range(3))
        comparisons[name]={
            "best_achieved_conventional_rmse_by_sensor":best,
            "gated_candidate_rmse_by_sensor":candidate,
            "gated_relative_gain_by_sensor":gains,
            "all_three_frozen_5pct_gain":all(g>=0.05 for g in gains)}
    return{
        "schema":SCHEMA,
        "source":SOURCE,
        "source_provenance":source,
        "source_num_source_bytes_seen_prior":True,
        "wsp187_source_failed_before_fit":True,
        "wsp188_original_source_metadata_only":True,
        "frozen_protocol_commit":"0c65996f282fd0949f4117410965ee93da889072",
        "fit_examples":FIT_STOP,
        "validation_count":validation["rows"],
        "public_development_count":{x:dev[x]["rows"] for x in dev},
        "validation_control_selected":best_valid,
        "validation":validation,
        "public_development":dev,
        "comparisons":comparisons,
        "frozen_both_dev_conditions_all_three_5pct":all(
            c["all_three_frozen_5pct_gain"] for c in comparisons.values()),
        "learned_compact_state_rank":prior.RANK,
        "pretrained_core_sha256":old_sha,
        "pretrained_core_bytes_unchanged":True,
        "old_law_behavioral_cold_retention_verified":False,
        "unfamiliar_new_mechanism_transfer_verified":False,
        "native_yggdrasil_trained":False,
        "causal_mechanism_identified":False,
        "original_new_physical_actions":0,
        "remote_lab_calls":0,
        "scientific_pass":False,
        "developer_only":True,
        "process_cpu_seconds":time.process_time()-start,
        "conclusion":"Public real physical source learning/transfer screen; no claim of general intelligence."
    }


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--archive",type=Path,required=True)
    opts=a.parse_args()
    print("WSP189_PUBLIC_LIGHT_20K_DEV_RESULT="+json.dumps(
        run(opts.archive),sort_keys=True,separators=(",",":"),allow_nan=False))


if __name__=="__main__":
    main()
