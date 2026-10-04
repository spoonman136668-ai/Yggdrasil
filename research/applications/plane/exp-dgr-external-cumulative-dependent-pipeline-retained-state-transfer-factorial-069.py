"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-RETAINED-STATE-TRANSFER-FACTORIAL-069."""
import argparse
import json
import math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-RETAINED-STATE-TRANSFER-FACTORIAL-069"
PRIOR_PATH=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-indexed-collateral-state-transport-attribution-068.py")
RETAINED_KEY=bytes((10,32,32,32))
RETAINED_BEST=32
NEEDLE='active_guard=tuple(list(original_guard[:6])+[RETAINED_KEY]);active_used=True'

def context_stats(data):
    split=len(data)*60//100
    train=data[:split];ev=data[split:]
    def scan(buf):
        occ=0;succ=[0]*256
        for i in range(0,max(0,len(buf)-3)):
            if buf[i:i+4]==RETAINED_KEY:
                occ+=1
                if i+4<len(buf):succ[buf[i+4]]+=1
        best=max(range(256),key=lambda x:(succ[x],-x)) if any(succ) else -1
        return occ,sum(succ),best,max(succ) if succ else 0
    return scan(train),scan(ev)

def run_variant(root,pos):
    base=PRIOR_PATH.read_text(encoding="utf-8")
    if base.count(NEEDLE)!=1:raise RuntimeError("PRIOR_ACTIVATION_LINE_NOT_EXACT")
    repl=f'active_guard=tuple(list(original_guard[:{pos}])+[RETAINED_KEY]+list(original_guard[{pos+1}:]));active_used=True'
    source=base.replace(NEEDLE,repl,1)
    ns={"__name__":"y68_position_variant","__file__":str(PRIOR_PATH)}
    exec(compile(source,str(PRIOR_PATH),"exec"),ns)
    return ns["run"](root)

def run(root):
    prose=(Path(root)/"technical-prose.bin").read_bytes()
    train_stats,eval_stats=context_stats(prose)
    metrics={
      "position_variant_count":7.0,
      "prose_train_retained_key_occurrence_count":float(train_stats[0]),
      "prose_train_retained_key_successor_observation_count":float(train_stats[1]),
      "prose_train_retained_key_argmax_successor":float(train_stats[2]),
      "prose_train_retained_key_argmax_count":float(train_stats[3]),
      "prose_eval_retained_key_occurrence_count":float(eval_stats[0]),
      "prose_eval_retained_key_successor_observation_count":float(eval_stats[1]),
      "position_max_positive_prose_collateral_schedule_count":0.0,
      "position_rank7_positive_prose_collateral_schedule_count":0.0,
      "position_max_partner_collateral_failure_count":0.0,
      "all_variant_invalid_evaluation_rows":0.0,
      "all_variant_source_identity_mismatch_count":0.0,
      "all_variant_transport_identity_mismatch_count":0.0,
      "capacity_growth_event_count":0.0,
      "external_model_call_count":0.0,
      "tokenizer_use_count":0.0,
      "heldout_position_selection_count":0.0,
      "row_synthesis_count":0.0,
    }
    variants=[]
    for pos in range(7):
        r=run_variant(root,pos);m=r["metrics"]
        prose_count=float(m["active_positive_prose_collateral_schedule_count"])
        partner=float(m["active_partner_collateral_failure_count"])
        k=f"position_rank{pos+1}"
        metrics[k+"_positive_prose_collateral_schedule_count"]=prose_count
        metrics[k+"_partner_collateral_failure_count"]=partner
        metrics[k+"_mean_first_success_packet"]=float(m["active_mean_first_success_packet"])
        metrics["position_max_positive_prose_collateral_schedule_count"]=max(metrics["position_max_positive_prose_collateral_schedule_count"],prose_count)
        metrics["position_max_partner_collateral_failure_count"]=max(metrics["position_max_partner_collateral_failure_count"],partner)
        metrics["all_variant_invalid_evaluation_rows"]+=float(m["invalid_evaluation_rows"])
        metrics["all_variant_source_identity_mismatch_count"]+=float(m["source_identity_mismatch_count"]+m["transfer_manifest_identity_mismatch_count"])
        metrics["all_variant_transport_identity_mismatch_count"]+=float(m["transported_state_identity_mismatch_count"])
        metrics["capacity_growth_event_count"]+=float(m["capacity_growth_event_count"])
        metrics["external_model_call_count"]+=float(m["external_model_call_count"])
        metrics["tokenizer_use_count"]+=float(m["tokenizer_use_count"])
        if pos==6:metrics["position_rank7_positive_prose_collateral_schedule_count"]=prose_count
        variants.append({"rank":pos+1,"metrics":m})
    activation=(metrics["position_max_positive_prose_collateral_schedule_count"]>metrics["position_rank7_positive_prose_collateral_schedule_count"])
    no_position_rescue=(metrics["position_max_positive_prose_collateral_schedule_count"]==0)
    payload=(no_position_rescue and train_stats[0]>0 and train_stats[2]>=0 and train_stats[2]!=RETAINED_BEST)
    context=(no_position_rescue and train_stats[0]==0)
    flags=[activation,payload,context]
    if sum(bool(x) for x in flags)>1:attribution="MULTIPLE"
    elif activation:attribution="ACTIVATION_POSITION"
    elif payload:attribution="PAYLOAD_MISMATCH"
    elif context:attribution="TARGET_CONTEXT_MISMATCH"
    else:attribution="UNRESOLVED"
    metrics["activation_position_attribution_flag"]=float(activation)
    metrics["payload_mismatch_attribution_flag"]=float(payload)
    metrics["target_context_mismatch_attribution_flag"]=float(context)
    metrics["multiple_attribution_flag"]=float(attribution=="MULTIPLE")
    metrics["unresolved_attribution_flag"]=float(attribution=="UNRESOLVED")
    if any(not math.isfinite(float(v)) for v in metrics.values()):raise RuntimeError("NONFINITE_METRIC")
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"attribution":attribution,"metrics":metrics,"variants":variants}

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:json.dump(run(a.root),f,allow_nan=False,separators=(",",":"),sort_keys=True)

if __name__=="__main__":main()
