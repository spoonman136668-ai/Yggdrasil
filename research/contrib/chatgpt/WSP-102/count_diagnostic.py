"""Post-failure metadata-only source row-count reconciliation, NOT data science."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import tempfile
import time
from source_custody import _download_once, inspect_members

SEALED_SHA="ccda8bbcd3cf599b30dd3fd8979ac26e59b48fc53d23128882a044bfbb67f878"
SEALED_COMPRESSED_BYTES=174515774
TRAIN_MEMBER="wikidata5m/train.txt"
TRAIN_BYTES=436189882
PUBLISHED_ROWS=20614279
ROW_CAP=30000000
MAX_SCAN_SECONDS=600

def count_train_only(handle, *, expected_bytes=TRAIN_BYTES,
                     published_rows=PUBLISHED_ROWS, max_seconds=MAX_SCAN_SECONDS):
    start=time.monotonic()
    dig=hashlib.sha256()
    n=0
    consumed=0
    properties=set()
    for raw in handle:
        if time.monotonic()-start>max_seconds:
            raise TimeoutError("source metadata scan exceeded frozen time")
        n+=1
        consumed+=len(raw)
        if n>ROW_CAP or consumed>expected_bytes:
            raise ValueError("source metadata cap exceeded")
        if len(raw)>10000 or b"\x00" in raw:
            raise ValueError("malformed train source row")
        dig.update(raw)
        fields=raw.rstrip(b"\r\n").split(b"\t")
        if len(fields)!=3:
            raise ValueError("source row not three structured IDs")
        for field,typ in zip(fields,(b"Q",b"P",b"Q")):
            if (field[:1]!=typ or len(field)<2 or
                    not field[1:].isdigit() or int(field[1:])<=0):
                raise ValueError("malformed QID/PID/QID")
        properties.add(fields[1])
    if consumed!=expected_bytes:
        raise ValueError("source member raw-byte seal drift")
    return {
        "classification":"SOURCE_COUNT_AGREES_WITH_PUBLISHER"
        if n==published_rows else "SOURCE_PUBLISHED_COUNT_MISMATCH",
        "source_admitted_for_science":False,
        "observed_train_rows":n,
        "published_train_rows":published_rows,
        "row_count_equal":n==published_rows,
        "observed_relation_types":len(properties),
        "training_member_sha256":dig.hexdigest(),
        "source_member_bytes":consumed,
        "heldout_rows_read":0,
        "model_updates":0,
        "wall_seconds":time.monotonic()-start
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-count-diagnostic-only",action="store_true",required=True)
    parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="wsp102-countdiag-") as d:
        archive=Path(d)/"data.tar.gz"
        meta=_download_once(archive)
        if (meta["compressed_sha256"]!=SEALED_SHA or
                meta["compressed_bytes"]!=SEALED_COMPRESSED_BYTES):
            raise ValueError("source archive bytes no longer match frozen provenance")
        members=inspect_members(archive)
        expected={
            ("wikidata5m/valid.txt","file",109498),
            ("wikidata5m","directory",0),
            ("wikidata5m/train.txt","file",436189882),
            ("wikidata5m/test.txt","file",108932)
        }
        found={(m["path"],m["type"],m["uncompressed_bytes"])
               for m in members["members"]}
        if found!=expected:
            raise ValueError("archive members changed")
        with tarfile.open(archive,mode="r:gz") as tar:
            f=tar.extractfile(tar.getmember(TRAIN_MEMBER))
            if f is None:
                raise ValueError("no sealed train member")
            with f:
                report=count_train_only(f)
        print("WSP102_TRAIN_COUNT_DIAGNOSTIC="+json.dumps({
            "schema":"wsp102.train-count-diagnostic.v1",
            "original_count_failure_run":43626765368,
            "frozen_archive_sha256":SEALED_SHA,
            "trained_model":False,
            "scoring":False,
            **report
        },sort_keys=True,separators=(",",":")),flush=True)

if __name__=="__main__":
    main()
