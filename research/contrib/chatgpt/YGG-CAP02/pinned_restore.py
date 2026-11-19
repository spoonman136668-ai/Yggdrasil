"""CAP02 only: pinned, source-replayed original CAP01 model compatibility.

CAP01's *actual* original Linux/Windows trained weight receipts are immutable.
NumPy future-head GEMM has ULP-scale re-execution variation even at same source.
The generic CAP01 restore remains strict. This adapter only accepts the FOUR
exact, source-qualified published CAP01 checkpoint hashes below, independently
replays their entire witnessed tape, requires exact non-numeric/source fields
and <=1e-12 finite numeric drift, and restores the exact archived trained
parameters, not the approximate replay weights.

No unpinned/user-supplied/rehashed alternative checkpoint can enter here.
"""
from __future__ import annotations
import json
import math
from yggdrasil.native_context_basis import canonical,digest,require
from yggdrasil.native_segmented_continuation import (
    SegmentedNativeJEPA, EVENT_FIELDS, SCHEMA as CAP01_SCHEMA, MAX_SHARD,
    MAX_SHARDS,MAX_CHECKPOINT_BYTES,
)
from yggdrasil.native_episode_experience import NativeEpisodeExperience
from yggdrasil.native_jepa2_multilearner import ActionLatentSpecialist
from yggdrasil.native_jepa_temporal import TemporalLatentSpecialist
from yggdrasil.native_jepa_future import FutureStateHead,NativeFutureStateLearner

PINNED_ORIGINALS={
    "6babc23f4baf30afde14db5f2ca8eb3e55e321169aa245482478ff9855b68f14",
    "c503ccf979f90d6d4954f0e8d42133fc177017d4b47de80ee64c9524b870d827",
    "2d08c7e2d6d4d80acfc53727cdd0880d3f632c0f44bdb405b78feffba405938e",
    "e09b0cbbe47b95686f3ed3732baf080fe6b47301f0128c360437bf29bf9dfbfb",
}
TOLERANCE=1e-12

def require_compat(ok,name):
    if not ok:
        raise ValueError("CAP02_PINNED_CUSTODY_"+name)

def compare(a,b,path="$",stat=None):
    if stat is None:
        stat={"float_differences":0,"maximum_float_difference":0.0}
    require_compat(type(a) is type(b),"TYPE:"+path)
    if type(a) is dict:
        require_compat(set(a)==set(b),"FIELDS:"+path)
        for k in sorted(a):
            compare(a[k],b[k],path+"."+k,stat)
    elif type(a) is list:
        require_compat(len(a)==len(b),"LENGTH:"+path)
        for i,(x,y) in enumerate(zip(a,b)):
            compare(x,y,path+"["+str(i)+"]",stat)
    elif type(a) is float:
        require_compat(math.isfinite(a) and math.isfinite(b),
                       "NONFINITE:"+path)
        d=abs(a-b)
        require_compat(d<=TOLERANCE,"OUT_OF_TOLERANCE:"+path)
        if d:
            # ALL numeric changes must reside in trained specialist state
            # of the original source; native history/context/segments frozen.
            require_compat(
                path.startswith("$.future[") or
                path.startswith("$.one[") or
                path.startswith("$.temporal["),
                "NON_SPECIALIST_FLOAT:"+path)
            stat["float_differences"]+=1
            stat["maximum_float_difference"]=max(
                stat["maximum_float_difference"],d)
    else:
        require_compat(a==b,"EXACT_SOURCE_OR_STRUCTURE:"+path)
    return stat

def _public_event(record):
    require_compat(type(record) is dict and
                   set(record)==set(EVENT_FIELDS),
                   "REPLAY_SOURCE_EVENT_SCHEMA")
    views=tuple(tuple(v) for v in record["views"])
    post=tuple(record["post"])
    return (
        record["identifier"],views,record["first"],record["state"],
        record["second"],record["reward"],post,
    )

def load_pinned_cap01(raw,expected_sha):
    require_compat(type(raw) is bytes and expected_sha in PINNED_ORIGINALS
                   and digest(raw)==expected_sha and
                   0<len(raw)<=MAX_CHECKPOINT_BYTES,
                   "ONLY_PUBLISHED_SOURCE_SHA256")
    d=json.loads(raw.decode("ascii"))
    require_compat(type(d) is dict and set(d)=={
        "schema","archive_sha256","archive_ascii","original_count",
        "total_count","segments","events","offsets","one","temporal","future",
    } and d["schema"]==CAP01_SCHEMA and canonical(d)==raw,
        "ORIGINAL_CANONICAL_SCHEMA")
    require_compat(d["original_count"] in (1022,997) and
                   d["total_count"]==d["original_count"]+32 and
                   len(d["events"])==32 and len(d["segments"])==1,
                   "ORIGINAL_32_WITNESSES")
    archive=d["archive_ascii"].encode("ascii")
    source=NativeFutureStateLearner.restore(archive,d["archive_sha256"])
    independent=SegmentedNativeJEPA.from_archive(
        archive,d["archive_sha256"])
    for record in d["events"]:
        e=_public_event(record)
        independent=independent.observe(e[0],e[1],{
            "s1":e[1][0][0],"x1":e[2],"s2":e[3],
            "x2":e[4],"y":e[5],
        },e[6])
    measured=compare(d,json.loads(independent.checkpoint()))
    # Source-only re-execution tolerances do not change any saved weights.
    new_shards=[]
    for entry in d["segments"]:
        require_compat(type(entry) is dict and
                       set(entry)=={"sha256","ascii"},
                       "SEGMENT_CUSTODY_FIELDS")
        nested=entry["ascii"].encode("ascii")
        new_shards.append(NativeEpisodeExperience.restore(
            nested,entry["sha256"]))
    one=(
        ActionLatentSpecialist.from_data(d["one"][0],"transition"),
        ActionLatentSpecialist.from_data(d["one"][1],"reward"),
    )
    temporal=(
        TemporalLatentSpecialist.from_data(d["temporal"][0],"transition"),
        TemporalLatentSpecialist.from_data(d["temporal"][1],"reward"),
    )
    future=tuple(FutureStateHead.restore(v) for v in d["future"])
    offsets=tuple(tuple(x) for x in d["offsets"])
    events=tuple(_public_event(item) for item in d["events"])
    original=SegmentedNativeJEPA(
        archive,source,tuple(new_shards),events,one,temporal,future,offsets)
    require_compat(original._validate_custody() and
                   original.checkpoint()==raw,
                   "EXACT_ORIGINAL_STORED_PARAMETERS")
    return original,measured
