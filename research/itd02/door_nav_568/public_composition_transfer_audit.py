"""Two-stage publicly observable causal composition with matched controls.

Eight independent pair-outcome calibrations, then three final-outcome
configurations each observed twice. Held-out fourth composition is never
shown to either learner before evaluation. All 22 interactions counted.
The candidate and conventional factorized learner have the same observable
subcause supervision and affine hypothesis class; exact table does not
exploit subcause feedback.
"""
import json
from time import process_time_ns
from compositional_local_cells import CompositionalLocalCells
from conventional_composition_controls import ConventionalFactorized,ConventionalExactTable
from multi_regime_online_comparison import deep_bytes

PAIRS=((False,False),(False,True),(True,False),(True,True))
FRAMES={value: ((False,False) if not value else (True,False))
        for value in (False,True)}

def trial(heldout=(True,True),bias=False):
    if heldout not in ((False,False),(True,False),(False,True),(True,True)):
        raise ValueError("HELDOUT_CONFIG_INVALID")
    candidate=CompositionalLocalCells()
    factor=ConventionalFactorized()
    exact=ConventionalExactTable()
    times={"native":0,"factorized":0,"tabular":0}
    pair_actions=final_actions=0
    for index in range(2):
        for pair in PAIRS:
            result=pair[0]^pair[1]
            for _ in range(2):
                start=process_time_ns()
                candidate.observe_pair(index,pair,result)
                times["native"]+=process_time_ns()-start
                start=process_time_ns()
                factor.observe_pair(index,pair,result)
                times["factorized"]+=process_time_ns()-start
                pair_actions+=1
    compositions=[(False,False),(False,True),(True,False),(True,True)]
    for messages in compositions:
        if messages==heldout:continue
        frame=FRAMES[messages[0]]+FRAMES[messages[1]]
        result=messages[0]^messages[1]^bias
        for _ in range(2):
            start=process_time_ns()
            candidate.observe_final(frame,result)
            times["native"]+=process_time_ns()-start
            start=process_time_ns()
            factor.observe_final(frame,result)
            times["factorized"]+=process_time_ns()-start
            start=process_time_ns()
            exact.observe_final(frame,result)
            times["tabular"]+=process_time_ns()-start
            final_actions+=1
    testframe=FRAMES[heldout[0]]+FRAMES[heldout[1]]
    correct=heldout[0]^heldout[1]^bias
    outcomes={}
    for name,result in (("native",candidate.predict(testframe)),
                        ("factorized",factor.predict(testframe)),
                        ("tabular",exact.predict(testframe))):
        outcomes[name]={"correct":int(result is not None and result==correct),
                        "wrong":int(result is not None and result!=correct),
                        "abstention":int(result is None)}
    return {
        "heldout":list(heldout),"bias":bias,
        "public_pair_actions":pair_actions,"public_final_actions":final_actions,
        "total_public_actions":pair_actions+final_actions,
        "native_observations":candidate.observations(),
        "factorized_observations":factor.observations,
        "tabular_final_observations":exact.observations,
        "native_coefficients":candidate.exchange.coefficients(),
        "native_messages":candidate.messages(testframe),
        "heldout_results":outcomes,
        "cpu_ns":times,
        "native_python_bytes":deep_bytes((candidate.pair_cells,candidate.exchange.equations)),
        "factorized_python_bytes":deep_bytes((factor.pairs,factor.final)),
        "tabular_python_bytes":deep_bytes(exact.values),
    }

def run():
    rows=[trial(heldout,bias) for heldout in
          ((False,False),(False,True),(True,False),(True,True))
          for bias in (False,True)]
    return {"runs":rows,
            "scope":"Eight held-out two-stage compositions; completed public intermediate and terminal outcomes, independent conventional factorization",
            "limits":"Handcrafted binary public subcause probes and affine compositional hypothesis; this is not autonomous discovery, original DoorKey, or demonstrated native superiority."}
if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))
