"""Seal the CKAD21 frozen development receipts from both executed OS jobs."""
import json
import os
from pathlib import Path
import subprocess
from independent_audit import audit

HERE=Path(__file__).resolve().parent
PARENT="d8f27db46af889afdfeb104fc471a710fc6d5c06"


def need(ok,code):
    if not ok:
        raise ValueError("CKAD21_SEAL_"+code)


def main():
    linux=Path(os.environ["CKAD21_LINUX_DIRECTORY"])/"result.json"
    windows=Path(os.environ["CKAD21_WINDOWS_DIRECTORY"])/"result.json"
    a=json.loads(linux.read_text())
    b=json.loads(windows.read_text())
    ga,gb=audit(a),audit(b)
    need(ga["stable_sha256"]==gb["stable_sha256"],"PLATFORM_STABLE_MISMATCH")
    need(a["totals"]==b["totals"] and a["gates"]==b["gates"],"PLATFORM_SCORE_DRIFT")
    need(a["classification"]==b["classification"],"PLATFORM_CLASSIFICATION")
    need(a["parent_sha"]==PARENT and a["source_sha256"]==b["source_sha256"],"PARENT_SOURCE")
    prereg=subprocess.check_output(["git","rev-parse","8736e1358e34eea1c0823de80122ce8da7b5539a"],text=True).strip()
    source=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    need(prereg=="8736e1358e34eea1c0823de80122ce8da7b5539a","PREREG_SHA")
    need(subprocess.run(["git","merge-base","--is-ancestor",prereg,source],check=False).returncode==0,
         "PREREG_ANCESTOR")
    (HERE/"result.json").write_text(json.dumps(a,sort_keys=True,indent=2)+"\n")
    (HERE/"replication-windows.json").write_text(json.dumps(b,sort_keys=True,indent=2)+"\n")
    provenance={
      "schema":"yggdrasil.ckad21.provenance.v1","prereg_sha":prereg,
      "exact_parent_sha":PARENT,"source_sha":source,
      "result_stable_sha256":a["stable_sha256"],
      "linux_wall_seconds":a["whole_wall_seconds"],
      "windows_wall_seconds":b["whole_wall_seconds"],
      "science":False,"accepted_native":False,"deployment":"NONE"
    }
    (HERE/"provenance.json").write_text(json.dumps(provenance,sort_keys=True,indent=2)+"\n")
    prior=a["totals"]["eval-0"]
    shifted=a["totals"]["eval-2"]
    gates=a["gates"]
    report=[
        "# CKAD21 — early/late memory and first-consequence Bayesian belief",
        "",
        "**"+a["classification"]+"** — synthetic, previously consumed CKAD20 environment.",
        "No new native training or source first-use; only trained public witnesses are read.",
        "The native checkpoint remains byte-exact; two conventional",
        "Beta histories are combined through a fixed equal prior. After receiving",
        "first-stage s2, the second action uses a conditional posterior over",
        "older versus recent models. No true family, regime, hidden state or future outcome",
        "is passed to the learner.",
        "",
        "## Matched closed-loop rewards",
        "",
        "| Final trained policy | Old invariant eval-0 /288 | Shifted eval-2 /288 |",
        "|---|---:|---:|"
    ]
    for name in ("two_timescale_dynamic","two_timescale_static","early_only","late_only",
                 "native_ckad20","full_beta","trailing64_mle"):
        report.append(f"| {name} | {prior[name]} | {shifted[name]} |")
    report.extend(["", "## Frozen gates", ""])
    report.extend(f"- {name}: {'PASS' if good else 'FAIL'}" for name,good in gates.items())
    report.extend([
        "",
        "The independently coded exact conventional joint readout and posterior identity",
        "tied the frozen Beta representation. Early/late swapping leaves the algorithm",
        "unchanged. No architectural superiority is implied even if development passes.",
        "Historical CKAD20 native model exactly matches 204/288 prior and 227/288 shifted",
        "successes; each arm executes its own actions on the same exogenous held draws.",
        "No held training, new source calls or model promotion occurred.",
        "",
        "Linux and Windows semantic results match at SHA256:",
        a["stable_sha256"],
        "",
        f"Linux wall {a['whole_wall_seconds']:.3f}s, Windows wall {b['whole_wall_seconds']:.3f}s,",
        "excluding CI provision and final regression.",
        "",
        "**ENGINEERING**: subject to mandatory final SHA/full regression.",
        "**SCIENTIFIC_PASS=false. DEPLOYMENT NONE.**",
        "",
        "Replay with: python -B research/contrib/chatgpt/CKAD-21/campaign.py --output-directory OUTPUT",
        "Audit with: python -B research/contrib/chatgpt/CKAD-21/independent_audit.py",
        "",
    ])
    (HERE/"SESSION_REPORT.md").write_text("\n".join(report))
    print(json.dumps({"sealed":True,"stable":a["stable_sha256"],
                      "development":a["classification"],"gates":a["gates"]},sort_keys=True))


if __name__=="__main__":
    main()
