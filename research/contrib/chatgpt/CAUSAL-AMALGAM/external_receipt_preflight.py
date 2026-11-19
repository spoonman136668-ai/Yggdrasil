"""Exercise the source boundary on a disposable copy of the sealed anchor."""

import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic

from growth_preflight import expect_value_error
from joint_update_preflight import parent_material
from shadow_preflight import checked_bytes, require
from yggdrasil.native_causal_amalgam import EXTERNAL_SCHEMA, NativeCausalAmalgam
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE, experience_packet_sha256


HERE = Path(__file__).resolve().parent
SOURCE = digest(b"amalgam-external-source-engineering-fixture-v1")
OTHER = digest(b"amalgam-external-source-negative-control")


def anchor_material(inputs):
    proof = json.loads((HERE / "selection_protocol_dev.json").read_bytes())
    return proof, parent_material(inputs / proof["native_name"], inputs / proof["donor_name"])


def run(inputs):
    started = monotonic()
    proof, material = anchor_material(inputs)
    parent_path = inputs / proof["joint_name"]
    parent_raw = (parent_path.read_bytes() if sys.platform == "win32" else
                  checked_bytes(parent_path, proof["joint_sha256"]))
    parent_sha = digest(parent_raw)
    parent = NativeCausalAmalgam.restore(parent_raw, parent_sha, **material)
    expected = json.loads((HERE / "joint-result.json").read_bytes())
    require(digest(parent.native.checkpoint()) == expected["native_checkpoint_sha256"],
            "EXTERNAL_ANCHOR_NATIVE_PIN")
    prefix = parent.native._episode_reader()._ledger
    identifier = digest(b"amalgam-external-source-engineering-receipt-v1")
    views = ((1, 0), (1, 1))
    row = dict(s1=1, x1=0, s2=1, x2=1, y=0)
    packet = experience_packet_sha256(SOURCE, identifier, views, row)

    def admit(model, *, key=identifier, evidence=row, source=SOURCE, permitted=SOURCE, bound=None):
        return model.observe_experience(
            key, views, evidence, source_sha256=source, external_source_sha256=permitted,
            packet_sha256=bound if bound is not None else
            experience_packet_sha256(source, key, views, evidence),
        )

    expect_value_error(lambda: admit(parent, permitted=None), "EPISODE_EXTERNAL_SOURCE_PIN")
    expect_value_error(lambda: admit(parent, source=OTHER), "EPISODE_EXTERNAL_SOURCE_PIN")
    expect_value_error(lambda: admit(parent, bound=experience_packet_sha256(
        EXPERIENCE_SOURCE, identifier, views, row)), "EPISODE_SOURCE_PACKET")
    expect_value_error(lambda: admit(parent, key=prefix[-1][0]), "EPISODE_EXTERNAL_PREFIX_COLLISION")
    expect_value_error(lambda: admit(parent, evidence={**row, "s1": 0}), "EPISODE_EXTERNAL_CONTEXT")
    child = admit(parent, bound=packet)
    ledger = child.native._episode_reader()._ledger
    require(ledger[:-1] == prefix and len(ledger) == 1026, "EXTERNAL_NATIVE_PREFIX")
    require(child.native._external_experience == (len(prefix), SOURCE, (packet,)),
            "EXTERNAL_ALIGNED_SOURCE")
    require(admit(child) is child, "EXTERNAL_IDEMPOTENCE")
    expect_value_error(lambda: admit(child, evidence={**row, "y": 1}), "EPISODE_CONFLICTING_REPLAY")
    expect_value_error(lambda: admit(child, source=EXPERIENCE_SOURCE), "EPISODE_EXTERNAL_SOURCE_CHANGE")
    require(parent.checkpoint() == parent_raw, "EXTERNAL_ANCHOR_BYTES")
    steps = [new.steps - old.steps for old, new in zip(parent._heads, child._heads, strict=True)]
    require(steps == [3] * 4, "EXTERNAL_SHARED_UPDATE")
    raw = child.checkpoint()
    pin = digest(raw)

    def restore(checkpoint=raw, *, source=SOURCE):
        return NativeCausalAmalgam.restore(
            checkpoint, digest(checkpoint), external_source_sha256=source, **material)

    expect_value_error(lambda: restore(source=None), "CKAD_INTEGRATED_CHECKPOINT_REJECTED")
    expect_value_error(lambda: restore(source=OTHER), "CKAD_INTEGRATED_CHECKPOINT_REJECTED")
    cold = restore()
    require(cold.checkpoint() == raw and admit(cold) is cold, "EXTERNAL_COLD_PARITY")
    next_id = digest(b"amalgam-external-source-engineering-receipt-v2")
    require(admit(cold, key=next_id).checkpoint() == admit(child, key=next_id).checkpoint(),
            "EXTERNAL_COLD_CONTINUATION")
    with TemporaryDirectory(prefix="amalgam-external-restore-") as directory:
        path = Path(directory) / "checkpoint.json"
        path.write_bytes(raw)
        fresh = subprocess.check_output(
            [sys.executable, "-B", __file__, str(inputs), "--cold", str(path), pin],
            text=True, timeout=120,
        ).strip()
        require(fresh == pin, "EXTERNAL_FRESH_PROCESS")

    forged = json.loads(raw)
    require(forged["schema"] == EXTERNAL_SCHEMA, "EXTERNAL_JOINT_SCHEMA")
    forged["action_heads"][0]["encoder_bias"][0] += .05
    expect_value_error(lambda: restore(canonical(forged)), "JEPA3_SOURCE_BIAS_PARITY")
    forged = json.loads(raw)
    native = json.loads(forged["native_ascii"])
    native["external_experience"][2][0] = "0" * 64
    forged["native_ascii"] = canonical(native).decode("ascii")
    expect_value_error(lambda: restore(canonical(forged)), "CKAD_INTEGRATED_CHECKPOINT_REJECTED")
    return {
        "engineering": "PASS",
        "source": SOURCE,
        "anchor": parent_sha,
        "descendant": pin,
        "descendant_native": digest(child.native.checkpoint()),
        "native_witnesses": len(ledger),
        "head_step_deltas": steps,
        "new_source_actions": 0,
        "scientific_comparisons": 0,
        "wall_seconds": monotonic() - started,
    }


if __name__ == "__main__":
    inputs = Path(sys.argv[1])
    if len(sys.argv) == 5 and sys.argv[2] == "--cold":
        _, material = anchor_material(inputs)
        child = NativeCausalAmalgam.restore(
            Path(sys.argv[3]).read_bytes(), sys.argv[4], external_source_sha256=SOURCE, **material)
        print(digest(child.checkpoint()))
    else:
        print(json.dumps(run(inputs), indent=2, sort_keys=True))
