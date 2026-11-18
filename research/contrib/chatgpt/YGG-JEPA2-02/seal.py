"""Cross-platform native multi-learner source evidence verification and Git seal."""
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from yggdrasil.native_context_basis import canonical, digest

HERE = Path(__file__).resolve().parent
FILES = ("result.json", "seed-14071-states.json", "seed-14071-trace.json",
         "seed-14072-states.json", "seed-14072-trace.json")


def check(c, label):
    if not c:
        raise RuntimeError("YGG_JEPA2_02_SEAL_" + label)


def equiv(a, b, label="root"):
    if type(a) is float and type(b) in (float, int):
        check(abs(a - b) < 1e-9, "NUMERIC_DRIFT_" + label)
    elif isinstance(a, list):
        check(isinstance(b, list) and len(a) == len(b), "LIST_" + label)
        for i, (x, y) in enumerate(zip(a, b)):
            equiv(x, y, label + "/" + str(i))
    elif isinstance(a, dict):
        check(isinstance(b, dict) and set(a) == set(b), "KEYS_" + label)
        for key in a:
            equiv(a[key], b[key], label + "/" + key)
    else:
        check(a == b, "VALUE_" + label)


def without_costs(result):
    value = json.loads(json.dumps(result))
    for seed in value["seeds"]:
        seed.pop("resource_accounting")
        for world in seed["worlds"]:
            world.pop("multi_learner_sha256")
            world.pop("multi_learner_bytes")
    return value


def main():
    linux = Path(os.environ["YGG_JEPA2_LINUX"])
    windows = Path(os.environ["YGG_JEPA2_WINDOWS"])
    run = os.environ["YGG_JEPA2_RUN_ID"]
    source = os.environ["YGG_JEPA2_SOURCE_SHA"]
    for name in FILES:
        check((linux / name).is_file() and (windows / name).is_file(),
              "MISSING_EVIDENCE_" + name)
    lr = json.loads((linux / "result.json").read_bytes())
    wr = json.loads((windows / "result.json").read_bytes())
    equiv(without_costs(lr), without_costs(wr), "primary_scores")
    for seed in (14071, 14072):
        states_a = json.loads((linux / f"seed-{seed}-states.json").read_bytes())
        states_b = json.loads((windows / f"seed-{seed}-states.json").read_bytes())
        check(len(states_a) == len(states_b) == 2, "WORLD_COUNT")
        for a, b in zip(states_a, states_b):
            check(a["world"] == b["world"] and
                  a["native_original_sha256"] == b["native_original_sha256"],
                  "SOURCE_WORLD_SHA")
            x, y = json.loads(a["multi_learner_ascii"]), json.loads(b["multi_learner_ascii"])
            check(x["native_ascii"] == y["native_ascii"] and
                  x["native_sha256"] == y["native_sha256"], "NATIVE_EXACT")
            for kind in ("transition", "reward"):
                equiv(x[kind], y[kind], "specialist_weights/" + kind)
        trace_a = json.loads((linux / f"seed-{seed}-trace.json").read_bytes())
        trace_b = json.loads((windows / f"seed-{seed}-trace.json").read_bytes())
        equiv(trace_a, trace_b, "episode_scores")
    check(lr["science_pass"] is False and wr["science_pass"] is False
          and lr["development_go"] == wr["development_go"],
          "PRESET_DEVELOPMENT_VERDICT")
    for name in FILES:
        shutil.copyfile(linux / name, HERE / name)
    receipt = {
        "schema": "yggdrasil.jepa2-02.replication.v1",
        "source_sha": source, "training_run": run, "windows_result": wr,
        "linux_artifact_sha256": {n: digest((linux / n).read_bytes()) for n in FILES},
        "windows_artifact_sha256": {n: digest((windows / n).read_bytes()) for n in FILES},
        "cross_platform_original_native_exact": True,
        "scientific_pass": False,
    }
    (HERE / "windows-replication.json").write_bytes(canonical(receipt))
    (HERE / "provenance.json").write_bytes(canonical({
        "schema": "yggdrasil.jepa2-02.provenance.v1",
        "prereg_first_sha": "f00d39793bff2091b7c74c05192a873725e675c2",
        "original_source_parent": "60634ab8c46b13039e021f28f8fa70bb6b69db96",
        "frozen_source_sha": source, "training_run": run,
        "original_first_use": False, "development_go": lr["development_go"],
        "scientific_pass": False, "deployment": "NONE",
    }))
    lines = [
        "# YGG-JEPA2-02 — cumulative native JEPA-style multi-learner",
        "",
        "ENGINEERING: primary and Windows replica completed and independently",
        "source-audited. Exact-final full Linux/Windows regression is separate.",
        "",
        "This trainable development model BUNDLES original NativeEpisodeExperience",
        "with two separately learned action-conditioned latent specialists;",
        "all 919 CKAD37 previously consumed public interventions are processed",
        "prequentially, with original native source checkpoints reproduced exactly.",
        "No original-world scientific first-use, transformer, text tokenizer,",
        "owner/controller action, hidden regime labels, or accepted model mutation.",
        "",
        "Frozen prereg commit: f00d39793bff2091b7c74c05192a873725e675c2",
        "Source commit: " + source,
        "Linux+Windows run: " + run,
        "",
        "## Pooled late B and A-return Brier (lower better)",
        "",
        "| Seed | Original native | JEPA-only | Native/JEPA blend | Best conventional | Mispaired | Verdict |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in lr["seeds"]:
        p = item["metrics"]["pooled_late"]
        lines.append(
            f"| {item['seed']} | {p['native_stream']['brier']:.9f} | "
            f"{p['jepa']['brier']:.9f} | {p['mixed']['brier']:.9f} | "
            f"{item['strongest_control_brier']:.9f} | "
            f"{p['mispaired']['brier']:.9f} | "
            f"{'DEVELOPMENT_GO' if item['development_go'] else 'DEVELOPMENT_NO_GO'} |"
        )
    lines.extend([
        "",
        "Frozen development verdict: " + ("GO" if lr["development_go"] else "NO_GO"),
        "SCIENTIFIC_PASS=false. DEPLOYMENT=NONE. DRAFT/UNMERGED.",
        "",
        "Each real episode trains both independently parameterized latent experts",
        "and the original native episode memory. A full versioned multi-learner",
        "checkpoint is independently restored by rederiving learned parameters",
        "from the authenticated native witnessed-action ledger; tampered neural",
        "weights cannot be legitimized by simply recalculating the file hash.",
        "",
        "Files: result.json, two seed-*-states.json, two seed-*-trace.json,",
        "windows-replication.json, provenance.json, prereg.json, campaign.py,",
        "audit.py, seal.py, the native module and its tests.",
        "",
        "Because the CKAD37 source was already consumed, this is a development",
        "comparison and may NOT be promoted as new scientific first-use.",
    ])
    (HERE / "README.md").write_text("\n".join(lines) + "\n", encoding="utf8")
    print("YGG_JEPA2_02_SEAL_PASS",
          "DEVELOPMENT_GO" if lr["development_go"] else "DEVELOPMENT_NO_GO",
          "SCIENCE_NOT_PASS", flush=True)


if __name__ == "__main__":
    main()

