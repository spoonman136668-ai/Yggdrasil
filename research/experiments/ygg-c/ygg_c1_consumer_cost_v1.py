#!/usr/bin/env python3
import ctypes, hashlib, json, os, platform, sys, time
from ctypes import wintypes
from pathlib import Path

import torch
import lu2v_task4_independent_confirmation_v1 as lu2v

PREREG="fa1b88d0e6e4b9605d113a719742f75b01f2ceb1"
LU2VF1="e832853554e813db2e185d6b607543541f32d887"
SCALES=(1,2,4,8,10)

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def peak_rss_bytes():
    if os.name!="nt":
        return None
    class PMC(ctypes.Structure):
        _fields_=[
            ("cb",wintypes.DWORD),("PageFaultCount",wintypes.DWORD),
            ("PeakWorkingSetSize",ctypes.c_size_t),("WorkingSetSize",ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage",ctypes.c_size_t),("QuotaPagedPoolUsage",ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage",ctypes.c_size_t),("QuotaNonPagedPoolUsage",ctypes.c_size_t),
            ("PagefileUsage",ctypes.c_size_t),("PeakPagefileUsage",ctypes.c_size_t)
        ]
    pmc=PMC(); pmc.cb=ctypes.sizeof(PMC)
    kernel32=ctypes.WinDLL("kernel32",use_last_error=True)
    psapi=ctypes.WinDLL("psapi",use_last_error=True)
    kernel32.GetCurrentProcess.argtypes=[]
    kernel32.GetCurrentProcess.restype=wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(PMC),wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype=wintypes.BOOL
    handle=kernel32.GetCurrentProcess()
    ok=psapi.GetProcessMemoryInfo(handle,ctypes.byref(pmc),pmc.cb)
    return int(pmc.PeakWorkingSetSize) if ok else None

def gpu_state(reset=False):
    available=bool(torch.cuda.is_available())
    if reset and available:
        torch.cuda.reset_peak_memory_stats()
    return {
        "available":available,
        "device":torch.cuda.get_device_name(0) if available else None,
        "allocated":int(torch.cuda.max_memory_allocated()) if available else None,
        "reserved":int(torch.cuda.max_memory_reserved()) if available else None,
    }

def run_n(manifests,n):
    rows=[]
    t0=time.perf_counter()
    for m in manifests[:n]:
        rows.append(lu2v.run_pair(m))
    dt=time.perf_counter()-t0
    evidence=hashlib.sha256(canonical(rows)).hexdigest()
    return {"worlds":n,"seconds":dt,"seconds_per_world":dt/n,"evidence_sha256":evidence,
            "peak_rss_bytes":peak_rss_bytes(),"cuda":gpu_state(False)}

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    source=Path(lu2v.__file__).read_bytes()
    manifests=lu2v.primary_manifests(LU2VF1)

    # Unscored warm-up.
    _=lu2v.run_pair(lu2v.mechanical_manifest())

    passes=[]
    for pass_id in (1,2):
        gpu_state(True)
        rows=[run_n(manifests,n) for n in SCALES]
        passes.append({"pass":pass_id,"rows":rows})

    out={
      "schema":1,
      "experiment":"YGG-C1",
      "prereg":PREREG,
      "shared_baseline":"878464cf84833d06a1ac7e45988bfb79608547dc",
      "lu2vf1":LU2VF1,
      "environment":{
        "python":sys.version,
        "platform":platform.platform(),
        "torch":torch.__version__,
        "cuda_runtime":torch.version.cuda,
        "cuda_available":bool(torch.cuda.is_available()),
        "cuda_device":torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "cpu_count":os.cpu_count(),
      },
      "source_sha256":hashlib.sha256(source).hexdigest(),
      "passes":passes
    }
    out["evidence_sha256"]=hashlib.sha256(canonical(out)).hexdigest()
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
