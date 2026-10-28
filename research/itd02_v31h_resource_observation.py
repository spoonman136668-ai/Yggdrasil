"""V31H host-local resource sample; no policy changes or holdout."""
import gc,json,subprocess,time,tracemalloc
from pathlib import Path
from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v26_calibrated_return_audit import STREAMS
from research.itd02_v31g_disagreement_control_audit import run
def main():
 root=Path(__file__).resolve().parents[1]
 git=lambda *x:subprocess.check_output(("git",)+x,cwd=root,text=True).strip()
 for pin in ("da5498e628166f741e25b0ebceb9815e54220790","f5f251698ac5a6c0db190a1edc76cac0634bddc0"):
  assert git("merge-base","--is-ancestor",pin,"HEAD")==""
 assert not (root/"research/itd02_v31_heldout_evaluator.py").exists()
 source=train_source()["pretrained_shared"]
 selected=[s for s in STREAMS if s[0] in ("basic_t1","basic_t2","unchanged_t1","unchanged_t2")]
 report=[]
 for name,stages,offset in selected:
  for policy in ("scheduled","disagreement","uncertainty_rls"):
   gc.collect();tracemalloc.start();start=time.perf_counter_ns()
   x=run(name,stages,offset,source,policy)
   duration=time.perf_counter_ns()-start
   current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
   report.append({"stream":name,"policy":policy,"elapsed_ns":duration,
     "python_peak_traced_bytes":peak,"python_current_traced_bytes":current,
     "source_sha_unchanged":x["source_sha_unchanged"],
     "return_latency":x["latency"],"false_source":x["false_source"],
     "cumulative_regret":x["regret"]})
 assert len(report)==12 and all(x["source_sha_unchanged"] for x in report)
 print(json.dumps({"schema":"ygg.itd02.v31h.host_resource_observation.v1",
  "classification":"V31H_RESOURCE_OBSERVED_ACCEPTANCE_INCOMPLETE__NO_SCIENCE",
  "host_specific_timing_not_cross_host_digest":True,
  "scientific_first_use":False,"holdout_evaluated":False,
  "learned_ring_scalars":326,"rls_covariance_and_weight_numbers":6480,
  "edge_message_count":"not_measured",
  "opt_in_selector_checkpoint_cold_restore":"not_implemented",
  "complete_inherited_native_suite":False,
  "records":report},sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
