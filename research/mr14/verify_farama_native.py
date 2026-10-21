"""MR14: validate independently authored native source bytes and development transitions.

This is ONLY source intake + direct native runtime observation. It is not a
new Yggdrasil learner, new local-role mapping, hidden-task test, or scientific
first-use. Privileged world inspection is allowed ONLY in this evidence probe
and must never be passed into a candidate or its controls.
"""
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys


def checked_command(args, root):
    return subprocess.run(args, cwd=root, check=True, capture_output=True,
                          text=True, timeout=15).stdout.strip()


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--upstream", required=True)
    cli.add_argument("--manifest", default="research/mr14/farama_source_manifest.json")
    cli.add_argument("--native-probe", action="store_true")
    args = cli.parse_args()

    manifest = json.loads(pathlib.Path(args.manifest).read_text(encoding="utf-8"))
    assert manifest["schema"] == "yggdrasil.mr14.external-source-birth.v1"
    source = pathlib.Path(args.upstream).resolve()
    expected_commit = manifest["upstream_commit"]
    actual_commit = checked_command(["git", "rev-parse", "HEAD"], source)
    if actual_commit != expected_commit:
        raise ValueError("MR14_EXTERNAL_COMMIT_DRIFT")
    if checked_command(["git", "status", "--porcelain"], source):
        raise ValueError("MR14_EXTERNAL_CHECKOUT_NOT_CLEAN")
    exact_hashes = {}
    for path, blob in sorted(manifest["source_blobs"].items()):
        source_bytes = (source / path).read_bytes()
        git_blob = checked_command(["git", "rev-parse", "HEAD:" + path], source)
        if blob != git_blob:
            raise ValueError("MR14_EXTERNAL_GIT_BLOB_DRIFT: " + path)
        committed = subprocess.run(["git", "show", "HEAD:" + path],
                                   cwd=source, check=True, capture_output=True,
                                   timeout=15).stdout
        if committed != source_bytes:
            raise ValueError("MR14_EXTERNAL_SOURCE_CHECKOUT_DRIFT: " + path)
        exact_hashes[path] = hashlib.sha256(committed).hexdigest()

    license_text = (source / "LICENSE").read_text(encoding="utf-8-sig")
    metadata = (source / "pyproject.toml").read_text(encoding="utf-8-sig")
    root_apache = license_text.lstrip().startswith("Apache License")
    metadata_mit = 'license = { text = "MIT License" }' in metadata
    # Divergent licensing evidence is preserved as a blocking condition
    # rather than silently assuming which statement controls distribution.
    if not(root_apache and metadata_mit):
        raise ValueError("MR14_EXTERNAL_LICENSE_EVIDENCE_CHANGED")
    print("MR14_INDEPENDENT_SOURCE_BIRTH=" + json.dumps({
        "source_repo": manifest["upstream_repository"],
        "source_commit": actual_commit,
        "verified_blobs": len(exact_hashes),
        "sha256_of_blobs": exact_hashes,
        "source_author_independent": True,
        "root_license": "APACHE_2_TEXT",
        "packaging_license": "MIT_METADATA",
        "license_discrepancy_reconciled": False,
        "first_use": False,
        "model_training": False,
        "science_admission": "BLOCKED",
    },sort_keys=True))

    if not args.native_probe:
        return
    sys.path.insert(0,str(source))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.core.world_object import Door, Key, Goal

    native = DoorKeyEnv(size=5, render_mode=None)
    try:
        obs, _ = native.reset(seed=11)
        assert "image" in obs and "direction" in obs
        found_door = []
        found_key = []
        for x in range(native.width):
            for y in range(native.height):
                obj = native.grid.get(x,y)
                if isinstance(obj, Door): found_door.append((x,y,obj))
                if isinstance(obj, Key): found_key.append((x,y,obj))
        if len(found_door)!=1 or len(found_key)!=1:
            raise ValueError("MR14_ORIGINAL_GRID_OBJECT_INVENTORY_CHANGED")
        dx,dy,door = found_door[0]
        kx,ky,key = found_key[0]
        assert door.is_locked and not door.is_open and key.color == door.color

        # Manipulate ONLY the test probe's original environment positions;
        # no positions, object type IDs, or evaluator truth enter a learner.
        native.agent_pos = (dx-1,dy)
        native.agent_dir = 0  # face original door to its east
        before_door = (door.is_locked,door.is_open)
        native.step(native.actions.toggle)
        assert (door.is_locked,door.is_open)==before_door
        blocked_toggle = True

        # Find a valid adjacent original native tile to execute *pickup*.
        adj = [((kx-1,ky),0),((kx+1,ky),2),
               ((kx,ky-1),1),((kx,ky+1),3)]
        pickup = next((pos,face) for pos,face in adj
                      if 0 <= pos[0] < native.width and
                         0 <= pos[1] < native.height and
                         native.grid.get(*pos) is None)
        native.agent_pos, native.agent_dir = pickup
        native.step(native.actions.pickup)
        assert isinstance(native.carrying,Key)
        assert native.grid.get(kx,ky) is None
        native.agent_pos = (dx-1,dy)
        native.agent_dir = 0
        native.step(native.actions.toggle)
        assert door.is_open and not door.is_locked
        native.step(native.actions.forward)
        assert tuple(native.agent_pos)==(dx,dy)
        # Execute native terminal reward using the original goal.
        # Evaluator controls position, not hidden cognitive target labels.
        goal = native.grid.get(native.width-2,native.height-2)
        assert isinstance(goal,Goal)
        native.agent_pos = (native.width-2,native.height-3)
        native.agent_dir = 1
        _,reward,terminated,truncated,_ = native.step(native.actions.forward)
        assert terminated and reward > 0 and not truncated
        print("MR14_INDEPENDENT_NATIVE_CONSEQUENCES=" + json.dumps({
            "source_commit":actual_commit,
            "native_environment":"Original MiniGrid DoorKeyEnv(size=5)",
            "native_step_api_used":True,
            "locked_door_without_key_stays_locked":blocked_toggle,
            "original_pickup_action_acquired_key":True,
            "native_door_toggle_with_key_unlocked":True,
            "native_forward_through_open_door":True,
            "native_goal_step_terminated_with_reward":True,
            "original_world_state_inspected_by_evaluator_only":True,
            "heterogeneous_transition_classes_verified":True,
            "source_newly_authored_by_yggdrasil":False,
            "independent_hidden_task_family":False,
            "cell_local_mapping_within_45_parameters":"NOT_QUALIFIED",
            "native_model_training":"NONE",
            "resource_parity":"NOT_QUALIFIED",
            "protected_scientific_first_use":False,
            "licensing_reconciled":False,
        },sort_keys=True))
    finally:
        native.close()


if __name__=="__main__":
    try:
        main()
    except (ValueError, AssertionError, OSError, subprocess.CalledProcessError,
            ImportError) as exc:
        print("MR14_SOURCE_INTAKE_FAIL_CLOSED: "+str(exc),file=sys.stderr)
        raise
