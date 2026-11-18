"""Seal exact cross-platform oracle evidence while preserving any negative."""
import json
import os
from pathlib import Path
import subprocess
from independent_audit import audit

HERE=Path(__file__).resolve().parent
FROZEN="75c23a3bde818056c3035a73e7bf89fdfda71cce"
PARENT="392f6c5d66adfff3b79d6a6a2910b6557dfccbdc"

def main():
    linux=json.loads((Path(os.environ["CK21OH_LINUX"])/"result.json").read_text())
    windows=json.loads((Path(os.environ["CK21OH_WINDOWS"])/"result.json").read_text())
    a,b=audit(linux),audit(windows)
    if a["stable_sha256"]!=b["stable_sha256"] or a["classification"]!=b["classification"]:
        raise ValueError("CK21_OH01_CROSS_PLATFORM_DRIFT")
    source=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    if subprocess.run(["git","merge-base","--is-ancestor",FROZEN,source],
                      check=False).returncode:
        raise ValueError("CK21_OH01_PREREG_ANCESTOR")
    (HERE/"result.json").write_text(json.dumps(linux,sort_keys=True,indent=2)+"\n")
    (HERE/"replication-windows.json").write_text(json.dumps(windows,sort_keys=True,indent=2)+"\n")
    provenance={"schema":"yggdrasil.ck21oh01.provenance.v1",
                "source_parent":PARENT,"prereg_sha":FROZEN,
                "source_commit":source,"result_sha256":a["stable_sha256"],
                "linux_wall_seconds":linux["whole_wall_seconds"],
                "windows_wall_seconds":windows["whole_wall_seconds"],
                "scientific_pass":False,"deployment":"NONE"}
    (HERE/"provenance.json").write_text(json.dumps(provenance,sort_keys=True,indent=2)+"\n")
    returning=linux["returning"]
    report=[
      "# CK21-OH01 — informed-oracle reward headroom on returning causal regimes",
      "",
      "Frozen **before scoring** at "+FROZEN+". Exact prior integrated head "+PARENT+".",
      "**"+linux["classification"]+"**. Isolated previously-consumed synthetic evaluator-only development.",
      "No real source actions, retraining or native integration.",
      "",
      "This reference receives true evaluator source family and regime, which the",
      "native model does NOT receive. It cannot see private hidden/noise bits,",
      "future transition/reward or the chosen episode's counterfactuals. It selects",
      "two actions sequentially from the public initial state and observed s2.",
      "An exhaustive independent model of hidden, observation/transition noise and",
      "reward noise verifies the exact expected source-informed optimum 113/128",
      "(88.28125 percent), equal across all frozen source families.",
      "",
      "## Same previously consumed held episode scores",
      "",
      "| Session | World | Reference successes /288 | CKAD21 active /288 | Pooled /288 |",
      "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in linux["by_session"]:
        report.append("| "+str(row["session"])+" | "+row["family"]+" "+str(row["regime"])+" | "+
                      str(row["oracle_reward"])+" | "+str(row["active_reward"])+" | "+
                      str(row["pooled_reward"])+" |")
    report.extend([
      "",
      "## Returning environments (sessions 0+3)",
      "",
      "- Informed reference: "+str(returning["oracle_reward"])+"/576.",
      "- Native CKAD21 active: "+str(returning["active_reward"])+"/576.",
      "- Pooled CKAD21: "+str(returning["pooled_reward"])+"/576.",
      "- Original frozen 5pp gain requires at least "+
          str(returning["required_absolute_successes"])+"/576 above pooled.",
      "- Informed reference's observed headroom versus pooled: "+
          str(returning["oracle_minus_pooled"])+"/576.",
      "- Expected reference result before frozen sampling: 1017/2 =508.5 of576;",
      "- Reference result reaches old 5pp margin: "+
          str(returning["reference_oracle_meets_frozen_5pp_margin"])+".",
      "",
      "The informed reference is optimal **in expectation** given true source family",
      "and regime, but is NOT a strict upper bound on realized 576-trial rewards",
      "for a learner with only public data. Small realized-sample differences",
      "do not justify changing the original frozen development requirement.",
      "No trained conventional learner or native system is promoted here.",
      "",
      "Exact Linux/Windows semantic sha256: "+a["stable_sha256"],
      "Run primary, replication and mandatory final regression independently.",
      "**SCIENTIFIC_PASS=false. DEPLOYMENT NONE.**",
      "",
    ])
    (HERE/"SESSION_REPORT.md").write_text("\n".join(report))
    print(json.dumps({"sealed":True,"stable":a["stable_sha256"],
                      "classification":a["classification"],
                      "returning":returning},sort_keys=True))

if __name__=="__main__":
    main()
