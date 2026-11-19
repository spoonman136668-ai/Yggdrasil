"""WSP188: ORIGINAL physical light-tunnel data count/header audit, zero training.

Source metadata only; reuses independently qualified WSP185 roster_entry.
No sensor target values are parsed, scored, trained or emitted.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent/"WSP-185"))
from roster_probe import roster_entry  # proven count+field+hash-only parser

MD5="dcad019186661a56de7a2d1db97fc2f0"
SCHEMA="yggdrasil.wsp188.light-physical-roster.v1"
ROSTER=("actuators_white","color_mix","smooth_polarizers")
REQUIRED=("red","green","blue","pol_1","pol_2",
          "l_31","l_32","vis_1","vis_2","vis_3")
LIMIT_BYTES=180_000_000
LIMIT_EXPANDED=350_000_000


def diagnose(path:Path):
    if not path.is_file() or not 0<path.stat().st_size<=LIMIT_BYTES:
        raise ValueError("WSP188_ARCHIVE_BYTES")
    raw=path.read_bytes()
    md5=hashlib.md5(raw).hexdigest()
    if md5!=MD5:
        raise ValueError("WSP188_PUBLISHED_SOURCE_HASH")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        selected={}
        expanded=0
        for item in z.infolist():
            name=PurePosixPath(item.filename)
            if name.is_absolute() or ".." in name.parts:
                raise ValueError("WSP188_ARCHIVE_PATH")
            expanded+=item.file_size
            if expanded>LIMIT_EXPANDED:
                raise ValueError("WSP188_EXPANSION_BUDGET")
            if item.is_dir() or name.stem not in ROSTER:
                continue
            if name.suffix!=".csv" or name.stem in selected:
                raise ValueError("WSP188_SOURCE_COLLISION")
            selected[name.stem]=item
        if set(selected)!=set(ROSTER):
            raise ValueError("WSP188_SOURCE_MISSING")
        entries={}
        for name in ROSTER:
            m=roster_entry(z,selected[name])
            entries[name]={
                "source_file_sha256":m["file_sha256"],
                "physical_rows":m["physical_record_count"],
                "empty_records":m["empty_csv_records"],
                "malformed_records":m["wrong_width_records"],
                "field_count":m["field_count"],
                "original_headers":m["header_fields"],
                "light_fields_missing":sorted(set(REQUIRED)-set(m["header_fields"])),
                "original_preregistered_10000_rows":m["physical_record_count"]==10000
            }
    return {
        "schema":SCHEMA,"source":"juangamella/causal-chamber@967d59a42956872f37463cc561ecf6e9ceab9364",
        "dataset":"lt_walks_v1","author_zip_md5":md5,
        "archive_sha256":hashlib.sha256(raw).hexdigest(),
        "protocol_commit":"56c73b5220f22e9ff6887bb5dea70ab75af8d98d",
        "metadata_only":True,"new_original_actions":0,
        "trained_models":0,"scientific_pass":False,
        "wsp187_frozen_source_admission_failure_preserved":True,
        "files":entries
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True,type=Path)
    a=p.parse_args()
    print("WSP188_ORIGINAL_LIGHT_METADATA="+json.dumps(
        diagnose(a.archive),sort_keys=True,separators=(",",":"),allow_nan=False))


if __name__=="__main__":
    main()
