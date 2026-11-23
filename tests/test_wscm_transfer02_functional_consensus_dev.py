"""Source-free functional-consensus regression; original native first-use prohibited."""
import importlib.util
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / 'research' / 'contrib'
          / 'chatgpt' / 'WSCM-TRANSFER-02' / 'composition_wire_dev.py')
SPEC = importlib.util.spec_from_file_location('wscm_consensus_dev', SOURCE)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
propose = MOD.propose_two_step_composition
AND = (0, 0, 0, 1)
FIRST_BIT = (0, 0, 1, 1)
XOR = (0, 1, 1, 0)

class Ledger:
    def __init__(self, first=AND, second=AND):
        self.rows = {1301: first, 22007: second}
    def observed_external_fixture_value(self, view, action):
        table = self.rows.get(action)
        return None if table is None else table[2*view[0]+view[1]]

def trace(first, second, starts=((0,0),(0,1)), wire='output_then_x'):
    out = []
    for ordinal, (x,y) in enumerate(starts, 1):
        k = first[2*x+y]
        middle = {'output_then_x':(k,x), 'output_then_y':(k,y),
                  'x_then_output':(x,k), 'y_then_output':(y,k)}[wire]
        out.append({'source_id':f'{ordinal:064x}', 'public_view':[x,y],
                    'first_outcome':k, 'second_public_view':list(middle),
                    'second_outcome':second[2*middle[0]+middle[1]]})
    return tuple(out)

def independent_symbolic(first, second, rows, query):
    possibilities=[]
    x,y=query
    for name in ('output_then_x','output_then_y','x_then_output','y_then_output'):
        supports=True
        for row in rows:
            a,b=row['public_view']
            bit=first[2*a+b]
            mid={'output_then_x':(bit,a),'output_then_y':(bit,b),
                 'x_then_output':(a,bit),'y_then_output':(b,bit)}[name]
            supports &= (list(mid)==row['second_public_view'])
        if supports:
            k=first[2*x+y]
            mid={'output_then_x':(k,x),'output_then_y':(k,y),
                 'x_then_output':(x,k),'y_then_output':(y,k)}[name]
            possibilities.append(second[2*mid[0]+mid[1]])
    return possibilities[0] if possibilities and len(set(possibilities))==1 else None

