"""WSP186: original public physical recordings, separate pre-frozen cohort.

WSP184 stopped before any training because original walk 1 contained only
1,016 physical records; WSP185 verified the full public source roster.
This new study imports the unchanged WSP184 predictor/controls and admits
only the nine published full-length walks plus the 32-regime physical run.

All real recordings are existing CC BY 4.0 physical experiments.
No original-world first-use, Remote Lab calls, source owner admission,
native Yggdrasil integration, or scientific acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import sys
import time
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "WSP-184"))
import physical_context as prior  # original, frozen WSP184 mechanism

SCHEMA = "yggdrasil.wsp186.corrected-public-physical-dev.v1"
ZIP_SHA256 = "1ef92d39fff7645a9e6e8cd41311e708362606491590a1534c6a5135d207736e"
ZIP_MD5 = "19bb4e92cbe0b8dff49299b9b509ac36"
FIT_RUNS, VALID_RUNS, DEV_RUNS = (2,3,4,5,6), (7,8), (9,10)
RUN_SHA = {
    "actuators_random_walk_2": "de9ddacd37582f9b8b3fe28c6d852c86ef891e4b87de48679a54f84b00326f9a",
    "actuators_random_walk_3": "7a039b92188c78d906f9d8f0ab5646281c89d83a3e458f1661cdccd096dd2d3b",
    "actuators_random_walk_4": "022c754017fa4ac831adf91a98fbd49d984086d7c21164ec2c5986bfd85e8c6b",
    "actuators_random_walk_5": "f4e26667ef8650edbdb5bc9b182543527461d2e7bde03063ea7cf1e7bab45a37",
    "actuators_random_walk_6": "7502f2acd9ed1b40d2039f17320d50a58d01b7d749d4c8298af7f5efa8bba18d",
    "actuators_random_walk_7": "710c2d7ca785971f73e3c8777fefda85fcd241e3f0c771f05706204cfe46e8b9",
    "actuators_random_walk_8": "cc38d03b6b7e0f53a9c4b46a1227d34979fda58a9db15137791e66b2c00c05e6",
    "actuators_random_walk_9": "750d9e25f3ef9c8b6eb2c6b1cc3743a10ffd4ac0dc3ab1c2141f2b66f17d4ea4",
    "actuators_random_walk_10": "4e9630d13ddea8d481190b764e816523045550d8c73a4484d1cd9b04be548cae",
    "regime_jumps_single": "ae00d09adddde4db86f571d85f402adc959017f376848e14cc16625b02cd59e0",
}
SOURCE = "juangamella/causal-chamber@967d59a42956872f37463cc561ecf6e9ceab9364"


def admit_public_source(path: Path):
    """Reject unauthorized/missing/altered original input before model import use."""
    if not path.is_file() or not 0 < path.stat().st_size <= prior.MAX_ZIP_BYTES:
        raise ValueError("WSP186_ZIP_SIZE")
    blob = path.read_bytes()
    digest = hashlib.sha256(blob).hexdigest()
    if digest != ZIP_SHA256 or hashlib.md5(blob).hexdigest() != ZIP_MD5:
        raise ValueError("WSP186_ORIGINAL_SOURCE_HASH")
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        entries = {}
        total = 0
        for member in archive.infolist():
            name = PurePosixPath(member.filename)
            if name.is_absolute() or ".." in name.parts:
                raise ValueError("WSP186_ARCHIVE_TRAVERSAL")
            total += member.file_size
            if member.file_size > prior.MAX_MEMBER_BYTES or total > prior.MAX_UNCOMPRESSED_BYTES:
                raise ValueError("WSP186_UNCOMPRESSED_BUDGET")
            if member.is_dir() or name.stem not in RUN_SHA:
                continue
            if name.suffix != ".csv" or name.stem in entries:
                raise ValueError("WSP186_SOURCE_DUPLICATE_OR_FORMAT")
            entries[name.stem] = member
        if set(entries) != set(RUN_SHA):
            raise ValueError("WSP186_SOURCE_ROSTER")
        data = {}
        for name in sorted(RUN_SHA):
            with archive.open(entries[name]) as stream:
                raw = stream.read(prior.MAX_MEMBER_BYTES+1)
            if len(raw) > prior.MAX_MEMBER_BYTES:
                raise ValueError("WSP186_MEMBER_SIZE")
            if hashlib.sha256(raw).hexdigest() != RUN_SHA[name]:
                raise ValueError("WSP186_MEMBER_INTEGRITY")
            # Unchanged WSP184 reader still requires exactly 10k per walk,
            # 32x10k for changed physical regimes, and original valid fields.
            data[name] = prior.parse_csv(raw, name)
    return data, {"archive_sha256": digest, "upstream_md5": ZIP_MD5,
                  "member_sha256": dict(RUN_SHA),
                  "walk_1_excluded": True,
                  "walk_1_known_metadata_rows": 1016}


def analyze(data, manifest, start_cpu: float):
    fit = [data[prior.WALK+str(i)] for i in FIT_RUNS]
    val = [data[prior.WALK+str(i)] for i in VALID_RUNS]
    dev = [data[prior.WALK+str(i)] for i in DEV_RUNS]
    physical_regimes = data[prior.REGIME]
    model = prior.train_fit(fit)
    frozen = prior.checkpoint(model)
    frozen_sha = hashlib.sha256(frozen).hexdigest()
    val_scores = prior.evaluate_runs(val, model)
    best_valid_control = min(prior.CONTROLS,
                             key=lambda name:(val_scores["mean_normalized_rmse"][name],name))
    # Exactly once, only AFTER FIT & VALID model choice.
    dev_walk = prior.evaluate_runs(dev, model)
    changed_all = prior.evaluate_runs([physical_regimes], model,
                                      select=lambda row: row.regime > 0)
    changed_first = prior.evaluate_runs(
        [physical_regimes], model,
        select=lambda row: row.regime > 0 and
                           row.index % prior.EXPECTED_WALK < prior.FIRST_WINDOW)
    if (dev_walk["count"] != 2*(prior.EXPECTED_WALK-1)
            or changed_all["count"] != 31*prior.EXPECTED_WALK
            or changed_first["count"] != 31*prior.FIRST_WINDOW):
        raise ValueError("WSP186_SCORING_CUSTODY")
    frozen_after = prior.checkpoint(model)
    if frozen_after != frozen or hashlib.sha256(frozen_after).hexdigest() != frozen_sha:
        raise ValueError("WSP186_FROZEN_CORE_DRIFT")

    # Conservative control envelope is scored per output. This is an oracle
    # LOWER loss reference (not a deployable model-selector) to prevent
    # selective promotion of a weaker baseline.
    best_control = tuple(
        min(changed_first["normalized_rmse"][name][k]
            for name in prior.CONTROLS) for k in range(2))
    direct = changed_first["normalized_rmse"]["gated"]
    gain = tuple((best_control[k]-direct[k])/best_control[k]
                 if best_control[k] > 0 else 0. for k in range(2))
    return {
        "schema":SCHEMA,
        "experiment_id":"WSP-186",
        "frozen_prereg_first_commit":"82c3f824c735b6c0e8a505648737ae4f0d7eecba",
        "public_offline_development_only":True,
        "scientific_pass":False,
        "original_source_actions":0,
        "remote_lab_calls":0,
        "native_yggdrasil_training":False,
        "original_source":SOURCE,
        "published_physical_data":manifest,
        "fit_runs":FIT_RUNS,"validation_runs":VALID_RUNS,"public_dev_walk_runs":DEV_RUNS,
        "fit_record_pairs":model["fit_observations"],
        "direct_batch_coeff_abs_gap":model["parity"],
        "validation_selected_conventional":best_valid_control,
        "validation":val_scores,
        "public_dev_walk":dev_walk,
        "public_dev_regime_all":changed_all,
        "public_dev_regime_first200":changed_first,
        "best_scored_control_by_output_first200":best_control,
        "gated_relative_gain_first200_vs_best_control_by_output":gain,
        "frozen_5pct_both_sensors_met":all(g>=0.05 for g in gain),
        "frozen_fit_core_sha256":frozen_sha,
        "software_old_core_cold_retention_verified":True,
        "behavioral_old_law_retention_verified":False,
        "unfamiliar_world_transfer_verified":False,
        "process_cpu_seconds":time.process_time()-start_cpu,
        "interpretation":"One published physical chamber, parameter changes only; public development results, no scientific acceptance."
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",type=Path,required=True)
    a=p.parse_args()
    start=time.process_time()
    data,manifest=admit_public_source(a.archive)
    result=analyze(data,manifest,start)
    print("WSP186_PUBLIC_PHYSICAL_DEV_RESULT="+json.dumps(
        result,sort_keys=True,separators=(",",":"),allow_nan=False))


if __name__=="__main__":
    main()
