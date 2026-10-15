"""Y-F56 independent FIT-only online/offline receipt and threshold recount."""
import json,sys
def audit(path,prereg):
 d=json.load(open(path));p=json.load(open(prereg))
 assert d["schema"]=="yggdrasil.f56.online-constructive-arrival.fitonly.v1"
 assert d["cases"]==len(d["rows"])==p["fit"]["expected_streams"]==64
 assert d["FIT_seeds"]==p["fit"]["seeds"]
 assert d["FIT_families"]==p["fit"]["families"]
 assert d["source_query_hidden_until_retention"]
 assert d["all_DIAG_untouched"] and d["originals_untouched"]
 assert not d["source_independent_F3"] and d["native_total_576B_unverified"]
 assert d["online_min_gate"]==p["feasibility_first"]["FIT_only_fixed_online_constructive_min_accuracy"]
 assert d["offline_min_gate"]==p["feasibility_first"]["FIT_only_offline_public_min_accuracy"]
 count_online=count_offline=0;seen=set();regime_count={}
 for row in d["rows"]:
  key=row["seed"],row["family"]
  assert key not in seen;seen.add(key)
  assert p["fit"]["seeds"][0]<=key[0]<p["fit"]["seeds"][1] and key[1] in p["fit"]["families"]
  assert row["regime"] in p["fit"]["public_arrival_regimes"]
  regime_count[row["regime"]]=regime_count.get(row["regime"],0)+1
  assert row["online_correct"] in (0,1) and row["offline_correct"] in (0,1)
  assert 0<=row["online_records"]<=p["stream"]["records_max"]
  assert row["online_bytes"]==12*row["online_records"]<=p["stream"]["serialized_payload_budget_bytes"]
  assert row["offline_bytes"]<=p["stream"]["serialized_payload_budget_bytes"]
  count_online+=row["online_correct"];count_offline+=row["offline_correct"]
 assert len(seen)==64 and len(regime_count)==2
 assert count_online==d["online_constructive_correct"]
 assert count_offline==d["offline_reference_correct"]
 assert abs(d["online_accuracy"]-count_online/64)<1e-12
 assert abs(d["offline_accuracy"]-count_offline/64)<1e-12
 qualified=count_online/64>=d["online_min_gate"] and count_offline/64>=d["offline_min_gate"]
 assert qualified==d["frozen_fit_gate_met"]
 print("Y_F56_FIT_ONLY_FEASIBILITY",json.dumps(dict(online_correct=count_online,offline_correct=count_offline,regimes=regime_count,source_feasible=qualified),sort_keys=True))
if __name__=="__main__":
 assert len(sys.argv)==3
 audit(*sys.argv[1:])
