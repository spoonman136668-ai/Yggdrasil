#!/usr/bin/env python3
"""F08 bounded published matrix-size/hash and artifact-license metadata preflight."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
import urllib.parse
import urllib.request

MODEL = "neuronpedia/icalens-qwen3.6-27b"
REV = "3e83450ee5d6cb172ae11f2da06500be326c16ad"
SUBDIR = "blocks.32.hook_resid_post"
NAME = SUBDIR + "/sae_weights.safetensors"
BASE = "https://huggingface.co/"
DIR = f"{BASE}api/models/{MODEL}/tree/{REV}/{SUBDIR}"
README = f"{BASE}{MODEL}/resolve/{REV}/README.md"
SIZE = 131_072
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class Invalid(ValueError):
    pass


def get(url):
    if url not in (DIR, README):
        raise Invalid("NON_PREREGISTERED_URL")
    with urllib.request.urlopen(urllib.request.Request(url, headers={
        "User-Agent":"qtr01-f08-fitted-layer-custody/1.0",
        "Accept":"application/json" if url == DIR else "text/plain"
    }), timeout=20) as response:
        body = response.read(SIZE + 1)
    if not 0 < len(body) <= SIZE:
        raise Invalid("SOURCE_BOUND")
    return body


def listed_matrix(raw):
    if not 0 < len(raw) <= SIZE:
        raise Invalid("SOURCE_BOUND")
    try:
        listing = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeError) as e:
        raise Invalid("DIRECTORY_NOT_JSON") from e
    if not isinstance(listing,list) or len(listing)>100:
        raise Invalid("BAD_DIRECTORY")
    for item in listing:
        if not isinstance(item,dict):
            raise Invalid("BAD_ENTRY")
        path=item.get("path")
        if path != NAME:
            continue
        size=item.get("size")
        lfs=item.get("lfs")
        oid=lfs.get("oid") if isinstance(lfs,dict) else None
        # HF API may expose an LFS oid either as bare hex or sha256:hex.
        digest=oid.removeprefix("sha256:") if isinstance(oid,str) else None
        if type(size) is not int or not 0<size<2_000_000_000:
            raise Invalid("INVALID_MATRIX_SIZE")
        if not isinstance(digest,str) or not SHA256.fullmatch(digest):
            raise Invalid("MISSING_PUBLISHED_MATRIX_LFS_HASH")
        return {"file":NAME,"bytes_listed":size,"published_lfs_sha256":digest,
                "sha256_independently_recomputed":False,
                "fitted_matrix_downloaded":False}
    raise Invalid("EXACT_MATRIX_NOT_LISTED")


def license_readme(raw):
    if not 0 < len(raw) <= SIZE:
        raise Invalid("SOURCE_BOUND")
    try:
        text=raw.decode("utf-8-sig")
    except UnicodeError as e:
        raise Invalid("README_NOT_UTF8") from e
    license_name=None
    if text.startswith("---\n"):
        end=text.find("\n---",4)
        if 0<end<8192:
            header=text[4:end]
            match=re.search(r"^license:\s*([A-Za-z0-9.-]+)\s*$",header,re.M)
            if match:
                license_name=match.group(1).lower()
    return {"artifact_repo_license_declaration":license_name or "UNVERIFIED",
            "readme_sha256":hashlib.sha256(raw).hexdigest(),
            "readme_bytes":len(raw),
            "separate_third_party_explanation_rights":"UNVERIFIED"}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--read-pinned-layer-metadata-only",action="store_true",required=True)
    parser.parse_args()
    try:
        matrix=listed_matrix(get(DIR))
        license_data=license_readme(get(README))
    except (Invalid,OSError,TimeoutError) as e:
        print("QTR01_F08_SOURCE_PRECHECK_BLOCKED: "+str(e),file=sys.stderr)
        return 2
    record={"schema":"yggdrasil.qtr01.f08.pinned-matrix-custody-metadata.v1",
            "repo":MODEL,"revision":REV,"matrix":matrix,"rights":license_data,
            "causal_feature_validated":False,"native_recipient_alignment_validated":False,
            "model_executed":False,"transplant_performed":False,
            "result":"PUBLISHED_MATRIX_CUSTODY_METADATA_AVAILABLE_ONLY"}
    print(json.dumps(record,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
