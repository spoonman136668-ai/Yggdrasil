"""MG93-AM: retrospective public-transition/history sufficiency diagnostic."""
import argparse,hashlib,json,zipfile
from collections import defaultdict
from pathlib import Path
ARTIFACT="9f284ce2b793a2f6e0d0d8a1cb097efb5a9e5ce9b5d75f5c53a77f8474d0104a"
HELDOUT="0cdb155ce150717c3a678f6c536a81f5f4203dd96acafee459b2fdc1d2a36427"
ROLES=("mg92_native_feedback","mg91_frozen_native_prototypes","mg91_independent_linear_control","mg86_frozen_teacher")
def load(p):
 raw=Path(p).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=ARTIFACT: raise ValueError("ARTIFACT_SHA_MISMATCH")
 with zipfile.ZipFile(p) as z: b=z.read("heldout.json")
 if hashlib.sha256(b).hexdigest()!=HELDOUT: raise ValueError("HELDOUT_SHA_MISMATCH")
 d=json.loads(b)
 if d.get("schema")!="yggdrasil.itd02.mg93.immutable-original-feedback-replication.v1": raise ValueError("SCHEMA_MISMATCH")
 return d
def keys(rows,i):
 r=rows[i];p=rows[i-1] if i else None;p2=rows[i-2] if i>1 else None
 return ((r["before_sha"],r["action"]),
 (r["before_sha"],r["action"],p["action"] if p else None),
 (r["before_sha"],r["action"],p["before_sha"] if p else None,p["action"] if p else None),
 (r["before_sha"],r["action"],p2["action"] if p2 else None,p["action"] if p else None))
def summarize(eps):
 levels=[defaultdict(set) for _ in range(4)]
 for e in eps:
  rows=e["source_ledger"]
  for i,r in enumerate(rows):
   for j,k in enumerate(keys(rows,i)): levels[j][k].add(r["after_sha"])
 names=("public_state_action","plus_previous_action","plus_previous_public_state_action","plus_previous_two_actions")
 return [{"context":n,"unique_context_keys":len(m),"ambiguous_context_keys":sum(len(v)>1 for v in m.values()),"ambiguity_fraction":sum(len(v)>1 for v in m.values())/len(m) if m else 0} for n,m in zip(names,levels)]
def run(p):
 d=load(p);out={}
 for role in ROLES:
  out[role]={}
  for family in sorted({e["family"] for e in d["episodes"] if e["role"]==role}):
   eps=[e for e in d["episodes"] if e["role"]==role and e["family"]==family]
   out[role][family]={"episodes":len(eps),"steps":sum(len(e["source_ledger"]) for e in eps),"levels":summarize(eps)}
 return {"schema":"mg93.public_transition_aliasing.v1","classification":"RETROSPECTIVE_ORIGINAL_LEDGER_DIAGNOSTIC_NOT_CAUSAL","artifact_id":12972852607,"artifact_sha256":ARTIFACT,"heldout_sha256":HELDOUT,"roles":out,"limits":"Only three heldout seeds per family; episode boundaries isolated; public observation digest may alias latent inventory/pose. No unselected outcomes, interventions, policy changes or causal conclusions. Reduced ambiguity from finite history is descriptive, not proof of Markov sufficiency or transfer."}
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("artifact_zip");ap.add_argument("--output");a=ap.parse_args()
 s=json.dumps(run(a.artifact_zip),sort_keys=True,indent=2)
 if a.output:Path(a.output).write_text(s+"\\n",encoding="utf-8")
 print(s)
