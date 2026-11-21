"""Read-only two-expert evidence-gate screen on *consumed* Amalgam traces.

The experiment protocol was Git-frozen before this code scored the traces.
This is not fresh scientific first-use, held-out validation, model training,
checkpoint editing, native acceptance, or a production selector.
"""
from __future__ import annotations

from hashlib import sha1
from json import dumps, loads
from pathlib import Path
import sys

SCALE = 1_000_000
SOURCE = "86264b41a08d49f558418c0fba367f3a2636befa"
ARMS = ("pinned", "unguarded", "guarded", "fit_full", "fit_trailing",
        "fit_change_point")
STAGES = ("novel_causal_switch", "swapped_terminal", "A_return")


def git_blob_sha(raw: bytes) -> str:
    return sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def step(posterior_pinned: float, frozen: tuple[int, int], live: tuple[int, int],
         state: int, reward: int, *, hazard: float = 1 / 32) -> tuple[tuple[int, int], float]:
    """Forecast before revealing the scored reward; then update evidence.

    Forecast inputs are the original source's prequential, million-scaled
    Yggdrasil predictions, not fitted hindsight outcomes.
    """
    if state not in (0, 1) or reward not in (0, 1):
        raise ValueError("R15_NONBINARY_LABEL")
    if not 0 <= posterior_pinned <= 1 or not 0 <= hazard <= 1:
        raise ValueError("R15_BAD_PRIOR")
    if not all(type(v) is int and 0 <= v <= SCALE for v in (*frozen, *live)):
        raise ValueError("R15_BAD_FORECAST")
    tp, rp = (v / SCALE for v in frozen)
    tl, rl = (v / SCALE for v in live)
    prior = (1 - hazard) * posterior_pinned + hazard / 2
    pt = prior * tp + (1 - prior) * tl
    sp = tp if state else 1 - tp
    sl = tl if state else 1 - tl
    norm = prior * sp + (1 - prior) * sl
    if norm <= 0:
        raise ValueError("R15_IMPOSSIBLE_TRANSITION")
    conditioned = prior * sp / norm
    pr = conditioned * rp + (1 - conditioned) * rl
    predicted = (round(pt * SCALE), round(pr * SCALE))
    lp = sp * (rp if reward else 1 - rp)
    ll = sl * (rl if reward else 1 - rl)
    denom = prior * lp + (1 - prior) * ll
    if denom <= 0:
        raise ValueError("R15_IMPOSSIBLE_OBSERVATION")
    posterior = prior * lp / denom
    if not 0 <= posterior <= 1:
        raise ValueError("R15_POSTERIOR_OUT_OF_BOUNDS")
    return predicted, posterior


def evaluate_trace(trace: list[dict], seed: int, git_sha: str,
                   *, hazard: float, margin: float, return_bound: float) -> dict:
    if len(trace) != 72 or any(x["stage"] != index // 24 + 1
                               for index, x in enumerate(trace)):
        raise ValueError("R15_TRACE_ORDER")
    posterior = 0.5
    totals = [{name: [0, 0] for name in ("candidate", *ARMS)} for _ in STAGES]
    stage_initial = []
    for i, event in enumerate(trace):
        row, arms = event["row"], event["forecast"]
        if set(arms) != set(ARMS) or i % 24 == 0 and len(stage_initial) != i // 24:
            raise ValueError("R15_TRACE_STRUCTURE")
        if i % 24 == 0:
            stage_initial.append(posterior)
        s, r = row["s2"], row["y"]
        predicted, posterior = step(posterior, tuple(arms["pinned"]),
                                    tuple(arms["unguarded"]), s, r,
                                    hazard=hazard)
        truth = (s * SCALE, r * SCALE)
        for name in ("candidate", *ARMS):
            forecast = predicted if name == "candidate" else arms[name]
            for k in range(2):
                totals[i // 24][name][k] += (forecast[k] - truth[k]) ** 2
    stages = []
    for i, sums in enumerate(totals):
        scores = {name: sum(v) / (48 * SCALE * SCALE)
                  for name, v in sums.items()}
        best = min(scores[a] for a in ARMS)
        advantage = best - scores["candidate"]
        return_noninfer = scores["candidate"] - scores["pinned"] <= return_bound
        stage_pass = advantage >= margin and (i != 2 or return_noninfer)
        stages.append(dict(stage=i + 1, name=STAGES[i], mean_brier=scores,
                           strongest_control=[a for a in ARMS
                                              if abs(scores[a] - best) < 1e-12],
                           gain_vs_best=advantage, beat_strongest=advantage >= margin,
                           return_noninferiority_vs_pinned=return_noninfer,
                           stage_pass=stage_pass,
                           start_pinned_weight=stage_initial[i]))
    return dict(seed=seed, trace_git_blob=git_sha, n=72,
                end_pinned_weight=posterior, stages=stages,
                pass_all_stages=all(s["stage_pass"] for s in stages))


def run(root: Path) -> dict:
    here = Path(__file__).parent
    protocol = loads((root / "r15_expert_switch_protocol.json").read_text())
    if protocol["source_commit"] != SOURCE or protocol["forecast_scale"] != SCALE:
        raise ValueError("R15_PROTOCOL_DRIFT")
    if [s["index"] for s in protocol["stages"]] != [1, 2, 3]:
        raise ValueError("R15_STAGE_PROTOCOL_DRIFT")
    h = 1 / 32
    if protocol["candidate"]["hazard"] != "1/32" or len(protocol["traces"]) != 3:
        raise ValueError("R15_HAZARD_OR_SEED_DRIFT")
    results = []
    for item in protocol["traces"]:
        path = root / "staged-retention-dev-01" / f"seed-{item['seed']}" / "trace.json"
        raw = path.read_bytes()
        git_sha = git_blob_sha(raw)
        if git_sha != item["git_blob"]:
            raise ValueError("R15_SOURCE_GIT_BLOB_MISMATCH")
        results.append(evaluate_trace(loads(raw), item["seed"], git_sha,
                                      hazard=h, margin=0.005, return_bound=0.02))
    return dict(schema="yggdrasil.amalgam.r15.two-expert-evidence-switch-dev-report-v1",
                source_commit=SOURCE, protocol_git_blob=
                "55ca0440062bbe6348612657756a489c75750773",
                pre_result_commit="ec48f08cbbd0b65239d8faf5c4cee2595afe71cd",
                hazard="1/32", existing_consumed_traces_only=True,
                scientific_pass=False, owner_accepted=False,
                development="DEV_GO" if all(r["pass_all_stages"] for r in results)
                else "DEV_NO_GO", results=results)


if __name__ == "__main__":
    expected = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
    print(dumps(run(expected), sort_keys=True, indent=2))
