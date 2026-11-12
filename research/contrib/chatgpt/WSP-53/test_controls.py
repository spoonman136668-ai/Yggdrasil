"""WSP53 negative-control engineering checks. No world or DEV/PRIMARY execution."""
from dataclasses import dataclass,replace
import json
import unittest
from controls import WholeStreamTable,ErasedControl,MAX_ACTIONS

@dataclass(frozen=True)
class Observation:
    before:tuple
    acoustic_bits:str
    after:tuple
    action_cost:int=1
    reset_cost:int=0

class Contracts(unittest.TestCase):
    @staticmethod
    def fact(family):
        before=(0,)*(16 if family=="anchored_effect" else 8)
        after=list(before)
        after[0]=2
        if family=="anchored_effect":
            after[8]=1
        return Observation(before,"010101010101",tuple(after))

    def test_lookup_abstention_and_restore(self):
        for family in ("anchored_effect","noncommuting_order"):
            r=self.fact(family)
            m=WholeStreamTable(family=family)
            m.observe(r)
            self.assertEqual(m.predict(r.before,r.acoustic_bits),r.after)
            self.assertIsNone(m.predict(r.before,"010101010100"))
            different=list(r.before);different[1]=1
            self.assertIsNone(m.predict(tuple(different),r.acoustic_bits))
            cold=WholeStreamTable.restore(m.snapshot())
            self.assertEqual(cold.predict(r.before,r.acoustic_bits),r.after)
            self.assertEqual(cold.capacity_bits(),m.capacity_bits())

    def test_conflicts_irreversible(self):
        for family in ("anchored_effect","noncommuting_order"):
            r=self.fact(family)
            m=WholeStreamTable(family=family)
            m.observe(r)
            m.observe(replace(r,after=r.before))
            m.observe(r)
            self.assertIsNone(m.predict(r.before,r.acoustic_bits))
            self.assertIsNone(WholeStreamTable.restore(m.snapshot()).predict(r.before,r.acoustic_bits))

    def test_tamper_and_invalid_receipts(self):
        r=self.fact("anchored_effect")
        m=WholeStreamTable(family="anchored_effect")
        for wrong in (replace(r,action_cost=0),replace(r,reset_cost=1),
                      replace(r,acoustic_bits="bad"),
                      replace(r,before=r.before[:-1]),
                      replace(r,before=(True,)+r.before[1:])):
            with self.assertRaises(ValueError):
                m.observe(wrong)
        self.assertEqual(m.actions,0)
        m.observe(r)
        envelope=json.loads(m.snapshot())
        envelope["payload"]["facts"][0][2][0]=3
        with self.assertRaises(ValueError):
            WholeStreamTable.restore(json.dumps(envelope))
        envelope=json.loads(m.snapshot())
        envelope["payload"]["facts"].append(envelope["payload"]["facts"][0])
        with self.assertRaises(ValueError):
            WholeStreamTable.restore(json.dumps(envelope))
        with self.assertRaises(ValueError):
            WholeStreamTable(family="invalid")

    def test_budget_and_erased(self):
        for family in ("anchored_effect","noncommuting_order"):
            r=self.fact(family)
            for clazz in (WholeStreamTable,ErasedControl):
                m=clazz(family=family)
                for _ in range(MAX_ACTIONS):
                    m.observe(r)
                self.assertEqual(m.actions,60)
                with self.assertRaises(ValueError):
                    m.observe(r)
                if clazz is ErasedControl:
                    self.assertIsNone(m.predict(r.before,r.acoustic_bits))

if __name__=="__main__":
    unittest.main()
