import hashlib
import unittest
import source_attempt_intent as x

class SourceAttemptIntentTests(unittest.TestCase):
    def test_proposed_only(self):
        a=x.verified_intent()
        self.assertFalse(a['execution_authority'])
        self.assertEqual(a['admission'], 'NO')
        self.assertEqual(a['original_source_resets'], 0)
    def test_full_budget(self):
        a=x.verified_intent()
        self.assertEqual(a['proposed_physical_attempts_per_host'],4240)
        self.assertEqual(a['proposed_total_physical_attempts'],8480)
        self.assertEqual(a['distinct_seed_values'],1168)
    def test_preflight_is_16_per_host(self):
        a=x.verified_intent()
        self.assertTrue(all(v['PREFLIGHT']==16 for v in a['counts_by_host_phase'].values()))
    def test_full_phase_breakdown(self):
        a=x.verified_intent()
        self.assertTrue(all(v['FIT']==2304 and v['DEV']==640 and v['HELD']==1280 for v in a['counts_by_host_phase'].values()))
    def test_all_seed_roles_disjoint(self):
        s=[set(x.seeds(p)) for p in x.PHASE_ARMS]
        for i in range(4):
            for j in range(i+1,4): self.assertFalse(s[i] & s[j])
    def test_separate_arm_host_attempt_ids(self):
        rows=list(x.attempts())
        self.assertEqual(len(rows),len({z['scheduled_attempt_id'] for z in rows}))
        sample=[z for z in rows if z['phase']=='HELD' and z['seed']==x.seeds('HELD')[0]]
        self.assertEqual(len(sample),10)
        self.assertEqual(len({(z['host_role'],z['arm_id']) for z in sample}),10)
    def test_all_attempts_not_reserved_or_consumed(self):
        self.assertTrue(all(z['reservation']=='PROPOSED_NOT_RESERVED' and z['consumed']=='UNVERIFIED' for z in x.attempts()))
    def test_sealed_donor_rule_for_registered_dev_and_held(self):
        for phase in ('DEV', 'HELD'):
            for seed in x.seeds(phase):
                expect=int.from_bytes(hashlib.sha256(f'341303:{seed}'.encode()).digest()[:8],'big')%768
                self.assertEqual(x.fit_only_donor_index(seed),expect)
    def test_donor_rule_rejects_fit_preflight_arbitrary_and_changed_salt(self):
        for seed in (x.seeds('FIT')[0], x.seeds('PREFLIGHT')[0], 0, 3_200_999, 3_300_999, -10, True, 3_300_100.0):
            with self.subTest(seed=seed),self.assertRaises(ValueError):
                x.fit_only_donor_index(seed)
        with self.assertRaises(ValueError):
            x.fit_only_donor_index(x.seeds('DEV')[0],salt=341304)
    def test_intent_digest_deterministic(self):
        self.assertEqual(x.verified_intent()['attempt_id_set_sha256'],x.verified_intent()['attempt_id_set_sha256'])
    def test_no_external_runtime_import(self):
        from pathlib import Path
        source=Path(x.__file__).read_text()
        self.assertNotIn('import minigrid',source)
        self.assertNotIn('import gymnasium',source)
        self.assertNotIn('env.reset(',source)
    def test_no_permitted_scheduler(self):
        source=__import__('pathlib').Path(x.__file__).read_text()
        self.assertNotIn('dispatch_workflow',source)
        self.assertNotIn('requests.post(',source)

if __name__ == '__main__': unittest.main()
