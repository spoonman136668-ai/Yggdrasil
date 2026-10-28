"""Cross-host V31I cold restart exact deterministic provenance."""
import hashlib,json,subprocess
from pathlib import Path
from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v26_calibrated_return_audit import context,reward
from research.itd02_v31i_cold_restart_codec import pack,restore
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import canonical
from yggdrasil.itd02_v31d_distinct_return_dev import DistinctReturnRingDev
def replay(source,with_restart):
 m=DistinctReturnRingDev(source);rows=[]
 for family,n in (("cue_second",12),("source",12)):
  for i in range(n):
   if with_restart and rows:
    m=restore(pack(m))
   case=context(i,0);y=reward(family,case)
   m.start_observation(case[0]);m.accept_first(case[1])
   pred=m.score(case[2]);m.accept_second(case[2],y)
   rows.append([list(case),round(pred,12),m.fast,m.bank.slow.parameters_sha256(),m.bank.fast.parameters_sha256(),m.switches])
  if with_restart:m=restore(pack(m))
 return rows,pack(m)
def main():
 root=Path(__file__).resolve().parents[1]
 git=lambda *args:subprocess.check_output(("git",)+args,cwd=root,text=True).strip()
 for pin in ("a6e54f8cb6c0ff50976b2c748697990bc74d599f","3e2fb223b670f10914c8ced769ac60530530632f"):
  assert git("merge-base","--is-ancestor",pin,"HEAD")==""
 source=train_source()["pretrained_shared"]
 a,final_a=replay(source,False);b,final_b=replay(source,True)
 assert a==b and final_a==final_b
 assert restore(final_a).bank.source_sha==DistinctReturnRingDev(source).bank.source_sha
 envelope=json.loads(final_a);envelope["sha256"]="0"*64
 try:restore(canonical(envelope))
 except ValueError:pass
 else:raise AssertionError("TAMPER_ACCEPTED")
 assert len(final_a)<=12288
 print(json.dumps({"schema":"v31i.cold_restart.v1","classification":"V31I_COLD_RESTART_SCOPED_ENGINEERING_PASS__NO_SCIENCE",
 "events":len(a),"checkpoint_bytes":len(final_a),"source_only":True,
 "reserved_q_holdout_evaluated":False,"scientific_first_use":False,
 "native_source_modified":False,"continuous_vs_restored_identical":True,
 "tampered_digest_rejected":True,
 "canonical_trace_sha256":hashlib.sha256(canonical(a)).hexdigest(),
 "checkpoint_sha256":hashlib.sha256(final_a).hexdigest()},sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
