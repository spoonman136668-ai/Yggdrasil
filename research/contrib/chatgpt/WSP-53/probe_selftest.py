"""WSP53 deterministic SELFTEST-only mechanism diagnostics.

This is a *development engineering probe*, not WSP53 DEV or PRIMARY science.
Learners never receive SourceWorld, hidden codebook, role order or target triples.
Every arm consumes the same 48 + 12 public charged experiences in each world.
The raw-bit recurrent arm is deliberately smoke-trained (96 + 48 updates), so
any apparent method advantage cannot be used as a scientific superiority claim.
"""
from __future__ import annotations
from dataclasses import asdict,dataclass
from time import perf_counter,process_time
from source import build_world
from controls import ErasedControl,WholeStreamTable
from direct_writer import SparseAcousticWriter
from warm64 import Warm64AddressWriter
from conventional import RawBitRNN

@dataclass(frozen=True)
class Score:
    total:int
    correct:int
    abstain:int
    wrong_confident:int

    def __post_init__(self):
        if self.total!=self.correct+self.abstain+self.wrong_confident:
            raise AssertionError("score accounting drift")

def score(model,heldout):
    correct=unknown=wrong=0
    for row in heldout:
        result=model.predict(row.before,row.acoustic_bits)
        if result is None:
            unknown+=1
        elif result==row.after:
            correct+=1
        else:
            wrong+=1
    return Score(len(heldout),correct,unknown,wrong)

def run_selftest(*, family,seed,encoding):
    if type(seed) is not int or seed not in (9901,9902):
        raise PermissionError("SELFTEST-only certified fixture seeds")
    if family not in ("anchored_effect","noncommuting_order") or encoding not in ("identity","permuted","rotated"):
        raise PermissionError("unapproved fixture")
    world=build_world(family,"SELFTEST",seed,encoding)
    world.audit()
    models={
        "pure_direct":SparseAcousticWriter(family=family,mode="pure_direct"),
        "count_only":SparseAcousticWriter(family=family,mode="count_only"),
        "random_address":SparseAcousticWriter(family=family,mode="random_address"),
        "lookup":WholeStreamTable(family=family),
        "erase":ErasedControl(family=family),
        "warm64_direct":Warm64AddressWriter(family=family),
        "conventional_smoke":RawBitRNN(family=family),
    }
    results={}
    for name,model in models.items():
        t0=perf_counter();c0=process_time()
        for row in world.phase_a:
            model.observe(row)
        if name=="warm64_direct":
            model.seal_a()
        if name=="conventional_smoke":
            model.seal_a()
            model.train(96)
        a=score(model,world.heldout_a)
        for row in world.phase_b:
            model.observe(row)
        if name=="conventional_smoke":
            model.train(48)
        b=score(model,world.heldout_b)
        retained=score(model,world.heldout_a)
        actions=(model.actions if hasattr(model,"actions") else
                 (len(model.rows) if hasattr(model,"rows") else -1))
        if actions!=60:
            raise AssertionError(f"{name} consumed {actions}, not 60 actions")
        cold=None
        if name!="erase":
            restored=type(model).restore(model.snapshot())
            cold=(score(restored,world.heldout_a)==retained and
                  score(restored,world.heldout_b)==b)
            if not cold:
                raise AssertionError(name+" cold restore divergence")
        cpu=process_time()-c0;wall=perf_counter()-t0
        results[name]={
            "a":asdict(a),"b":asdict(b),"a_retained":asdict(retained),
            "actions":actions,"gradient_updates":getattr(model,"updates",0),
            "persistent_bits":(model.capacity_bits() if hasattr(model,"capacity_bits") else 0),
            "wall_seconds":round(wall,5),"cpu_seconds":round(cpu,5),
            "cold_restore_parity":cold,
        }
        if name=="conventional_smoke":
            results[name]["train_diagnostic"]=model.train_diagnostic()
        if name=="warm64_direct" and model.updates!=64:
            raise AssertionError("warm64 drift")
    return {
        "schema":"wsp53.selftest-probe.v1","classification":"ENGINEERING_DIAGNOSTIC_NOT_SCIENCE",
        "cohort":"SELFTEST","source":world.source_receipt(),
        "comparators_qualified":False,"development_admitted":False,
        "conventional_fully_trained":False,"protected_primary_used":False,
        "arms":results,
    }
