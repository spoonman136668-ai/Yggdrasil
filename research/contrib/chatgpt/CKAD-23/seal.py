"""Seal matched Linux+Windows CKAD23 development results without promoting them."""
import json
import os
from pathlib import Path
import subprocess
from audit import load_artifact_dir,combine,WORLDS,PARENTS,ENVS

HERE=Path(__file__).resolve().parent
FROZEN="43bf1854d0c12c3dc26a3010c3ee9d945bece28b"
PARENT="f04cfcac2aa07806a6b942d968119de87bfb6aaf"

def need(b,code):
    if not b:raise ValueError("CKAD23_SEAL_"+code)

def save(name,obj):
    (HERE/name).write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n")

def main():
    root=Path(os.environ["CKAD23_ARTIFACT_ROOT"])
    source=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    need(subprocess.run(["git","merge-base","--is-ancestor",FROZEN,source],
                        check=False).returncode==0,"PREREG_FROZEN")
    need(subprocess.run(["git","merge-base","--is-ancestor",PARENT,source],
                        check=False).returncode==0,"PARENT_ANCESTOR")
    pair=load_artifact_dir(root)
    linux=[pair[("ubuntu-latest",p,h)] for p in PARENTS for h in (0,1)]
    windows=[pair[("windows-2022",p,h)] for p in PARENTS for h in (0,1)]
    a,b=combine(linux),combine(windows)
    need(a==b and a["stable_sha256"]==b["stable_sha256"],"OS_SEMANTIC_DRIFT")
    need(a["scientific_pass"] is False and a["accepted_native"] is False and a["deployment"]=="NONE",
         "NONPROMOTION")
    save("result.json",a)
    save("replication-windows.json",b)
    save("shards-linux.json",linux)
    save("shards-windows.json",windows)
    save("provenance.json",{
        "schema":"yggdrasil.ckad23.provenance.v1",
        "source_commit":source,"prereg_commit":FROZEN,"parent_sha":PARENT,
        "parent_ckad22_result_stable_sha256":a["parent_stable_sha256"],
        "result_stable_sha256":a["stable_sha256"],
        "linux_semantic_replication":True,"windows_semantic_replication":True,
        "source_class":"NEWLY_AUTHORED_UNPROTECTED_SYNTHETIC_DEVELOPMENT_ONLY",
        "scientific_pass":False,"accepted_native":False,"deployment":"NONE",
    })
    report=[
        "# CKAD23 — disjoint conjunctive and interaction causal transfer",
        "",
        "**"+a["classification"]+"** — new synthetic development structures,",
        "not independent scientific general intelligence qualification.",
        "",
        "Protocol frozen before any CKAD23 result at "+FROZEN+".",
        "Parent CKAD22 candidate "+PARENT+"; its native trained checkpoints",
        "contain 448 preserved public episodes. Both new-world decision policies",
        "learned only from 16 actual sequentially chosen public interventions",
        "per case; family labels and hidden noise stayed inside the evaluator.",
        "",
        "Three independently retained model parent groups crossed with eight",
        "synthetic exogenous evaluation namespaces and two new causal structures",
        "(48 transfer cases). Namespaces are NOT eight independent model seeds.",
        "No protected scientific first-use or original real-world source actions.",
        "",
        "| Environment | Novel success /1152 | Retrieval-only /1152 | Fully fitted Beta /1152 | Novel minus retrieval | Novel familiar return /1152 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for world in WORLDS:
        row=a["by_world"][world]
        new=row["scores"][world]
        old=row["scores"]["familiar"]
        report.append(f'| {world} | {new["novel_active"]} | {new["retrieval_only"]} | '
                      f'{new["full_beta"]} | {row["novel_deltas"]["retrieval_only"]} | '
                      f'{old["novel_active"]} |')
    report += [
        "",
        "## Frozen gates",
        "",
        *[f'- {key}: {"PASS" if passed else "FAIL"}'
          for key,passed in a["frozen_gates"].items()],
        "",
        "## Independent parent groups and synthetic seed namespaces",
        "",
    ]
    for world in WORLDS:
        report.append("- "+world+" group deltas vs retrieval: "+
                     str(a["by_parent_group"][world]["retrieval_only"])+"; "+
                     "exact two-sided sign-flip p="+
                     "/".join(map(str,a["seed_exact_two_sided_signflip_p"][world]["retrieval_only"]))+
                     "; positive environment namespace groups="+
                     str(a["seed_robustness_positive_counts"][world])+"/8.")
    report += [
       "",
       "Novel-vs-retrieval receives identical actual 16-probe receipts and actions.",
       "Novel-random uses an independent intervention policy and therefore tests",
       "a combination of probing and novel hypothesis effects.",
       "The exact conventional mixture is required to tie native forecasts/plans",
       "and observed held rewards. Fully fitted Beta uses the same 448+16 public receipts.",
       "No model learned from held rewards; source and historical prefix were immutable.",
       "All world scores are actual executed held policy reward, never counterfactual estimates.",
       "",
       "Linux/Windows exact semantic result SHA256: "+a["stable_sha256"],
       "Full result and per-shard score/trace/retention provenance preserved in this folder.",
       "",
       "**ENGINEERING:** subject to mandatory final regression at the atlas-sealed exact SHA.",
       "**SCIENTIFIC_PASS=false. DEPLOYMENT NONE.**",
       ""
    ]
    (HERE/"SESSION_REPORT.md").write_text("\n".join(report))
    print(json.dumps({"sealed":True,"classification":a["classification"],
          "gates":a["frozen_gates"],"stable":a["stable_sha256"]},sort_keys=True))

if __name__=="__main__":main()
