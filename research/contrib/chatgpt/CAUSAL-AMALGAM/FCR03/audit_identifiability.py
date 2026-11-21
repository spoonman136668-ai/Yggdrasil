"""FCR03 retrospective, exact input-action identifiability audit.

Reads the already consumed source-free fixture and archived result; executes
no new policy, trial, or original-world action. Not a prospective experiment.
"""
from __future__ import annotations

from hashlib import sha1, sha256
from itertools import product
from pathlib import Path
from collections import defaultdict
import json
import lzma

HERE = Path(__file__).resolve().parent
SOURCE_GIT_BLOBS = {
    "dev_trial.py": "ae4cbf1f7193291f26dfafcede535a0493825f57",
    "mechanism_recall.py": "ad23ec009e81f3c86405ad309289464a8827ccff",
}
TRIAL_LZMA_GIT_BLOB = "f9ca478fe6ff6d3fd7b694d70ec279c22bebfe34"
TRIAL_RAW_SHA256 = "a81297f6a0f0bf7c982f7c8656af85be92c432e321b5e49dfbea9b5beee92cee"
EXPECTED_PARENT = "86264b41a08d49f558418c0fba367f3a2636befa"
PHASE_LENGTHS = (("A_familiar",80),("B_changed",80),("A_return",80),
                 ("C_recombination",80),("D_nonlinear_unknown",48))
SEEDS = tuple(range(317101,317109))


def git_blob_sha(data):
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def bit(seed, index, field):
    return sha256(f"{seed}/{index}/{field}".encode("ascii")).digest()[0] & 1


def check_custody():
    for name, wanted in SOURCE_GIT_BLOBS.items():
        actual = git_blob_sha((HERE/name).read_bytes())
        if actual != wanted:
            raise ValueError(f"FCR03_SOURCE_DRIFT:{name}:{actual}")
    raw_archive = (HERE/"primary_result.json.xz").read_bytes()
    if git_blob_sha(raw_archive) != TRIAL_LZMA_GIT_BLOB:
        raise ValueError("FCR03_ARCHIVE_BLOB_DRIFT")
    raw = lzma.decompress(raw_archive)
    if sha256(raw).hexdigest() != TRIAL_RAW_SHA256:
        raise ValueError("FCR03_ARCHIVE_SHA_DRIFT")
    result = json.loads(raw)
    if (result.get("source_parent") != EXPECTED_PARENT or
        result.get("classification") != "DEV_NO_GO" or
        result.get("seed_count") != 8 or
        result.get("total_events") != 2944 or
        result.get("consumed_trials") != 1):
        raise ValueError("FCR03_ORIGINAL_RESULT_DRIFT")
    return result


def transition_a(c, x1): return x1 ^ c

def transition_b(c, x1): return x1

def reward_a(c, x1, s2, x2): return s2 ^ x2

def reward_b(c, x1, s2, x2): return s2 ^ x2 ^ c


def separation_table():
    table = {}
    for context in (0,1):
        transition = {transition_a(context,x1) != transition_b(context,x1)
                      for x1 in (0,1)}
        reward = {reward_a(context,x1,s2,x2) != reward_b(context,x1,s2,x2)
                  for x1,s2,x2 in product((0,1),repeat=3)}
        if transition != {bool(context)} or reward != {bool(context)}:
            raise ValueError("FCR03_ACTION_INVARIANCE_VIOLATED")
        table[str(context)] = {
            "transition_model_separation":int(bool(context)),
            "reward_model_separation_given_public_s2":int(bool(context)),
            "bits_if_equal_priors_before_witness":context,
            "information_gain_dependent_on_x1_or_x2":False,
            "public_outcome_combinations_checked":10,
        }
    return table


def phase_coverage():
    totals=defaultdict(lambda: {"total":0,"informative_c1":0,"per_seed":{}})
    for seed in SEEDS:
        offset=0
        for phase,length in PHASE_LENGTHS:
            count=sum(bit(seed,i,"context") for i in range(offset,offset+length))
            totals[phase]["total"] += length
            totals[phase]["informative_c1"] += count
            totals[phase]["per_seed"][str(seed)] = count
            offset+=length
    for name,_ in PHASE_LENGTHS:
        if totals[name]["informative_c1"] <= 0:
            raise ValueError("FCR03_INFORMATIVE_WITNESSES_MISSING")
    return dict(totals)


def audit():
    primary=check_custody()
    separation=separation_table()
    coverage=phase_coverage()
    best=primary["matched_best"]
    means=primary["means"]["mechanism_recall"]
    c_reward=means["C_recombination"]["reward"]
    c_best=best["C_recombination"]["reward"]
    a_transition=means["A_return"]["transition"]
    a_best=best["A_return"]["transition"]
    if not(c_reward > c_best and a_transition > a_best + 0.020):
        raise ValueError("FCR03_RECORDED_NEGATIVE_MISMATCH")
    return {
        "schema":"yggdrasil.fcr03.retrospective-action-identifiability.v1",
        "classification":"DIAGNOSTIC_ACTION_ADVANTAGE_NOT_IDENTIFIABLE_ON_FCR03_FIXTURE",
        "scope":"read_only_retrospective_exact_enumeration; not new trial",
        "fcr03_parent":EXPECTED_PARENT,
        "source_blobs":SOURCE_GIT_BLOBS,
        "raw_trial_git_blob":TRIAL_LZMA_GIT_BLOB,
        "raw_trial_sha256":TRIAL_RAW_SHA256,
        "original_result":"DEV_NO_GO",
        "separation_by_context":separation,
        "phase_coverage":coverage,
        "recombined_reward_Brier_delta_vs_strongest_control":round(c_reward-c_best,12),
        "return_transition_Brier_delta_vs_strongest_control":round(a_transition-a_best,12),
        "information_conclusion":"A versus B transition/reward laws are identical at c=0 and fully separated at c=1 for EVERY allowed x1/x2 action; because c is exogenous in this fixture, policy action selection cannot change mechanism identifiability at matched public c and witness counts.",
        "failure_mechanism":"FCR03 reward/return failure cannot be attributed to insufficient diagnostically different x1/x2 actions in this fixture; investigate detector/recall and phase-change inference rather than rerun equivalent action policies.",
        "new_experiment_consumed":False,
        "safety":{"original_world_first_use":False,"native_model_modified":False,"scientific_gain_verified":False,"deployment":False},
    }


if __name__=='__main__':
    print(json.dumps(audit(),indent=2,sort_keys=True))
