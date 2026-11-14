"""WSP-102: bounded full-training-graph structural audit after source seal.

Reads only the exact SHA-pinned train.txt member; NEVER opens the official
valid.txt or test.txt as graph records. No training, model weights or scoring.
"""
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import time

from source_custody import _download_once, inspect_members

SEALED_SOURCE_SHA256 = "ccda8bbcd3cf599b30dd3fd8979ac26e59b48fc53d23128882a044bfbb67f878"
SEALED_BYTES = 174515774
TRAIN_MEMBER = "wikidata5m/train.txt"
TRAIN_BYTES = 436189882
EXPECTED_LINES = 20614279
EXPECTED_PROPERTY_TYPES = 822
MAX_QID = 250000000
MAX_SECONDS = 600
SCHEMA = "wsp102.real-kg-train-source-audit.v1"


def _parse_id(data, letter):
    if (not data or data[:1] != letter or len(data) == 1
            or not data[1:].isdigit() or data[1:2] == b"0"):
        raise ValueError("invalid structured QID/PID")
    return int(data[1:])


def count_train_rows(handle, *, expected_lines=EXPECTED_LINES,
                     expected_bytes=TRAIN_BYTES, max_seconds=MAX_SECONDS):
    """Consumes only training file stream, not file arrays or target labels."""
    started = time.monotonic()
    cpu_started = time.process_time()
    byte_count=0
    count=0
    digest=hashlib.sha256()
    property_counts={}
    seen = bytearray()
    unique_entities = 0
    max_qid = 0
    self_edges = 0

    def mark_entity(qid):
        nonlocal unique_entities, max_qid
        if qid > MAX_QID:
            raise ValueError("unexpected unsafe QID range")
        if qid > max_qid:
            max_qid = qid
        slot = qid >> 3
        if slot >= len(seen):
            seen.extend(b"\x00" * (slot + 1 - len(seen)))
        flag = 1 << (qid & 7)
        if not (seen[slot] & flag):
            seen[slot] |= flag
            unique_entities += 1

    for raw in handle:
        if time.monotonic() - started > max_seconds:
            raise TimeoutError("source-only broad train scan exceeded budget")
        byte_count += len(raw)
        if byte_count > expected_bytes:
            raise ValueError("training file exceeds frozen byte size")
        count += 1
        if count > expected_lines:
            raise ValueError("more source rows than frozen published budget")
        digest.update(raw)
        if b"\x00" in raw or len(raw) > 10000:
            raise ValueError("malformed training relation line")
        cells = raw.rstrip(b"\r\n").split(b"\t")
        if len(cells) != 3:
            raise ValueError("unexpected triple columns")
        subject=_parse_id(cells[0],b"Q")
        predicate=_parse_id(cells[1],b"P")
        obj=_parse_id(cells[2],b"Q")
        property_counts[predicate] = property_counts.get(predicate, 0) + 1
        mark_entity(subject)
        mark_entity(obj)
        if subject == obj:
            self_edges += 1

    if byte_count != expected_bytes or count != expected_lines:
        raise ValueError("source size or line count differs from sealed dataset")
    if expected_lines == EXPECTED_LINES and len(property_counts) != EXPECTED_PROPERTY_TYPES:
        raise ValueError("observed relation breadth differs from precommitted benchmark")
    return {
        "classification":"TRAIN_ONLY_STRUCTURAL_AUDIT_NOT_SCIENCE",
        "train_sha256":digest.hexdigest(),
        "train_lines":count,
        "train_uncompressed_bytes":byte_count,
        "relation_types":len(property_counts),
        "unique_entity_ids_in_train":unique_entities,
        "max_entity_qid":max_qid,
        "self_relation_edges":self_edges,
        "ten_most_common_property_ids":[
            {"property":"P"+str(k),"train_edges":v}
            for k,v in sorted(property_counts.items(),key=lambda x:(-x[1],x[0]))[:10]
        ],
        "scan_wall_seconds":time.monotonic()-started,
        "scan_cpu_seconds":time.process_time()-cpu_started,
        "heldout_rows_read":0,
        "models_trained":0
    }


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--full-source-audit",action="store_true",required=True)
    parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="wsp102-trainonly-") as d:
        local=Path(d)/"source.tar.gz"
        meta=_download_once(local)
        if meta["compressed_sha256"] != SEALED_SOURCE_SHA256 or meta["compressed_bytes"] != SEALED_BYTES:
            raise ValueError("Wikidata5M archive changed from frozen provenance; refuse all graph rows")
        listing=inspect_members(local)
        names={(x["path"],x["type"],x["uncompressed_bytes"])
               for x in listing["members"]}
        expected={
            ("wikidata5m/valid.txt","file",109498),
            ("wikidata5m","directory",0),
            ("wikidata5m/train.txt","file",436189882),
            ("wikidata5m/test.txt","file",108932),
        }
        if names != expected:
            raise ValueError("archive member allowlist deviates from source seal")
        with tarfile.open(local,mode="r:gz") as archive:
            entry=archive.getmember(TRAIN_MEMBER)
            source=archive.extractfile(entry)
            if source is None:
                raise ValueError("sealed train source is not a readable regular file")
            with source:
                audit=count_train_rows(source)
        print("WSP102_TRAIN_SOURCE_AUDIT="+json.dumps({
            "schema":SCHEMA,
            "archive_sha256":SEALED_SOURCE_SHA256,
            "source_custody_run_id":43626313760,
            "independent_heldout_use":False,
            "original_wsp101_cohort_use":False,
            "scientific_superiority":False,
            **audit,
        },sort_keys=True,separators=(",",":")),flush=True)


if __name__=="__main__":
    main()
