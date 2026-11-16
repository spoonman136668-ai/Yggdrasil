"""Source-safe CB4 mechanics/negative tests. No source-private held first use."""
from __future__ import annotations
from collections import namedtuple
import ast
from pathlib import Path
import unittest

import binding
import role_interventions as m
import mediated_source as source


class CausalRoleInterventionTests(unittest.TestCase):
    def test_new_public_seed_fence_and_delayed_earned_action(self):
        self.assertEqual(source.WORLDS,tuple(range(82400,82432)))
        for seed in (978500,978531,978600,978663,82300,True,82432):
            with self.assertRaises(PermissionError):source.training(seed)
        rows=source.training(82400)
        self.assertEqual(len(rows),515)
        for i,row in enumerate(rows):
            credit,_=binding._credit_public(row)
            self.assertEqual(credit is None,i<3)
            if i>=3:
                self.assertEqual(credit[1],row.history[-2].action if row.reward==1
                                 else 1-row.history[-2].action)
                self.assertEqual(row.history[-1].after,row.before)

    def test_actual_bit_flip_and_physically_paid_budget(self):
        world=source.PublicInterventionSource(82400)
        for idx in (1,17,6):
            old=world.paid
            row=world.probe(idx)
            self.assertEqual(row._fields,m.PROBE_FIELDS)
            self.assertEqual(row.cost,1)
            self.assertEqual(row.target_feature,idx)
            self.assertEqual(tuple(a^b for a,b in zip(row.before_state,row.after_state)),
                             tuple(1<<(idx%4) if j==idx//4 else 0 for j in range(8)))
            self.assertEqual(world.paid,old+1)
        with self.assertRaises(ValueError):world.probe(22)
        with self.assertRaises(ValueError):source.PublicInterventionSource(82400).probe(35)

    @staticmethod
    def fake_probe(feature,content,before=(0,)*8):
        after=list(before);after[feature//4]^=1<<(feature%4)
        return source.PublicProbe(before,feature,tuple(after),0,int(feature in content),1)

    def test_all_six_role_partitions_identifiable_with_at_most_three_actions(self):
        four=(1,6,17,22)
        for content in __import__('itertools').combinations(four,2):
            a=m.DirectRoleProbe(four)
            b=m.ConventionalExactPartitions(four)
            while (j:=a.next_feature()) is not None:
                row=self.fake_probe(j,content)
                a.observe_public(row)
            while (j:=b.next_feature()) is not None:
                b.observe_public(self.fake_probe(j,content))
            want=(tuple(sorted(content)),tuple(x for x in four if x not in content))
            self.assertEqual(a.roles,want)
            self.assertEqual(b.roles,want)
            self.assertEqual(a.paid_probes,b.paid_probes)
            self.assertLessEqual(a.paid_probes,3)

    def test_invalid_private_or_forged_probes_rejected_atomically(self):
        a=m.DirectRoleProbe((1,6,17,22))
        valid=self.fake_probe(1,(1,6))
        Extra=namedtuple('Extra',m.PROBE_FIELDS+('private_oracle',))
        wrongs=(Extra(*valid,1),valid._replace(cost=0),valid._replace(target_feature=True),
                valid._replace(mediator_after=2),valid._replace(after_state=valid.before_state),
                valid._replace(target_feature=6))
        for invalid in wrongs:
            with self.assertRaises(ValueError):a.observe_public(invalid)
            self.assertEqual(a.paid_probes,0)
        self.assertEqual(a.next_feature(),1)
        a.observe_public(valid)
        before=a.paid_probes
        with self.assertRaises(ValueError):a.observe_public(
            self.fake_probe(6,(1,6),before=(1,)*8))
        self.assertEqual(a.paid_probes,before)

    def test_cold_role_checkpoint_74_bytes_and_checksum_refusal(self):
        a=m.DirectRoleProbe((1,6,17,22))
        for idx in (1,6):a.observe_public(self.fake_probe(idx,(1,6)))
        original=a.snapshot()
        self.assertEqual(len(original),74)
        cold=m.DirectRoleProbe.restore(original)
        self.assertEqual(cold.snapshot(),original)
        self.assertEqual(cold.roles,a.roles)
        bad=bytearray(original);bad[7]^=1
        for data in (bytes(bad),b'',original+b' '):
            with self.assertRaises(ValueError):m.DirectRoleProbe.restore(data)

    def test_role_model_never_imports_source_law_private_fields(self):
        text=Path(m.__file__).read_text('utf-8')
        tree=ast.parse(text)
        imports=set()
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):imports.update(x.name for x in node.names)
            elif isinstance(node,ast.ImportFrom):imports.add(node.module)
        self.assertNotIn('mediated_source',imports)
        self.assertNotIn('PREREG_PRIVATE_CONFIGS',text)
        self.assertNotIn('_private_features',text)

    def test_observation_only_cannot_name_role_partition_by_arbitrary_table(self):
        # Exact proof: all 6 ways to name two of four inputs as 'content' can
        # represent the SAME 16-entry Boolean input/output mapping after
        # reindexing the truth table. No passive reward can distinguish labels.
        from itertools import combinations,product
        inputs=list(product((0,1),repeat=4))
        truth=[(x[0]^x[1]^int((2*x[0]+x[1])==(2*x[2]+x[3]))) for x in inputs]
        for content in combinations(range(4),2):
            order=tuple(content)+tuple(i for i in range(4) if i not in content)
            permuted={tuple(x[j] for j in order): y for x,y in zip(inputs,truth)}
            self.assertEqual(len(permuted),16)
            self.assertEqual([permuted[tuple(x[j] for j in order)] for x in inputs],truth)

if __name__=='__main__':unittest.main()
