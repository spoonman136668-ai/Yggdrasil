"""MG94-Z paired public-message value assay. Development only.

For each public sequence, route-on and route-off counterfactual predictors
receive identical observations. This evaluates realized message utility, NOT a
deployable learner or evidence for native causal discovery. Route benefit is
measured by later prediction accuracy minus a fixed per-message cost.
"""
from consequential_routing import Cells
from itertools import product

def assay(sequence, message_cost=1):
    if type(message_cost) is not int or message_cost < 0:
        raise ValueError("INVALID_MESSAGE_COST")
    on, off = Cells(True), Cells(False)
    on_correct = off_correct = 0
    changes = 0
    for bit in sequence:
        p_on, p_off = on.step(bit), off.step(bit)
        on_correct += int(p_on == bit)
        off_correct += int(p_off == bit)
        changes += int(p_on != p_off)
    return {
        "on_correct": on_correct, "off_correct": off_correct,
        "messages": on.messages, "prediction_changes": changes,
        "net_delta": on_correct-off_correct-message_cost*on.messages,
    }

def run():
    streams = {
        "stable": [0]*24, "reversal": [0]*8+[1]*16,
        "recurrence": [0]*8+[1]*8+[0]*8,
        "alternating": [0,1]*12,
        "blocks2": [0,0,1,1]*6,
        "irregular": [0,1,0,0,1,1]*4,
    }
    measured = {name: assay(seq) for name,seq in streams.items()}
    assert measured["stable"]["net_delta"] == 0
    assert measured["blocks2"]["messages"] > 0
    # Controls are evaluated on the same public outcomes and with a fixed cost;
    # this paired hindsight score must never be used to choose a message online.
    return measured

if __name__ == "__main__":
    import json
    print(json.dumps(run(),sort_keys=True,indent=2))