class FunctionalConsensusDev(unittest.TestCase):
    def call(self, rows=None, second=AND, *, query=None, flag=True, native=None):
        return propose(Ledger(AND,second) if native is None else native, 1301,
                       22007, trace(AND,second) if rows is None else rows,
                       [1,0] if query is None else query,
                       allow_functional_consensus=flag)

    def test_ambiguous_wiring_agreed_outcome(self):
        rows=trace(AND,AND)
        old=self.call(rows, flag=False)
        new=self.call(rows)
        self.assertEqual(old['reason'],'AMBIGUOUS_WIRING')
        self.assertEqual(new['status'],'HYPOTHESIS')
        self.assertEqual(new['reason'],'SOURCE_FREE_FUNCTIONAL_CONSENSUS')
        self.assertEqual(new['predicted_next_bit'],0)
        self.assertEqual(new['predicted_next_bit'],independent_symbolic(AND,AND,rows,(1,0)))
        self.assertEqual(new['compatible_wirings'],['output_then_x','x_then_output'])
        for key in ('structural_chain_authenticated','action_authorized','native_state_updated','scientific_gain_verified'):
            self.assertFalse(new[key])

    def test_disagreeing_effects_abstain(self):
        rows=trace(AND,FIRST_BIT)
        got=self.call(rows,FIRST_BIT)
        self.assertEqual((got['status'],got['reason']),('ABSTAIN','AMBIGUOUS_FUNCTIONAL_OUTCOME'))
        self.assertIsNone(independent_symbolic(AND,FIRST_BIT,rows,(1,0)))

    def test_unique_wire_backwards_compatible(self):
        rows=trace(XOR,FIRST_BIT,((0,1),(1,0)),wire='y_then_output')
        ledger=Ledger(XOR,FIRST_BIT)
        original=propose(ledger,1301,22007,rows,[1,1])
        self.assertEqual(propose(ledger,1301,22007,rows,[1,1],allow_functional_consensus=True),original)

    def test_absent_or_single_trace_refuses(self):
        self.assertEqual(self.call(())['reason'],'NO_STRUCTURAL_TRACES')
        self.assertEqual(self.call(trace(AND,AND)[:1])['reason'],'INSUFFICIENT_DISTINCT_STRUCTURAL_SUPPORT')

    def test_observed_query_not_transfer(self):
        self.assertEqual(self.call(query=[0,1])['reason'],'EXACT_STRUCTURAL_TRACE_WITNESSED')

    def test_missing_primitive_refuses(self):
        ledger=Ledger();ledger.rows.pop(22007)
        self.assertEqual(self.call(native=ledger)['reason'],'PRIMITIVE_NOT_FULLY_WITNESSED')

    def test_replay_and_corrupt_outcome_rejected(self):
        rows=trace(AND,AND)
        with self.assertRaisesRegex(ValueError,'WSCM_COMPOSE_TRACE_ID'):
            self.call((rows[0],rows[0]))
        with self.assertRaisesRegex(ValueError,'WSCM_COMPOSE_PRIMITIVE_MISMATCH'):
            self.call((rows[0], rows[1]|{'second_outcome':1}))

    def test_private_law_rejected(self):
        rows=trace(AND,AND)
        with self.assertRaisesRegex(ValueError,'WSCM_COMPOSE_TRACE_FIELDS'):
            self.call((rows[0]|{'law':'oracle'},rows[1]))

    def test_invalid_flag_rejected(self):
        for value in (0,1,None,'true',[],{}):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(ValueError,'WSCM_COMPOSE_CONSENSUS_FLAG'):
                    self.call(flag=value)

    def test_deterministic_read_only(self):
        native=Ledger()
        old=dict(native.rows)
        self.assertEqual(self.call(native=native),self.call(native=native))
        self.assertEqual(old,native.rows)

    def test_exhaustive_fixed_grammar_control_parity(self):
        # Deterministic recheck of the already-inspected, source-free family.
        # These cases are correlated logic fixtures, NOT scientific trials.
        from itertools import combinations, product
        states = ((0, 0), (0, 1), (1, 0), (1, 1))
        wires = ('output_then_x', 'output_then_y',
                 'x_then_output', 'y_then_output')
        counts = {'total': 0, 'default': 0, 'consensus': 0,
                  'recovered': 0, 'wrong': 0}
        for f in product((0, 1), repeat=4):
            for g in product((0, 1), repeat=4):
                native = Ledger(f, g)
                for wire in wires:
                    for observed in combinations(states, 2):
                        receipts = trace(f, g, starts=observed, wire=wire)
                        for query in states:
                            if query in observed:
                                continue
                            before = propose(native, 1301, 22007, receipts,
                                             list(query))
                            after = propose(native, 1301, 22007, receipts,
                                            list(query), allow_functional_consensus=True)
                            control = independent_symbolic(f, g, receipts, query)
                            x, y = query
                            first = f[2*x+y]
                            mids = {'output_then_x': (first, x),
                                    'output_then_y': (first, y),
                                    'x_then_output': (x, first),
                                    'y_then_output': (y, first)}
                            actual_mid = mids[wire]
                            truth = g[2*actual_mid[0]+actual_mid[1]]
                            counts['total'] += 1
                            if before['status'] == 'HYPOTHESIS':
                                counts['default'] += 1
                                self.assertEqual(before['predicted_next_bit'], truth)
                            if after['status'] == 'HYPOTHESIS':
                                counts['consensus'] += 1
                                counts['wrong'] += int(after['predicted_next_bit'] != truth)
                                self.assertEqual(after['predicted_next_bit'], control)
                                self.assertIsNotNone(control)
                            else:
                                self.assertEqual(after['status'], 'ABSTAIN')
                                self.assertIsNone(control)
                            if before['status'] != 'HYPOTHESIS' and after['status'] == 'HYPOTHESIS':
                                counts['recovered'] += 1
        self.assertEqual(counts, {'total': 12288, 'default': 7680,
                                  'consensus': 10496, 'recovered': 2816, 'wrong': 0})

if __name__ == '__main__':
    unittest.main()
