"""Read-only WSP102 capacity experiment: direct numeric write of real TRAIN triples.

This packs known Wikidata-derived Q/P/Q statements into fixed-endian numeric
slots. It does NOT infer unseen facts or constitute scientific generalization.
NEVER opens the public benchmark validation/test members.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import struct
import tarfile
import tempfile
import time
from source_custody import _download_once, inspect_members

ARCHIVE_SHA="ccda8bbcd3cf599b30dd3fd8979ac26e59b48fc53d23128882a044bfbb67f878"
ARCHIVE_BYTES=174515774
TRAIN_SHA="2ef1a279f6393a8edfbb2b44114a2c97944272e5fe2a1bd2a7cbe48f94742f1a"
TRAIN_BYTES=436189882
TRAIN_ROWS=21343681
TRAIN_RELATIONS=828
WEIGHT_BYTES=256124172
MAX_WEIGHT_BYTES=600000000
MAX_SECONDS=600
PACK=struct.Struct("<III")
assert PACK.size==12 and TRAIN_ROWS*PACK.size==WEIGHT_BYTES


def _positive_id(value, prefix):
    if (value[:1]!=prefix or len(value)<2 or not value[1:].isdigit()
            or value[1:2]==b"0"):
        raise ValueError("source is not strict Q/P/Q triple")
    number=int(value[1:])
    if number<=0 or number>4294967295:
        raise ValueError("ID outside unsigned numeric weight range")
    return number


def pack_train_source(handle, *, expected_rows=TRAIN_ROWS,
                      expected_bytes=TRAIN_BYTES, expected_sha=TRAIN_SHA,
                      expected_relations=TRAIN_RELATIONS,
                      max_weight_bytes=MAX_WEIGHT_BYTES,
                      max_seconds=MAX_SECONDS):
    """One pass; halfway cold restore, then append remaining original records."""
    begin=time.monotonic()
    begin_cpu=time.process_time()
    packed=bytearray()
    source_hash=hashlib.sha256()
    count=0
    byte_count=0
    relation_ids=set()
    cold_hash=None
    cold_bytes=None
    halfway=expected_rows//2
    cold_cpu=None
    with tempfile.TemporaryDirectory(prefix="wsp102-cold-numeric-") as d:
        cold=Path(d)/"half_numeric_weights.bin"
        for raw in handle:
            if time.monotonic()-begin>max_seconds:
                raise TimeoutError("large real graph numeric-write budget exceeded")
            count+=1
            byte_count+=len(raw)
            if count>expected_rows or byte_count>expected_bytes:
                raise ValueError("original training source row/byte drift")
            if b"\x00" in raw or len(raw)>10000:
                raise ValueError("invalid source statement line")
            cols=raw.rstrip(b"\r\n").split(b"\t")
            if len(cols)!=3:
                raise ValueError("source not a QID/PID/QID triple")
            subject=_positive_id(cols[0],b"Q")
            predicate=_positive_id(cols[1],b"P")
            target=_positive_id(cols[2],b"Q")
            relation_ids.add(predicate)
            source_hash.update(raw)
            packed.extend(PACK.pack(subject,predicate,target))
            if len(packed)>max_weight_bytes:
                raise MemoryError("numeric weight byte capacity exceeded")
            if count==halfway:
                t0=time.process_time()
                cold_hash=hashlib.sha256(packed).hexdigest()
                cold_bytes=len(packed)
                cold.write_bytes(packed)
                del packed
                packed=bytearray(cold.read_bytes())
                if len(packed)!=cold_bytes or hashlib.sha256(packed).hexdigest()!=cold_hash:
                    raise AssertionError("exact halfway numeric cold restoration failed")
                cold_cpu=time.process_time()-t0

        if count!=expected_rows or byte_count!=expected_bytes:
            raise ValueError("real KG source fact inventory does not match frozen variant")
        if source_hash.hexdigest()!=expected_sha:
            raise ValueError("train source bytes differ from verified source SHA")
        if len(relation_ids)!=expected_relations:
            raise ValueError("relation breadth differs from frozen actual data")
        if len(packed)!=expected_rows*PACK.size:
            raise AssertionError("numeric slot count incorrect")
        if cold_hash is None or cold_bytes is None:
            raise AssertionError("halfway cold restoration missing")
        if hashlib.sha256(memoryview(packed)[:cold_bytes]).hexdigest()!=cold_hash:
            raise AssertionError("previously stored first-half weights changed")
        packed_hash=hashlib.sha256(packed).hexdigest()
        return {
            "classification":"REAL_KG_LITERAL_NUMERIC_CAPACITY_ONLY",
            "actual_train_facts_written":count,
            "observed_relations":len(relation_ids),
            "numeric_weight_slots":count*3,
            "numeric_weight_bytes":len(packed),
            "source_uncompressed_bytes":byte_count,
            "source_sha256":source_hash.hexdigest(),
            "packed_numeric_sha256":packed_hash,
            "half_cold_image_bytes":cold_bytes,
            "half_cold_image_sha256":cold_hash,
            "half_restore_cpu_seconds":cold_cpu,
            "source_to_weights_cpu_seconds":time.process_time()-begin_cpu,
            "source_to_weights_wall_seconds":time.monotonic()-begin,
            "heldout_truth_read":False,
            "novel_facts_inferred":0,
            "scientific_superiority":False
        }


def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--train-only-full-numeric-capacity",action="store_true",required=True)
    ap.parse_args()
    with tempfile.TemporaryDirectory(prefix="wsp102-real-width-") as directory:
        local=Path(directory)/"wikidata5m.tar.gz"
        start=time.monotonic()
        received=_download_once(local)
        if received["compressed_sha256"]!=ARCHIVE_SHA or received["compressed_bytes"]!=ARCHIVE_BYTES:
            raise ValueError("training source archive provenance changed")
        members=inspect_members(local)
        actual={(m["path"],m["type"],m["uncompressed_bytes"]) for m in members["members"]}
        frozen={
            ("wikidata5m/valid.txt","file",109498),
            ("wikidata5m","directory",0),
            ("wikidata5m/train.txt","file",436189882),
            ("wikidata5m/test.txt","file",108932)
        }
        if actual!=frozen:
            raise ValueError("archive train/heldout member seal mismatch")
        with tarfile.open(local,mode="r:gz") as archive:
            member=archive.getmember("wikidata5m/train.txt")
            source=archive.extractfile(member)
            if source is None:
                raise ValueError("no training-only member")
            with source:
                result=pack_train_source(source)
        report={
            "schema":"wsp102.real-kg-numeric-capacity.v1",
            "historical_variant_source":True,
            "source_archive_sha256":ARCHIVE_SHA,
            "source_versioned_count_run":43627376935,
            "source_metadata_only_initial_run":43626313760,
            "original_wsp101_reserved_used":False,
            "validation_test_used":False,
            "full_process_wall_seconds":time.monotonic()-start,
            **result
        }
        print("WSP102_FULL_REAL_NUMERIC_WRITE="+json.dumps(
            report,sort_keys=True,separators=(",",":")),flush=True)


if __name__=="__main__":
    main()
