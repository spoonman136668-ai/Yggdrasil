"""Persist two-OS reproductions of the frozen CKAD22 seed robustness audit."""
import json
import os
from pathlib import Path
import subprocess
from audit import canonical,sha

HERE=Path(__file__).resolve().parent
FROZEN="fa9abc8ba0a0331960fc59f9ef6b7ccf4d9320e8"
PARENT="f04cfcac2aa07806a6b942d968119de87bfb6aaf"


def require(condition, message):
    if not condition:
        raise ValueError("CK22_SR01_SEAL_"+message)


def main():
    linux=json.loads((Path(os.environ["CK22SR_LINUX"])/"result.json").read_text())
    windows=json.loads((Path(os.environ["CK22SR_WINDOWS"])/"result.json").read_text())
    require(linux["stable_sha256"]==windows["stable_sha256"],"OS_HASH_MISMATCH")
    require({k:v for k,v in linux.items() if k!="stable_sha256"}==
            {k:v for k,v in windows.items() if k!="stable_sha256"},"OS_REPRODUCTION")
    require(sha(canonical({k:v for k,v in linux.items() if k!="stable_sha256"}))==
            linux["stable_sha256"],"SELF_SHA")
    require(linux["source_stable_sha256"]==
            "4b20ef3b9229eddfd509e5897e6aa8f8d5226288ab331c4a98f8a7bc46fbccc2",
            "SOURCE_PIN")
    git_head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    require(subprocess.run(["git","merge-base","--is-ancestor",FROZEN,git_head],check=False).returncode==0,
            "PREREG_ANCESTOR")
    (HERE/"result.json").write_text(json.dumps(linux,indent=2,sort_keys=True)+"\n")
    (HERE/"replication-windows.json").write_text(json.dumps(windows,indent=2,sort_keys=True)+"\n")
    (HERE/"provenance.json").write_text(json.dumps({
       "schema":"yggdrasil.ck22.sr01.provenance.v1",
       "post_result_protocol_sha":FROZEN,
       "exact_qualified_ckad22_head":PARENT,
       "audit_source_sha":git_head,
       "stable_sha256":linux["stable_sha256"],
       "original_ckad22_development":"DEVELOPMENT_GO",
       "scientific_pass":False,"accepted_native":False,"deployment":"NONE"
    },indent=2,sort_keys=True)+"\n")
    rows=[
      "# CK22-SR01 — independent seed-group robustness and novel-candidate diagnostic",
      "",
      "This analysis was frozen AFTER the already-consumed CKAD22 experiment.",
      "It is not new preregistered scientific evidence and it did not train a model or",
      "execute another source episode.",
      "",
      "**Original CKAD22 engineering PASS; original development GO; scientific PASS not established.**",
      "Source SHA: "+PARENT+". Original result semantic SHA256: "+linux["source_stable_sha256"]+".",
      "The original 9/9 Linux/Windows CI is run 44266448951.",
      "",
      "| Session | Evaluator context (not given to learner) | Novel /288 | Retrieval /288 | Random probes /288 | Trailing MLE /288 |",
      "|---|---|---:|---:|---:|---:|"
    ]
    for s in linux["per_session"]:
       v=s["rewards"]
       rows.append(f'| {s["session"]} | {s["family"]} r{s["regime"]} | {v["novel_active"]} | {v["retrieval_only"]} | {v["novel_random"]} | {v["trailing_mle"]} |')
    rows.extend(["","## Per-seed gains on first encounters (sessions 0 + 1)","",
                  "| Seed | Novel minus retrieval (successes /192) | Novel minus trailing MLE | Novel minus random-probe arm |",
                  "|---|---:|---:|---:|"])
    r=linux["unfamiliar_0_1_group_differences"]
    for i,seed in enumerate((101,202,303)):
       rows.append(f'| {seed} | {r["retrieval_only"][i]} | {r["trailing_mle"][i]} | {r["novel_random"][i]} |')
    rows.extend([
      "",
      "Exact two-sided seed-cluster sign-flip p-values (3 independent seed groups):",
      *[f'- {name}: {val[0]}/{val[1]}'
         for name,val in linux["unfamiliar_group_exact_two_sided_signflip_p"].items()],
      "",
      "Novel-vs-retrieval shares actual new probe receipts. Novel-vs-random-probe",
      "also differs in selected probes, so it is not a pure novelty ablation.",
      "A source-matched exact independent online mixture ties the native learner;",
      "this prevents interpreting the source experiment as architecture superiority.",
      "",
      "All 12 sessions have 32 new-candidate updates and preserve 320 old ledger",
      "events plus previous sessions. Candidate posterior starts at 1/8 each session;",
      "ending weights, per-seed rewards, original metric fractions and falsification",
      "controls are retained in the canonical result JSON.",
      "",
      "No model state was modified. The source was already consumed.",
      "Exact cross-platform audit SHA256: "+linux["stable_sha256"],
      "",
      "**ENGINEERING:** subject to final sealed SHA regression and independent source audits.",
      "**SCIENTIFIC_PASS=false. DEPLOYMENT NONE.**",
      ""
    ])
    (HERE/"SESSION_REPORT.md").write_text("\n".join(rows))
    print(json.dumps({"sealed":True,"stable":linux["stable_sha256"],
                      "source":"CKAD22_DEVELOPMENT_GO",
                      "per_seed":r},sort_keys=True))


if __name__=="__main__":
    main()
