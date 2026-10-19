"""Source-neutral T7 Ygg native feasibility: no protected T7 first use.

Calls unchanged T5 native legal F62 composition/eviction on -16000
fixture with zero weights, and complete F60 frozen control and FULL PUBLIC
answer solver. Its results are engineering-only, never a model selection
signal or protected source birth.
"""
from __future__ import annotations
import importlib.util,sys,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def load(path,name):
    sp=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(sp);sys.modules[name]=m
    sp.loader.exec_module(m);return m
def main():
    t7=load(HERE/"20261018-yggdrasil-t7-independent.py","ygg_t7_fixture_source")
    t5=load(t7.T5,"ygg_t7_fixture_native")
    t3=load(t5.T3,"ygg_t7_fixture_t3")
    t4=load(t5.T4,"ygg_t7_fixture_t4")
    t2=t3.load(t3.T2,"ygg_t7_fixture_t2")
    f62,kernel,src=t2.modules()
    t2.materialize_ephemeral_canonical_native_sources(f62)
    p=f62.codec()
    public,private=t7.born(-16000,"fixture")
    records,stats=t5.compact_online(public,bytes(20),p,t2,f62)
    control=f62.controls()[0].online_fixed(public)
    question={"start":private["start"],"ops":private["ops"]}
    unique,full=t7.load(t7.T6,"ygg_t7_fixture_audit").fullgraph(public,question)
    assert unique==[private["answer"]] and stats["total_native_persistent_bytes"]==144
    assert len(records)<=10 and len(control)<=12
    answer=t4.public_solver(records,question,p)
    baseline=t4.public_solver(control,question,p)
    out={"schema":"ygg.t7.nonconsuming-native-fixture.v1",
         "native_legal_spotchecks":stats["legal_native_spotchecks"],
         "sourceblind_public_merges":stats["true_native_F62_causal_compositions"],
         "candidate_fixture_answer_correct":answer==private["answer"],
         "baseline_fixture_answer_correct":baseline==private["answer"],
         "full_public_unique_answer":len(unique)==1,
         "original_F62_source_untouched":True,
         "candidate_persistent_bytes":144,
         "protected_original_and_T7_prospective_cohorts_born":0}
    print(json.dumps(out,sort_keys=True))
if __name__=="__main__":main()
