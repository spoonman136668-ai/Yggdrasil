"""Y-F55 full FIT-only model-vs-controls feasibility and source-free replay.

Evaluates exclusively registered FIT 611000..611015/families 1120..1123.
A single model is learned on FIT (optimistically in-sample); no DIAG/F3/original.
The auditor is imported only to independently replay public events, decode
persisted records, and reconstruct answers; the auditor itself never imports
the experiment generator. All zero/negative findings remain valid findings.
"""
import importlib.util,json,sys
from pathlib import Path
here=Path(__file__).resolve().parent
def load(name,filename):
    s=importlib.util.spec_from_file_location(name,here/filename)
    m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
    return m
m=load("y55_fit_screen_source","source_pilot.py")
a=load("y55_fit_screen_public_reviewer","audit_result.py")
def run():
    q,n,pos=m.train()
    assert n>1000 and pos>0
    assert len(q)==8
    scores={arm:0 for arm in m.ARMS}
    by_family={str(f):{arm:0 for arm in m.ARMS} for f in m.base.FIT_FAM}
    reference=0;rows=[]
    for seed in m.base.FIT:
        for fam in m.base.FIT_FAM:
            public,question,paths=m.base.source(seed,fam)
            assert len(public)==72 and len(paths)==4
            ref,work=m.base.witness(public)
            assert len(ref)==12 and work>72
            offline=int(m.codec.solve(ref,question)==question["answer"])
            assert offline==int(a.solve(ref,question)==question["answer"])
            reference+=offline
            outcomes={};receipts={}
            for arm in m.ARMS[:-1]:
                mem,ops=m.retain_online(public,arm,q,debug=True)
                mirror,count=a.replay_online(public,arm,q)
                assert mem==tuple(mirror) and ops==count
                a.public_witness(mem,public)
                assert len(mem)<=12 and all(len(m.codec.pack(*r))==12 for r in mem)
                result=int(m.codec.solve(mem,question)==question["answer"])
                assert result==int(a.solve(mem,question)==question["answer"])
                outcomes[arm]=result
                receipts[arm]=len(mem)
                scores[arm]+=result;by_family[str(fam)][arm]+=result
            outcomes[m.ARMS[-1]]=1;scores[m.ARMS[-1]]+=1
            by_family[str(fam)][m.ARMS[-1]]+=1
            rows.append(dict(seed=seed,family=fam,results=outcomes,
                             retained_counts=receipts,public_reference_correct=offline))
    assert len(rows)==64
    fair=m.ARMS[1:-1];best=max(fair,key=lambda arm:scores[arm])
    gain=(scores[m.ARMS[0]]-scores[best])/64
    return dict(schema="yggdrasil.f55.full-fit-online-causal-screen.v1",
        stage="FIT_IN_SAMPLE_ONLY_SOURCE_FREE_REPLAY_NO_DIAG",
        source_files_frozen_no_refit_on_diagnostic=True,
        fit_seeds=[m.base.FIT.start,m.base.FIT.stop],
        fit_families=list(m.base.FIT_FAM),fit_cases=len(rows),
        learned_weights_int8=list(q),learned_positive_examples=pos,
        fit_labeled_examples=n,score_by_arm=scores,by_family=by_family,
        public_offline_constructive_reference_correct=reference,
        strongest_online_equal_byte_fair=best,
        in_sample_candidate_gain=gain,
        initial_fit_go_nogo_advisory=(
            "FIT_METHOD_WEAK_REDESIGN_NEW_PREREG_BEFORE_DIAG" if scores[m.ARMS[0]]==0
            else "FIT_NONZERO_NEEDS_PROSPECTIVE_QUALIFICATION"),
        diagnostic_source_UNTOUCHED=[m.base.DIAG.start,m.base.DIAG.stop],
        primary_original_NOT_RESERVED=[m.base.ORIGINAL.start,m.base.ORIGINAL.stop],
        source_independent_F3=False,accepted_ref_mutation=False,
        live_optimizer_promotion=False,paid_api_calls=0,rows=rows)
if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1]!="--fit-only":
        raise SystemExit("only FIT-only screen authorized")
    print(json.dumps(run(),sort_keys=True))
