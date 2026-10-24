"""MR34J3D single-use ORIGINAL MiniGrid public-scaffold development preflight.

Not a scientific experiment, a queue, a workflow, or execution authority.
This module is inert when imported; only a separately authorized CKB-plane
source-custodian may invoke the original-environment CLI path after approval.
Do not invoke the original-source path from ChatGPT or an unqualified runner.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.metadata
import io
import json
from pathlib import Path
import subprocess

from public_scaffold import PublicOnlyNavigation, PublicView, ProtocolBlocked
from online import PublicRuleSession

UPSTREAM = "7f5853792ea7f04f75614661006d87fcf949f26d"
SOURCE_BLOBS = {
    "minigrid/envs/memory.py": "660b0a1b769948034c87bb421759c2b9a4f24548",
    "minigrid/__init__.py": "41b4a731255d19bdf61072b7100e752a759a3ae4",
    "minigrid/minigrid_env.py": "eb29e9a902de0715ab77ec981a2113576d7664fa",
}
SOURCE_ID = "MiniGrid-MemoryS7-v0"
SEEDS = tuple(3_000_000 + i for i in range(16))


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args],
                          check=True, capture_output=True, text=True).stdout.strip()


def verify_checkout(root: Path) -> dict:
    """Read only: exact commit, clean source and immutable source blob OIDs."""
    root = Path(root).resolve()
    if _git(root, "rev-parse", "HEAD") != UPSTREAM:
        raise ProtocolBlocked("UPSTREAM_GIT_SHA_MISMATCH")
    if _git(root, "status", "--porcelain", "--untracked-files=no"):
        raise ProtocolBlocked("UPSTREAM_TRACKED_DIRTY")
    for path, expected in SOURCE_BLOBS.items():
        if _git(root, "hash-object", path) != expected:
            raise ProtocolBlocked("UPSTREAM_SOURCE_BLOB_DRIFT:" + path)
    return {"source_commit": UPSTREAM, "source_blobs": SOURCE_BLOBS}


def encode_row(seed: int, step: int, before: PublicView, action: int,
               after: PublicView, reward: float, terminated: bool,
               truncated: bool, stage_event: str) -> bytes:
    """Original public images as bytes; no source-private fields or info dict."""
    row = {"seed":seed,"step":step,"before_image_hex":before.image_bytes.hex(),
           "before_direction":before.direction,"action":int(action),
           "after_image_hex":after.image_bytes.hex(),
           "after_direction":after.direction,"reward":float(reward),
           "terminated":bool(terminated),"truncated":bool(truncated),
           "public_stage_event":stage_event}
    return (json.dumps(row,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode("utf-8")


def deterministic_gzip(payload: bytes) -> bytes:
    bio=io.BytesIO()
    with gzip.GzipFile(fileobj=bio,mode="wb",filename="",mtime=0,compresslevel=6) as z:
        z.write(payload)
    if gzip.decompress(bio.getvalue()) != payload:
        raise ProtocolBlocked("LOSSLESS_TRACE_ROUNDTRIP_FAILED")
    return bio.getvalue()


def preflight_episode(gym, seed: int) -> dict:
    """Source-free fixture-tested kernel; only a qualified owner may connect a real gym.

    This helper is *not* itself the trusted original-source admission boundary.
    """
    if type(seed) is not int or seed not in SEEDS:
        raise ProtocolBlocked("PREFLIGHT_SEED_NOT_IN_PROPOSED_INVENTORY")
    nav=PublicOnlyNavigation()
    policy=PublicRuleSession()
    env=gym.make(SOURCE_ID)
    rows=[]; choice=None; saw_cue=False; saw_fork=False; reward=0.
    try:
        original_obs, _=env.reset(seed=seed)
        for step_index in range(1, 33):
            before=PublicView.from_observation(original_obs)
            proposed=nav.advance(original_obs)
            stage_event=proposed.event
            if proposed.event=="PUBLIC_CUE_EXPOSURE":
                policy.observe(before,proposed.event)
                saw_cue=True
            if proposed.event=="PUBLIC_FORK_OBJECT_EXPOSURE_AND_CHOICE":
                if choice is not None or not saw_cue:
                    raise ProtocolBlocked("INVALID_FORK_EXPOSURE_ORDER")
                policy.observe(before,proposed.event)
                saw_fork=True
                choice=policy.choose()
                nav.commit(choice)
                proposed=nav.advance(original_obs)
            if proposed.action not in (0,1,2):
                raise ProtocolBlocked("SOURCE_ACTION_MISSING_OR_ILLEGAL")
            after_obs, reward, terminated, truncated, _=env.step(proposed.action)
            after=PublicView.from_observation(after_obs)
            rows.append(encode_row(seed,step_index,before,proposed.action,after,
                                   reward,terminated,truncated,stage_event))
            original_obs=after_obs
            if terminated or truncated:
                if not(saw_cue and saw_fork and choice is not None
                       and terminated and not truncated and float(reward)>0.0):
                    raise ProtocolBlocked("ORIGINAL_PUBLIC_RULE_DID_NOT_SUCCEED")
                return {"seed":seed,"choice":choice,"source_steps":step_index,
                        "terminal_reward":float(reward),"cue_visible":saw_cue,
                        "fork_visible":saw_fork,"rows":rows}
        raise ProtocolBlocked("SCAFFOLD_NEVER_TERMINATED_IN_32_ACTIONS")
    except Exception as exc:
        # Include incomplete/current episode rows in the custody receipt too.
        # This records genuinely consumed original source without pretending PASS.
        exc.original_rows = tuple(rows)
        raise
    finally:
        env.close()


def require_owner_admission() -> None:
    """Fail closed: no authenticated CKB-plane trust root is installed here.

    A future authorized integration must *replace* this denial with verification
    of a signed, bound source lease and immutable attempt consumption. The
    untrusted CLI flags, environment variables, or files cannot grant admission.
    """
    raise ProtocolBlocked("CKB_OWNER_LEASE_VERIFIER_NOT_INSTALLED_NO_SOURCE_EXECUTION")


def collect_16_original(root: Path, output: Path) -> dict:
    """Disabled original-source collector pending qualified owner integration.

    This denial is before checkout, import, mkdir or env.reset/step.
    """
    require_owner_admission()
    source=verify_checkout(root)
    if output.exists():
        raise ProtocolBlocked("NO_OVERWRITE_OF_PRIOR_SOURCE_RECEIPTS")
    import minigrid
    import gymnasium as gym
    module_path=Path(minigrid.__file__).resolve()
    if module_path != (Path(root).resolve()/"minigrid"/"__init__.py"):
        raise ProtocolBlocked("PYTHON_MINIGRID_IMPORT_NOT_PINNED_SOURCE_TREE")
    deps={k:importlib.metadata.version(k) for k in ("numpy","gymnasium","minigrid")}
    output.mkdir(parents=True,exist_ok=False)
    all_rows=[]; episodes=[]; attempted_seeds=[]
    try:
        for seed in SEEDS:
            attempted_seeds.append(seed)
            episode=preflight_episode(gym,seed)
            all_rows.extend(episode.pop("rows"))
            episodes.append(episode)
        plaintext=b"".join(all_rows)
        compressed=deterministic_gzip(plaintext)
        trace_path=output/"original_public_preflight_16.jsonl.gz"
        trace_path.write_bytes(compressed)
        receipt={"schema":"mr34j3d.source-preflight-development.v1",
                 "status":"16_ORIGINAL_PUBLIC_PREFLIGHT_DEV_PASS_NOT_SCIENCE",
                 "scientific_acceptance":"NOT_AUTHORIZED",
                 "protected_first_use":"NONE",
                 "source":source,"environment_id":SOURCE_ID,
                 "installed_versions":deps,"original_seed_count":len(SEEDS),
                 "original_seeds":list(SEEDS),"episodes":episodes,
                 "trace_sha256":hashlib.sha256(plaintext).hexdigest(),
                 "trace_gzip_sha256":hashlib.sha256(compressed).hexdigest(),
                 "source_public_row_count":len(all_rows),
                 "note":"Source runtime and seed role eligibility require independent CKB-plane custody; this is only development feasibility."}
        (output/"receipt.json").write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        return receipt
    except Exception as exc:
        # Preserve even the incomplete/failed episode and its attempted seed;
        # these original-source resets may NEVER be misrepresented as unused.
        partial=b"".join(all_rows)+b"".join(getattr(exc,"original_rows",()))
        (output/"partial_original_public_evidence.jsonl.gz").write_bytes(deterministic_gzip(partial))
        (output/"BLOCKED.json").write_text(json.dumps({
            "status":"SOURCE_SCAFFOLD_BLOCKED_NOT_SCIENCE",
            "completed_seeds":[p["seed"] for p in episodes],
            "attempted_seeds":attempted_seeds,
            "reason":type(exc).__name__+":"+str(exc),
            "partial_public_row_count":len(partial.splitlines()),
            "source":source,"environment_id":SOURCE_ID},sort_keys=True,indent=2)+"\n")
        raise


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--inspect-spec-only",action="store_true")
    p.add_argument("--run-original-source",action="store_true")
    p.add_argument("--pinned-source-checkout",type=Path)
    p.add_argument("--output",type=Path)
    opts=p.parse_args()
    if opts.inspect_spec_only and not opts.run_original_source:
        print(json.dumps({"status":"STATIC_SPEC_ONLY_NO_ENV_IMPORT_OR_RESET",
                          "expected_commit":UPSTREAM,"source_blobs":SOURCE_BLOBS,
                          "environment_id":SOURCE_ID,"preflight_seeds":list(SEEDS)},sort_keys=True))
        return 0
    if opts.run_original_source and not opts.inspect_spec_only and opts.pinned_source_checkout and opts.output:
        # Always blocked in this candidate. CLI arguments never authenticate
        # an owner, and no CKB verifier/trust root is installed.
        print(json.dumps(collect_16_original(opts.pinned_source_checkout,opts.output),sort_keys=True))
        return 0
    p.error("Use --inspect-spec-only; original-source execution requires qualified external CKB-plane delegation.")
    return 2

if __name__=="__main__":
    raise SystemExit(main())
