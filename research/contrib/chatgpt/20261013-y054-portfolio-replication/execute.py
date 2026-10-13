"""Y054: prospective, no-retuning replication of fixed schedule diversification."""
import importlib.util
import json
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent/"20261013-y053-schedule-hedge"/"execute.py"
spec=importlib.util.spec_from_file_location("y53_pinned",SOURCE)
assert spec and spec.loader
y53=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y53)

DEV=tuple(range(2080,2088))
HELDOUT=tuple(range(2088,2104))
FAMILIES=((3,13,1),(5,15,7),(7,5,13),(13,3,9))


def run():
    previous=(y53.DEV,y53.HELDOUT,y53.FAMILIES)
    try:
        y53.DEV=DEV
        y53.HELDOUT=HELDOUT
        y53.FAMILIES=FAMILIES
        result=y53.run()
    finally:
        y53.DEV,y53.HELDOUT,y53.FAMILIES=previous
    assert result["development_seeds"]==DEV
    assert result["sealed_heldout_seeds"]==HELDOUT
    assert result["families"]==FAMILIES
    assert result["hedge_balanced_schedule_counts"]=={"A":8,"B":8}
    assert len(result["heldout_records"])==5*4*16*3
    before=result["classification"]
    result["schema"]="yggdrasil.y054-fixed-schedule-diversification-transfer.v1"
    result["parent_head"]="cbc386856b12c06055e7baf4cdf460bbb77e7271"
    result["predecessor_classification_rubric_label"]=before
    result["classification"]={
        "PORTFOLIO_WORST_CASE_GAIN":"INDEPENDENT_COHORT_REPLICATION",
        "PARETO_PARTIAL":"PARTIAL_REPLICATION",
        "NO_GAIN":"NOT_REPLICATED"}[before]
    result["claim_limit"]=(
        "Fresh synthetic seed and affine-family transfer with pinned unchanged hedging rules; "
        "not independent physical source birth or within-run intelligent event forecasting.")
    return result


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
