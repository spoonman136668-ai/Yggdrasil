"""Optional owner-supplied native checkpoint continuation receipt verifier.

No automatic owner path discovery, network access, training, runner dispatch,
credentials, source first-use, accepted-state writes or model imports.
Passing this untrusted receipt integrity check NEVER proves owner authority,
native learning, authentic source, scientific acceptance, or deployment.

Call only with an explicitly owner-authorized bundle directory containing
the receipt and seven read-only files; fixture tests use synthetic bytes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat

SCHEMA="yggdrasil.owner.continuation-receipt-candidate.v1"
SHA256=re.compile(r"^[0-9a-f]{64}$")
PINNED_OWNER_BRANCH="research/autonomy-yggdrasil-active"
PINNED_OWNER_SHA="92c421a5475a27015a390efb88c373eb5f15379d"
PINNED_OWNER_TREE="e7a9cef8a7c31fd77f086915bab7c639411ac6cc"
MAX_FILE=536870912
ROLES=(
  "prior_checkpoint",
  "continued_checkpoint",
  "cold_restored_checkpoint",
  "prior_source_log",
  "continued_source_log",
  "prior_capability_probe",
  "continued_prior_capability_probe",
)
class IntakeError(ValueError):pass

def require(flag,code):
    if not flag: raise IntakeError("YGG_OWNER_INTAKE_"+code)

def parse_unique_json(raw):
    def no_duplicate(pairs):
        data={}
        for k,v in pairs:
            if k in data:raise IntakeError("YGG_OWNER_INTAKE_DUPLICATE_JSON_KEY")
            data[k]=v
        return data
    try:return json.loads(raw,object_pairs_hook=no_duplicate,
                          parse_constant=lambda _: (_ for _ in ()).throw(IntakeError("YGG_OWNER_INTAKE_NONFINITE")))
    except (json.JSONDecodeError,UnicodeError) as e:
        raise IntakeError("YGG_OWNER_INTAKE_RECEIPT_JSON") from e

def safe_input_file(path,base):
    # User chooses the bundle; the verifier does not select an owner directory.
    p=base/path
    require(type(path) is str and path in ROLES,"ROLE_FILE_NAME")
    require(not p.is_symlink(),"SYMLINK_REJECTED")
    try:
        st=p.lstat()
    except OSError as e:
        raise IntakeError("YGG_OWNER_INTAKE_FILE_UNAVAILABLE") from e
    require(stat.S_ISREG(st.st_mode),"NONREGULAR_FILE")
    require(0<st.st_size<=MAX_FILE,"RESOURCE_FILE_BOUND")
    return p,st.st_size

def sha_file(path,limit=None):
    sha=hashlib.sha256();count=0
    with path.open("rb") as stream:
        while True:
            chunk=stream.read(1024*1024)
            if not chunk:break
            count+=len(chunk)
            require(count<=MAX_FILE,"RESOURCE_FILE_BOUND")
            if limit is not None:require(count<=limit,"SOURCE_PREFIX_EXCESS")
            sha.update(chunk)
    return sha.hexdigest(),count

def exact_old_prefix(prior,new):
    with prior.open("rb") as old,new.open("rb") as current:
        while True:
            a=old.read(1024*1024)
            if not a:return True
            if current.read(len(a))!=a:return False

def verify_bundle(bundle):
    root=Path(bundle)
    require(not root.is_symlink(),"BUNDLE_SYMLINK")
    require(root.is_dir(),"BUNDLE_NOT_DIRECTORY")
    manifest=root/"receipt.json"
    require(not manifest.is_symlink(),"RECEIPT_SYMLINK")
    try:
        require(manifest.stat().st_size<=65536,"RECEIPT_SIZE")
        payload=parse_unique_json(manifest.read_bytes().decode("utf-8"))
    except (OSError,UnicodeError) as e:
        raise IntakeError("YGG_OWNER_INTAKE_RECEIPT_READ") from e
    require(type(payload) is dict,"RECEIPT_ROOT")
    require(set(payload)=={
       "schema","source","scope","checkpoint_schema","lineage","files",
       "old_ledger_entries","new_ledger_entries","external_owner_acceptance"
    },"RECEIPT_KEYS")
    require(payload["schema"]==SCHEMA,"SCHEMA")
    require(payload["scope"]=="research-only-candidate-integrity","NO_ACCEPTANCE_AUTHORITY")
    require(payload["external_owner_acceptance"] is None,"UNTRUSTED_ACCEPTANCE")
    require(type(payload["checkpoint_schema"]) is str and
            0<len(payload["checkpoint_schema"])<=128,"MODEL_SCHEMA")
    source=payload["source"]
    require(type(source) is dict and
            source=={"repo":"spoonman136668-ai/Yggdrasil",
                     "branch":PINNED_OWNER_BRANCH,
                     "git_sha":PINNED_OWNER_SHA,
                     "tree_sha":PINNED_OWNER_TREE},"SOURCE_NOT_PINNED")
    require(type(payload["files"]) is dict and set(payload["files"])==set(ROLES),"ROLES")
    lineage=payload["lineage"]
    require(type(lineage) is dict and set(lineage)=={"parent_checkpoint_sha256","continued_checkpoint_sha256",
                  "original_source_log_sha256","continued_source_log_sha256"},"LINEAGE_KEYS")
    for key,val in lineage.items():
        require(type(val) is str and SHA256.fullmatch(val),"LINEAGE_HASH")
    files={}
    for role in ROLES:
        row=payload["files"][role]
        require(type(row) is dict and set(row)=={"bytes","sha256"},"FILE_ENTRY")
        require(type(row["bytes"]) is int and 0<row["bytes"]<=MAX_FILE,"FILE_BYTES")
        require(type(row["sha256"]) is str and SHA256.fullmatch(row["sha256"]),"FILE_SHA")
        path,size=safe_input_file(role,root)
        require(size==row["bytes"],"FILE_SIZE_"+role.upper())
        digest,actual_size=sha_file(path)
        require(digest==row["sha256"] and actual_size==size,"FILE_HASH_"+role.upper())
        files[role]=path
    require(lineage["parent_checkpoint_sha256"]==payload["files"]["prior_checkpoint"]["sha256"],
            "PARENT_HASH")
    require(lineage["continued_checkpoint_sha256"]==payload["files"]["continued_checkpoint"]["sha256"],
            "NEW_HASH")
    require(lineage["original_source_log_sha256"]==payload["files"]["prior_source_log"]["sha256"],
            "PRIOR_LOG_HASH")
    require(lineage["continued_source_log_sha256"]==payload["files"]["continued_source_log"]["sha256"],
            "CONTINUED_LOG_HASH")
    require(lineage["parent_checkpoint_sha256"]!=lineage["continued_checkpoint_sha256"],
            "NO_CHANGED_STATE_WITNESS")
    require(payload["files"]["continued_checkpoint"]["sha256"]==
            payload["files"]["cold_restored_checkpoint"]["sha256"],
            "COLD_RESTORE_NOT_IDENTICAL")
    require(payload["files"]["prior_capability_probe"]["sha256"]==
            payload["files"]["continued_prior_capability_probe"]["sha256"],
            "PREVIOUS_CAPABILITY_PROBE_DRIFT")
    require(payload["files"]["continued_source_log"]["bytes"]>
            payload["files"]["prior_source_log"]["bytes"],"LOG_NOT_EXTENDED")
    require(exact_old_prefix(files["prior_source_log"],files["continued_source_log"]),
            "SOURCE_HISTORY_NOT_PREFIX")
    old_n=payload["old_ledger_entries"]
    new_n=payload["new_ledger_entries"]
    require(type(old_n) is int and type(new_n) is int and 0<=old_n<new_n<=100000000,
            "LEDGER_ENTRY_COUNT_CLAIM")
    return {
        "schema":"yggdrasil.owner.continuation-intake-classification.v1",
        "status":"INTEGRITY_CONSISTENT_BUT_UNTRUSTED",
        "source_git_sha":PINNED_OWNER_SHA,
        "source_git_tree":PINNED_OWNER_TREE,
        "checkpoint_sha256":lineage["continued_checkpoint_sha256"],
        "parent_checkpoint_sha256":lineage["parent_checkpoint_sha256"],
        "sha256_checked_roles":len(ROLES),
        "prior_source_log_byte_prefix_exact":True,
        "cold_restored_checkpoint_byte_hash_equal":True,
        "old_probe_output_byte_hash_equal":True,
        "ledger_entry_counts_verified_against_event_parser":False,
        "owner_authority":"UNVERIFIED",
        "training_source_authenticity":"UNVERIFIED",
        "native_learning_efficacy":"UNVERIFIED",
        "independent_science":"UNVERIFIED",
        "accepted_owner_state":"UNVERIFIED",
        "deployment":"NONE",
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--bundle",required=True,help="Explicit separately authorized directory; read-only")
    args=ap.parse_args()
    print("YGG_OWNER_RECEIPT_INTAKE="+json.dumps(verify_bundle(args.bundle),sort_keys=True,separators=(",",":")))

if __name__=="__main__":main()
