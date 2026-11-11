"""WSP-36: acquire gate semantics from queried bits; WSP35 numeric VM is unchanged."""
import importlib.util
from pathlib import Path

_parent = Path(__file__).resolve().parent.parent / "WSP-35" / "model.py"
_spec = importlib.util.spec_from_file_location("_wsp35_numeric", _parent)
_wsp35 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_wsp35)
NumericCircuit = _wsp35.NumericCircuit
GateTrainCache = _wsp35.GateTrainCache
N_INPUTS = _wsp35.N_INPUTS
GATES = _wsp35.GATES
ROW = _wsp35.ROW
MASKS = _wsp35.MASKS
bit = _wsp35.bit
table = _wsp35.table
source_spec = _wsp35.source_spec

THREE = (0, 1, 3)
TWO = (0, 1)
FOUR = (0, 1, 2, 3)

def signature(mask, positions):
    return tuple(table(mask)[k] for k in positions)

assert len(set(signature(mask, THREE) for mask in MASKS)) == len(MASKS), "WSP36_BAD_PREREG_FAMILY"

def numeric_acquire(topology, probe, rows=THREE):
    """Only graph, known family and actual probe replies are provided to this learner.

    Hidden source gate tables and composed target labels are intentionally absent.
    Returns a weight-written circuit, recovered primitive spec, and query trace.
    """
    if rows not in (THREE, TWO, FOUR):
        raise ValueError("WSP36_UNFROZEN_QUERY_SCHEDULE")
    if type(topology) is not tuple or len(topology) != GATES:
        raise ValueError("WSP36_BAD_TOPOLOGY")
    recovered, queried = [], []
    for i, route in enumerate(topology):
        if type(route) is not tuple or len(route) != 2:
            raise ValueError("WSP36_BAD_ROUTE")
        a, b = route
        if any(type(p) is not int or not 0 <= p < N_INPUTS+i for p in (a, b)):
            raise ValueError("WSP36_FORWARD_ROUTE")
        observations = {}
        for k in rows:
            observations[k] = bit(probe(i, k))
            queried.append((i, k, observations[k]))
        if rows == FOUR:
            inferred = tuple(observations[k] for k in FOUR)
        else:
            matches = sorted(mask for mask in MASKS
                             if signature(mask, rows) == tuple(observations[k] for k in rows))
            if not matches:
                raise ValueError("WSP36_CONTRADICTORY_OBSERVATION")
            # Frozen numeric tie-break: lowest mask among consistent known rules.
            inferred = table(matches[0])
        recovered.append((a, b, inferred))
    program = NumericCircuit.synthesize(tuple(recovered))
    return program, tuple(recovered), tuple(queried)

def teacher_view(hidden_spec):
    """Evaluator-side probe closure. Callers receive a function, never the source table."""
    source_spec(hidden_spec)
    receipts = []
    def probe(gate, row):
        if type(gate) is not int or not 0 <= gate < GATES:
            raise ValueError("WSP36_BAD_GATE_PROBE")
        if type(row) is not int or not 0 <= row < 4:
            raise ValueError("WSP36_BAD_ROW_PROBE")
        val = hidden_spec[gate][2][row]
        receipts.append((gate, row, val))
        return val
    return probe, receipts

def learned_weights(hidden_spec, positions):
    """Evaluator-side harness passes only a topology and bounded observation interface."""
    probe, audit = teacher_view(hidden_spec)
    topology = tuple((a, b) for a, b, _ in hidden_spec)
    circuit, recovered, transcript = numeric_acquire(topology, probe, positions)
    if tuple(audit) != transcript or len(transcript) != GATES * len(positions):
        raise AssertionError("WSP36_QUERY_CUSTODY")
    return circuit, recovered, transcript
