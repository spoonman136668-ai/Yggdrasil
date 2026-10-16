"""F61 one-shot WITHIN-FIT validation source, not DIAG or original.

Frozen training 741000..741007; validation 741008..741015, both families
1420..1423. Future query is only passed to the evaluation/solving routine
after each public-only memory policy has completely frozen its 12-record state.

FIT validation is permitted solely by the separate explicit first-use workflow.
This module deliberately has no DIAG or protected-original entry point.
"""
import importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("f61_frozen_candidate_for_validation",HERE/"source_pilot.py")
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
def run():
    weights,n,pos=m.learn()
    rows=[];score={arm:0 for arm in m.ARMS}
    per_family={str(f):{arm:0 for arm in m.ARMS} for f in m.FAMILIES}
    ablated_success=0
    for seed in m.VALIDATE:
        for family in m.FAMILIES:
            tagged,question,_paths,regime=m.source(seed,family)
            assert len(tagged)==72 and sum(row[3] for row in tagged)==36
            public=tuple(x[:3] for x in tagged)
            # Retention APIs only receive public edge triples and weights.
            learned,work=m.learned_online(public,weights)
            memory_by_arm={m.ARMS[0]:learned}
            for arm in m.ARMS[1:6]:
                memory_by_arm[arm]=m.fixed_online(public,arm)
            memory_by_arm[m.ARMS[6]]=m.f60.offline_public_witness(public)
            receipts={}
            answers={}
            for arm in m.ARMS[:7]:
                retained=memory_by_arm[arm]
                assert len(retained)<=12 and all(len(m.codec.pack(*r))==12 for r in retained)
                receipts[arm]=[m.codec.pack(*r).hex() for r in retained]
                answers[arm]=int(m.codec.solve(retained,question)==question["answer"])
            # Private future-query oracle only scores after all retention.
            answers[m.ARMS[7]]=1
            ablated=[x for x in learned if len(x[2])==1]
            ablated_success+=int(m.codec.solve(ablated,question)==question["answer"])
            for arm in m.ARMS:
                score[arm]+=answers[arm]
                per_family[str(family)][arm]+=answers[arm]
            rows.append(dict(seed=seed,family=family,regime=regime,
                public_events=[list(x) for x in public],
                public_tags=[x[3] for x in tagged],
                question=dict(start=question["start"],ops=[list(x) for x in question["ops"]],
                              answer=question["answer"]),
                retained_record_receipts=receipts,answers=answers,
                learned_online_candidate_proposals=work,
                learned_retrieval_without_composed_records=int(
                    m.codec.solve(ablated,question)==question["answer"])))
    assert len(rows)==32
    fair=m.ARMS[1:6]
    winner=max(fair,key=lambda arm:score[arm])
    improvement=(score[m.ARMS[0]]-score[winner])/len(rows)
    no_family=all(per_family[str(f)][m.ARMS[0]]>=
        max(per_family[str(f)][a] for a in fair) for f in m.FAMILIES)
    ablation=(score[m.ARMS[0]]-ablated_success)/len(rows)
    offline_ok=score[m.ARMS[6]]/len(rows)>=.85
    causal_ok=score[m.ARMS[1]]/len(rows)>=.25
    passed=(offline_ok and causal_ok and improvement>=.05 and no_family and ablation>0)
    return dict(schema="yggdrasil.f61.learned-query-utility.fit-validation.v1",
        stage="ONCE_ONLY_DISJOINT_WITHIN_FIT_VALIDATION_NO_DIAG_NO_ORIGINAL",
        fit_training_seeds=[m.TRAIN.start,m.TRAIN.stop],
        fit_validation_seeds=[m.VALIDATE.start,m.VALIDATE.stop],
        fit_families=list(m.FAMILIES),
        diagnostic_seeds_NOT_AUTHORIZED=[m.DIAG.start,m.DIAG.stop],
        original_seeds_NOT_RESERVED=[m.ORIGINAL.start,m.ORIGINAL.stop],
        learned_int8_parameters=list(weights),model_parameter_bytes=12,
        training_examples=n,training_positive_labels=pos,
        serialized_memory_max_bytes=144,serialized_record_bytes=12,
        rows=rows,cases=len(rows),scores=score,by_family=per_family,
        strongest_equal_byte_online_control=winner,
        learned_gain_over_strongest=improvement,
        composed_retrieval_ablation_gain=ablation,
        family_nondegradation=no_family,
        public_full_graph_reference_noncompetitive=True,
        public_offline_source_feasible=offline_ok,
        fixed_online_source_feasible=causal_ok,
        frozen_fit_learning_gate_met=passed,
        verdict=("FIT_VALIDATION_LEARNED_QUERY_VALUE_SUPPORTED_NOT_F3"
                 if passed else "FIT_VALIDATION_LEARNED_QUERY_VALUE_NEGATIVE"),
        query_hidden_until_retention_complete=True,
        physically_qualified_whole_native_576B=False,
        independent_F3=False,primary_original_executed=False,
        accepted_ref_mutation=False,live_optimizer_promotion=False,
        paid_API_or_Codex=False)
if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1]!="--once-only-frozen-fit-validation":
        raise SystemExit("only a single frozen FIT validation gate is permitted")
    print(json.dumps(run(),sort_keys=True))
