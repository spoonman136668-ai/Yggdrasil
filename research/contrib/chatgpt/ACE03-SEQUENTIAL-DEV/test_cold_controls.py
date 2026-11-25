"""All-arm cold process fixture; no registered scientific observations."""
import base64
import json
import unittest
from transfer_study_eval import ARMS, make_arm, forecast, checkpoint
from cold_continuation import cold_probe


class ColdControlFixtures(unittest.TestCase):
    def test_all_arms_cold_continue(self):
        probes=[(0,0),(1,17),(2,511),(None,42)]
        events=[(i%3,(i*17)%512,(0,1,0,1)) for i in range(12)]
        for arm in ARMS:
            with self.subTest(arm=arm):
                m=make_arm(arm,1)
                for i in range(300):
                    m.observe(i,i%3,i%512,(1,0,1,0))
                raw=checkpoint(m)
                before=[forecast(m,k,p) for k,p in probes]
                seen=[]
                for k,p,y in events:
                    seen.append(forecast(m,k,p))
                    m.observe(m.cursor,k,p,y)
                after=[forecast(m,k,p) for k,p in probes]
                local=json.loads(json.dumps({"before":before,"preupdate":seen,"after":after}))
                cold=cold_probe(arm,1,raw,probes,events)
                self.assertEqual(local,{k:cold[k] for k in local})
                self.assertEqual(base64.b64decode(cold["checkpoint"]),checkpoint(m))
                self.assertEqual(cold["cursor"],312)


if __name__=="__main__":
    unittest.main()
