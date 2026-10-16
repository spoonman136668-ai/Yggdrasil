"""F63C frozen public-path stability model; no future questions or heldout reads.

Synthetic guard before authentic fitting. Authentic path accepts ONLY the
already-archived FIT TRAIN rows whose exact SHA256 was independently verified.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
SOURCE_SHA="c04b73306861098eecf55db77b2db486aa918819"
PREREG_SHA="c0e69c1bc0a170646c8ad997efeb154b64ce9862"
TRAIN_ROWS_SHA256="f977ff5b7514de2c3ff3b213f414a27939890e409855bcce9df2041e28a714a7"
FIT_TRAIN_RUN=38884921783
def gitblob(p):
 b=p.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def load(name,path):
 sp=importlib.util.spec_from_file_location(name,path)
 o=importlib.util.module_from_spec(sp);sys.modules[name]=o;sp.loader.exec_module(o);return o
assert gitblob(HERE/"source.py")==SOURCE_SHA
assert gitblob(HERE/"prereg.json")==PREREG_SHA
source=load("f63c_fit_frozen_source",HERE/"source.py")
learn=load("f63c_fit_sha_pinned_public_reliability",HERE.parent/"20261016-y-f63"/"learn_reliability.py")
auditor=load("f63c_fit_independent_public_replay",HERE.parent/"20261015-y-f62"/"audit_public.py")
def _train(publics):
    examples=[]
    for public in publics:
        assert len(public)==72 and all(len(ev)==3 for ev in public)
        examples.extend(learn.examples_from_public(public))
    assert examples
    weights=[0.0]*4
    # Same fixed objective/updates as the earlier synthetic-only algorithm.
    for _ in range(3):
        for features,target in examples:
            x=[min(v,16)/16 for v in features]
            predicted=sum(w*f for w,f in zip(weights,x))
            error=target/3-predicted
            for j in range(4):
                weights[j]+=.01*error*x[j]
    quant=tuple(max(-127,min(127,round(w*32))) for w in weights)
    assert len(quant)==4 and all(-127<=w<=127 for w in quant)
    return quant,len(examples)
def synthetic_guard():
    publics=[]
    guards=[]
    for seed,family in ((-501,-2),(-502,-1),(-503,-2),(-504,-1),
                        (-505,-2),(-506,-1),(-507,-2),(-508,-1)):
        public,q,_=source.source(seed,family)
        publics.append(public)
        guards.append((public,q))
    weights,n=_train(publics)
    for public,question in guards:
        retained,trace=learn.m.select(public,learn.packing,weights,True)
        assert auditor.verify(public,question,trace)["prefixes"]==72
        assert len(retained)*12<=144
    return dict(schema="yggdrasil.f63c.fit-algorithm-synthetic-guard.v1",
     stage="UNREGISTERED_SYNTHETIC_ONLY",synthetic_cases=len(publics),
     examples=n,weights=list(weights),registered_fit_access=False,
     validation_executed=False,independent_F3=False)
def fit_from_archive(input_path):
    data=input_path.read_bytes()
    assert hashlib.sha256(data).hexdigest()==TRAIN_ROWS_SHA256,"ARCHIVE_DATA_IDENTITY_DRIFT"
    raw=[json.loads(line) for line in data.decode("utf-8").splitlines()]
    assert len(raw)==32
    identities={(r["seed"],r["family"]) for r in raw}
    expected={(seed,family) for seed in range(801000,801008) for family in (1540,1541,1542,1543)}
    assert identities==expected,"OUT_OF_BOUNDS_TRAIN_DATA"
    # Project only raw public events: future question, truth/score and labels
    # are never passed into the learning function or its feature extractor.
    public_cases=[tuple(tuple(ev) for ev in row["public_events"]) for row in raw]
    weights,n=_train(public_cases)
    return dict(schema="yggdrasil.f63c.frozen-public-path-reliability-fit.v1",
     source_blob=SOURCE_SHA,prereg_blob=PREREG_SHA,
     training_artifact=12039381339,training_run=FIT_TRAIN_RUN,
     training_rows_sha256=TRAIN_ROWS_SHA256,train_cases=32,
     public_only_structural_training_examples=n,weights=list(weights),
     weights_sha256=hashlib.sha256(bytes(w%256 for w in weights)).hexdigest(),
     fit_train_only=True,fit_validation_executed=False,
     diagnostics_executed=False,originals_executed=False,
     scientific_improvement_qualified=False,independent_F3=False,
     optimize_against_future_query_labels=False,policy_promotion=False)
if __name__=="__main__":
 parser=argparse.ArgumentParser()
 modes=parser.add_mutually_exclusive_group(required=True)
 modes.add_argument("--synthetic-only",action="store_true")
 modes.add_argument("--fit-evidence",type=pathlib.Path)
 args=parser.parse_args()
 print(json.dumps(synthetic_guard() if args.synthetic_only else fit_from_archive(args.fit_evidence),sort_keys=True))
