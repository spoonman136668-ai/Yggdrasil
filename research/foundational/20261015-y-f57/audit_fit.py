"""Source-free Y-F57 FIT online/offline feasibility audit."""
import json,sys
def verify(result,pre):
 d=json.load(open(result));p=json.load(open(pre))
 assert d["schema"]=="yggdrasil.f57.boundary-complete-online.fitonly.v1"
 assert d["FIT_seeds"]==p["fit"]["seeds"]
 assert d["FIT_families"]==p["fit"]["families"]
 assert d["cases"]==len(d["rows"])==p["fit"]["expected_cases"]==64
 assert d["witness_split"]==p["public_offline_reference"]["four_paths_each_split"]==[4,2,2]
 assert d["offline_records_per_stream"]==12
 assert d["previous_F56_experiment_never_reused"]
 assert d["source_query_hidden_until_retention"]
 assert d["all_DIAG_untouched"] and d["originals_untouched"]
 assert not d["source_independent_F3"] and d["native_total_576B_unverified"]
 seen=set();sums=[0,0];regimes=set()
 for row in d["rows"]:
  key=row["seed"],row["family"]
  assert key not in seen;seen.add(key)
  assert p["fit"]["seeds"][0]<=key[0]<p["fit"]["seeds"][1]
  assert key[1] in p["fit"]["families"]
  assert row["regime"] in p["fit"]["arrival_regimes"]
  regimes.add(row["regime"])
  assert row["online_correct"] in (0,1) and row["offline_correct"] in (0,1)
  assert 0<=row["online_records"]<=p["stream"]["max_records"]
  assert row["online_bytes"]==12*row["online_records"]<=144
  assert row["offline_bytes"]==144
  sums[0]+=row["online_correct"];sums[1]+=row["offline_correct"]
 assert len(seen)==64 and len(regimes)==2
 assert d["online_constructive_correct"]==sums[0] and d["offline_reference_correct"]==sums[1]
 assert abs(d["online_accuracy"]-sums[0]/64)<1e-12
 assert abs(d["offline_accuracy"]-sums[1]/64)<1e-12
 expected=(sums[0]/64>=p["FIT_source_thresholds"]["causal_fixed_online_accuracy_min"]
      and sums[1]/64>=p["FIT_source_thresholds"]["public_offline_accuracy_min"])
 assert d["frozen_fit_gate_met"]==expected
 print("Y_F57_FIT_FEASIBILITY",json.dumps(dict(online=sums[0],offline=sums[1],qualified=expected),sort_keys=True))
if __name__=="__main__":
 assert len(sys.argv)==3
 verify(sys.argv[1],sys.argv[2])
