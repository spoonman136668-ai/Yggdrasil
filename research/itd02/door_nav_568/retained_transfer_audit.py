"""Matched retained-learning and adverse unrelated-world experiments.

World source: all 16 Boolean truth-table functions, each fully observed at
four public inputs twice (8 source interactions). Target: each of the 16
worlds; one new public outcome (at first input), evaluated on the other
three unseen target inputs. Positive same/complement relations are assessed
separately from the 224 unrelated source-target pairs. No target relationship
label reaches a model. Probe is fixed in advance, not picked using target.
"""
import json
from time import process_time_ns
from unrestricted_operation_cells import INPUTS
from retained_cell_transfer import RetainedCellTransfer
from conventional_retained_transfer import ConventionalRetainedTransfer,ScratchConventional
from multi_regime_online_comparison import deep_bytes

def truth(mask,key):
    return bool((mask>>INPUTS.index(key))&1)

def grade(predict,target_mask):
    values=[predict(key) for key in INPUTS[1:]]
    expected=[truth(target_mask,key) for key in INPUTS[1:]]
    return {
        "correct":sum(p is not None and p==y for p,y in zip(values,expected)),
        "wrong":sum(p is not None and p!=y for p,y in zip(values,expected)),
        "abstentions":sum(p is None for p in values),
    }

def trial(source_mask,target_mask):
    if (type(source_mask) is not int or type(target_mask) is not int
        or not 0<=source_mask<16 or not 0<=target_mask<16):
        raise ValueError("INVALID_FIXTURE_MASK")
    local=RetainedCellTransfer()
    table=ConventionalRetainedTransfer()
    scratch=ScratchConventional()
    clock={k:0 for k in ("local","table","scratch")}
    for key in INPUTS:
        for _ in range(2):
            observation=truth(source_mask,key)
            for name,model in (("local",local),("table",table)):
                begin=process_time_ns()
                model.train_source(key,observation)
                clock[name]+=process_time_ns()-begin
    saved=local.checkpoint()
    local=RetainedCellTransfer.restore(saved)
    before={
        "local":grade(local.predict,target_mask),
        "table":grade(table.predict,target_mask),
        "scratch":grade(scratch.predict,target_mask),
    }
    key=INPUTS[0]
    outcome=truth(target_mask,key)
    for name,model in (("local",local),("table",table),("scratch",scratch)):
        begin=process_time_ns()
        model.observe_new(key,outcome)
        clock[name]+=process_time_ns()-begin
    restored=RetainedCellTransfer.restore(local.checkpoint())
    after={
        "local":grade(local.predict,target_mask),
        "table":grade(table.predict,target_mask),
        "scratch":grade(scratch.predict,target_mask),
    }
    return {
        "source_fixture_only":source_mask,
        "target_fixture_only":target_mask,
        "relationship_diagnostic":("same" if source_mask==target_mask else
          "complement" if (source_mask^target_mask)==15 else "unrelated"),
        "source_public_actions":8,
        "target_public_actions":1,
        "heldout_target_inputs":3,
        "local_source_updates":local.source.observations,
        "local_target_updates":local.new_observations,
        "table_target_updates":table.new_observations,
        "scratch_target_updates":scratch.new_observations,
        "cold_restore_exact":all(
           local.predict(x)==restored.predict(x) for x in INPUTS),
        "checkpoint_bytes":len(local.checkpoint()),
        "python_state_bytes":{"local":deep_bytes(local.source.cells),
                              "table":deep_bytes(table.table),
                              "scratch":deep_bytes(scratch.counts)},
        "cpu_ns":clock,
        "before":before,
        "after":after,
    }

def run():
    rows=[trial(source,target) for source in range(16) for target in range(16)]
    return {
        "runs":rows,
        "scope":"All 256 source/target function pairs, 8 public source observations and 1 target probe, 3 held-out target inputs",
        "limits":"Candidate assumes uniform retention or global inversion. Unrelated functions violate that prior; no model receives relationship identity. Identical information conventional memory control. Python microtimings are not retail-hardware benchmarks.",
    }

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))
