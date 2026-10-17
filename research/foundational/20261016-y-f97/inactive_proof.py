"""F97 frozen-empty-policy implication proof, source-only and no cohort data.

For each public prefix t:
- EXACT F62 baseline is computed from current native memory.
- Every nonbaseline legal candidate requires a grant from approved.get(key).
- Frozen approved={} makes every grant absent. Hence decide() returns baseline.
Induction on the 72-step memory sequence yields exact F60 on ALL legal streams.
The sampled toy events below only exercise this implication; they are not an
independent scientific original, new source, or acceptance cohort.
"""
from __future__ import annotations
import hashlib,importlib.util,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent
SRC=P/"paired_join_risk.py"
METHOD="d100ee3c329e648752647872e16473e9fe281963"
POLICY="2fd22c218978ae1765da9ec4e25845b1cc9c9bbe"
PRE="8e8450b07681ba4899e18d446e45f2007682a147"
def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def check():
 assert blob(SRC)==METHOD
 assert blob(P/"frozen-policy.json")==POLICY
 assert blob(P/"prereg.json")==PRE
 config=json.loads((P/"frozen-policy.json").read_text())
 assert config["stage"]=="TRAINED_EMPTY_POLICY_FROZEN_NO_HOLDOUT_ACCESSED"
 assert config["approved_categories"]==[]
 assert config["train_stats"]["eligible_categories"]==0
 assert config["approved_policy_sha256"]==hashlib.sha256(b"[]").hexdigest()
 assert config["validation_accessed"] is False and config["guard_accessed"] is False
 source=SRC.read_text()
 assert "grant=approved.get(k)" in source
 assert "if grant is None:continue" in source
 assert "if ranked:" in source
 assert "return baseline,False,num" in source
 spec=importlib.util.spec_from_file_location("f97_frozen_source_proof",SRC)
 F97=importlib.util.module_from_spec(spec);sys.modules[spec.name]=F97
 spec.loader.exec_module(F97)
 class Pack:
  def pack(self,a,b,c):return bytes(12)
 class Native:
  def _f60_step(self,before,event,pack):
   a,role,b=event
   return ((a,b,(2*role,)),)
  def actions(self,before,event,index,pack):
   base=self._f60_step(before,event,pack)
   alt=base+((event[2],event[0],(2*event[1]+1,)),)
   return (("append",-1,-1,base,()),("merge",-1,-1,alt,()))
  def _valid_memory(self,mem,pack):
   assert len(mem)<=12 and all(1<=len(r[2])<=6 for r in mem)
 native=Native()
 for offset in (0,1,7,13):
  public=tuple((10000+offset+i,(i+offset)%4,10001+offset+i) for i in range(72))
  memory=()
  receipts=[]
  for index,event in enumerate(public):
   memory=native._f60_step(memory,event,Pack())
   receipts.append(tuple(Pack().pack(*r).hex() for r in memory))
  observed,trace,diag=F97.online(public,{},Pack(),native,True)
  assert observed==memory and trace==tuple(receipts)
  assert diag["interventions"]==0 and len(trace)==72
 return dict(
  schema="yggdrasil.f97.empty-policy-construction.witness.v1",
  outcome="INELIGIBLE_PREHOLDOUT_FROZEN_EMPTY_POLICY",
  exact_source_and_training_receipt_verified=True,
  conditional_statement="For every admissible causal source stream, with frozen approved={} F97.online equals exact F60 native controller by induction",
  contract_examples=4,contract_public_prefixes=288,
  approved_categories=0,
  fresh_validation_or_guard_consumed=False,
  new_scientific_improvement_claim=False,
  optimizer_or_controller_mutation=False)
if __name__=="__main__":
 assert sys.argv[1:]==["--no-cohort-proof-only"]
 print(json.dumps(check(),sort_keys=True))
