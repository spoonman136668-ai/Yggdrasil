#!/usr/bin/env python3
"""NCI-SOURCE-07: inspect EXISTING archived Amalgam ZIP bytes; never run a learner/source.

Read only. No network, model imports, source execution, mutable checkpoints, or owner ops.
Both archived Linux/Windows sources are required and SHA-256 pinned by manifest.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile


def digest(x):
    return hashlib.sha256(x).hexdigest()


def insist(condition, message):
    if not condition:
        raise ValueError("NCI07_FAIL: " + message)


def unique_json(raw):
    def reject_duplicates(pairs):
        obj = {}
        for key, value in pairs:
            insist(key not in obj, "duplicate JSON key")
            obj[key] = value
        return obj
    return json.loads(raw, object_pairs_hook=reject_duplicates)


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def bit(value):
    return type(value) is int and value in (0, 1)


def verify_archive(zip_path, spec, manifest):
    raw = zip_path.read_bytes()
    insist(digest(raw) == spec["zip_sha256"], "outer artifact ZIP hash: " + spec["name"])
    with ZipFile(zip_path) as z:
        names = z.namelist()
        insist(len(names) == len(set(names)), "duplicate ZIP entry")
        insist(set(names) == set(manifest["archive_entries"]), "unexpected ZIP entry")
        for name in names:
            x = z.getinfo(name)
            insist(not x.is_dir() and not name.startswith("/") and ".." not in name.split("/"), "unsafe ZIP path")
        state_bytes = z.read("amalgam-joint-state.json")
        insist(len(state_bytes) == manifest["joint_state_bytes"], "joint state length")
        insist(digest(state_bytes) == spec["joint_sha256"], "joint state SHA-256")
        for entry in names:
            insist(len(z.read(entry)) <= manifest["max_entry_bytes"], "oversize ZIP member")
        joint = unique_json(state_bytes)
        native_bytes = joint["native_ascii"].encode("ascii")
        insist(digest(native_bytes) == manifest["native_sha256"], "native checkpoint SHA-256")
        insist(joint["schema"] == manifest["joint_schema"], "joint schema mismatch")
        insist(len(joint["action_heads"]) == len(joint["temporal_heads"]) == 2,
               "expected four specialist heads")
        native = unique_json(native_bytes)
        insist(native["schema"] == manifest["native_schema"], "native schema mismatch")
        insist(native["accepted_native"] is False and native["scientific_pass"] is False,
               "incorrect research/accepted status")
        episode_bytes = native["experience_ascii"].encode("ascii")
        insist(digest(episode_bytes) == manifest["episode_checkpoint_sha256"],
               "episode checkpoint SHA-256")
        experience = unique_json(episode_bytes)
        insist(experience["schema"] == manifest["episode_schema"], "episode schema mismatch")
        insist(experience["episode_limit"] == manifest["episode_limit"], "episode capacity drift")
        events = experience["episodes"]
        insist(type(events) is list and len(events) == manifest["episode_count"],
               "episode length drift")
        ids = set()
        mismatch_other = mismatch_primary = 0
        for index, event in enumerate(events):
            insist(type(event) is list and len(event) == 6, "episode width at " + str(index))
            identifier, views, x1, s2, x2, y = event
            insist(type(identifier) is str and len(identifier) == 64
                   and all(c in "0123456789abcdef" for c in identifier), "episode ID format")
            insist(identifier not in ids, "duplicate witnessed episode ID")
            ids.add(identifier)
            insist(type(views) is list and len(views) == 2
                   and all(type(v) is list and len(v) == 2 and all(bit(k) for k in v) for v in views),
                   "invalid paired views at " + str(index))
            insist(all(bit(v) for v in (x1, s2, x2, y)), "invalid action/outcome bit")
            mismatch_primary += views[0][0] != views[1][0]
            mismatch_other += views[0][1] != views[1][1]
        insist(mismatch_primary == 0, "reconstructed projection-0 historical view disagreement")
        # There is NO raw inbound s1 in archived events 0..1023. Do not infer it.
        last_id, last_views, x1, s2, x2, y = events[-1]
        reconstructed = {"s1": last_views[0][0], "x1": x1, "s2": s2, "x2": x2, "y": y}
        reconstructed_packet = canonical_json([last_id, last_views, reconstructed])
        insist(digest(reconstructed_packet) == manifest["one_original_public_packet_sha256"],
               "last originally sealed input packet differs from reconstructed row")
        altered = dict(reconstructed, s1=1-reconstructed["s1"])
        insist(digest(canonical_json([last_id, last_views, altered])) !=
               digest(reconstructed_packet), "mutated source row reused original packet hash")
        return {"archive_name": spec["name"], "artifact_id": spec["artifact_id"],
                "zip_sha256": digest(raw), "joint_sha256": digest(state_bytes),
                "native_sha256": digest(native_bytes),
                "episode_checkpoint_sha256": digest(episode_bytes),
                "events": len(events), "unique_event_ids": len(ids),
                "projection0_view_conflicts": mismatch_primary,
                "projection1_view_conflicts": mismatch_other,
                "last_packet_sha256": digest(reconstructed_packet),
                "full_joint_head_identity": "OS_DEPENDENT_NOT_COMPARABLE_AS_EQUAL"}, events


def run(linux, windows, manifest):
    data = unique_json(manifest.read_bytes())
    insist(data["schema"] == "nci-source07.archived-joint-custody.v1", "manifest schema")
    l, events_l = verify_archive(linux, data["artifacts"]["linux"], data)
    w, events_w = verify_archive(windows, data["artifacts"]["windows"], data)
    insist(events_l == events_w, "Linux/Windows native episodes diverged")
    insist(l["native_sha256"] == w["native_sha256"], "native state drift across OS")
    insist(l["joint_sha256"] != w["joint_sha256"], "unexpected joint-head identity")
    insist(l["last_packet_sha256"] == w["last_packet_sha256"], "new public packet drift")
    return {"schema":"nci-source07.result.v1",
            "classification":"ARCHIVED_RESEARCH_NATIVE_LEDGER_COMPATIBILITY_PASS",
            "sources": [l, w],
            "verified_episodes": len(events_l),
            "checked_historical_view0":len(events_l),
            "raw_inbound_s1_preserved_in_episode_ledger":False,
            "last_accepted_s1_reconstructible_from_external_pinned_packet":True,
            "historical_parent_original_raw_rows_authenticated":False,
            "first_use_actions":0,"model_imports":0,"model_training_steps":0,
            "owner_host_checkpoint_authenticated":False,
            "real_native_cold_restore_executed":False,
            "scientific_pass":False,"accepted_native":False,"deployment":"NONE"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--linux", required=True, type=Path)
    parser.add_argument("--windows", required=True, type=Path)
    parser.add_argument("--manifest", default=Path(__file__).with_name("manifest.json"), type=Path)
    p = parser.parse_args()
    try:
        print(json.dumps(run(p.linux, p.windows, p.manifest), sort_keys=True, indent=2))
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
