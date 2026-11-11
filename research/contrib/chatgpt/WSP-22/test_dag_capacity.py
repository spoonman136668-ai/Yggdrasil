import unittest
from dag_capacity import check_certificate,search,brute_depth_two,PlasticNand


class WSP22Tests(unittest.TestCase):
    def test_shared_xor_dag_uses_four_sites(self):
        c={'signature':6,'mode':'connected','gates':[[0,1],[0,3],[1,3],[4,5]],'output':6}
        checked=check_certificate(c)
        self.assertEqual(checked['sites'],4)
        self.assertEqual(checked['table'],[0,1,1,0,0,1,1,0])

    def test_null_source_allowed_for_input_only(self):
        c={'signature':63,'mode':'allow_disconnected','gates':[[-1,-1]],'output':3}
        self.assertEqual(check_certificate(c)['table'],[1]*8)
        c['output']=-1
        with self.assertRaises(ValueError):check_certificate(c)
        c['output']=3;c['mode']='connected'
        with self.assertRaises(ValueError):check_certificate(c)

    def test_duplicate_null_valued_output_is_not_pruned(self):
        r=search('allow_disconnected',(0,),max_sites=2)
        self.assertEqual(r['unresolved'],[])
        self.assertEqual(check_certificate(r['certificates'][0])['table'],[0]*8)
        self.assertEqual(len(r['certificates'][0]['gates']),2)

    def test_independent_brute_enumeration_matches_both_merged_modes(self):
        for mode in ('connected','allow_disconnected'):
            r=search(mode,tuple(range(64)),max_sites=2)
            self.assertEqual({c['signature'] for c in r['certificates']},brute_depth_two(mode))
            for c in r['certificates']:check_certificate(c)

    def test_forward_cycle_and_capacity_rejected(self):
        c={'signature':0,'mode':'connected','gates':[[3,0]],'output':3}
        with self.assertRaises(ValueError):check_certificate(c)
        c['gates']=[[0,0]]*7;c['output']=9
        with self.assertRaises(ValueError):check_certificate(c)

    def test_wrong_evidence_and_noninteger_fields_rejected(self):
        c={'signature':0,'mode':'connected','gates':[],'output':0}
        with self.assertRaises(ValueError):check_certificate(c)
        for field,bad in (('signature',True),('output',True)):
            d=dict(c);d[field]=bad
            with self.assertRaises(ValueError):check_certificate(d)

    def test_caps_never_label_a_miss_unsatisfiable(self):
        r=search('connected',(1,),max_states=1)
        self.assertEqual(r['status'],'STATE_CAP_UNRESOLVED')
        self.assertEqual(r['states'],1)
        r=search('connected',(1,),max_transitions=1)
        self.assertEqual(r['status'],'TRANSITION_CAP_UNRESOLVED')
        self.assertEqual(r['transitions'],1)

    def test_deterministic_search_and_checkpoint_corruption(self):
        a=search('connected',(63,),max_sites=2);b=search('connected',(63,),max_sites=2)
        self.assertEqual(a,b)
        raw=PlasticNand().snapshot()
        with self.assertRaises(ValueError):PlasticNand.restore(raw[:-1])

    def test_invalid_budget_and_mode_rejected(self):
        for kwargs in ({'mode':'bad'},{'mode':'connected','max_sites':7},{'mode':'connected','targets':(True,)}):
            with self.assertRaises(ValueError):search(**kwargs)


if __name__=='__main__':unittest.main()
