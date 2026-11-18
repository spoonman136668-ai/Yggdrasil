"""WSP183 source-free engineering checks, not physical-world experiments."""
from __future__ import annotations

import ast
import io
from pathlib import Path
import sys
import unittest

from physical_offline import (Event, aggregate, build_fit, get_predictions,
                             read_archive, score, perform, TARGETS)


def authored_events():
    result=[]
    for r in range(10):
        for i in range(10):
            load=(0.01,0.1,0.2,0.5)[i%4]
            targets=(120.0+85*load+0.4*r+0.1*i,
                     0.9+3.5*load+0.06*r+0.03*i)
            result.append(Event(r,i,load,targets))
    return result


def mock_csv():
    lines=["intervention,load_in,rpm_in,pressure_intake"]
    for event in authored_events()[:10]:
        for i in range(85):
            lines.append(f"{1 if i==0 else 0},{event.load},{event.targets[0]},{event.targets[1]}")
    return ("\n".join(lines)+"\n").encode()


class OfflineDataEngineeringTests(unittest.TestCase):
    def test_actual_source_csv_contract_segmentation(self):
        events=aggregate(0,mock_csv())
        self.assertEqual(len(events),10)
        self.assertEqual(events[0].run,0)
        self.assertEqual(events[0].order,0)
        self.assertAlmostEqual(events[0].targets[0],authored_events()[0].targets[0])
        self.assertEqual(events[0].load,0.01)

    def test_no_future_sensor_leak_at_prediction_time(self):
        events=authored_events()
        model=build_fit([e for e in events if e.run<=5])
        current=events[71]
        prior=events[70]
        baseline=get_predictions(current,prior,model)
        impossible_future=Event(current.run,current.order,current.load,(1e10,-1e10))
        self.assertEqual(baseline,get_predictions(impossible_future,prior,model))
        changed_past=Event(prior.run,prior.order,prior.load,(1e10,-1e10))
        self.assertNotEqual(baseline["direct_repair"],
                            get_predictions(current,changed_past,model)["direct_repair"])
        self.assertNotEqual(baseline["arx"],
                            get_predictions(current,changed_past,model)["arx"])

    def test_independent_equal_information_conventional_parity(self):
        events=authored_events()
        fit=[e for e in events if e.run<=5]
        model=build_fit(fit)
        self.assertLessEqual(model["parity_max_weight_abs_gap"],1e-5)
        for e in events:
            preds=get_predictions(e,None,model)
            for native,ordinary in zip(preds["direct"],preds["batch"]):
                self.assertAlmostEqual(native,ordinary,places=5)
        self.assertEqual(score([e for e in events if e.run in (8,9)],model)["events"],20)

    def test_reject_malformed_event_and_hidden_source(self):
        data=mock_csv().decode()
        with self.assertRaisesRegex(ValueError,"INITIAL_BOUNDARY"):
            aggregate(0,data.replace("1,0.01,","0,0.01,",1).encode())
        with self.assertRaisesRegex(ValueError,"UNEXPECTED_LOAD"):
            aggregate(0,data.replace("1,0.01,","1,20.0,",1).encode())
        with self.assertRaisesRegex(ValueError,"WITHIN_SEGMENT_ACTION_DRIFT"):
            aggregate(0,data.replace("0,0.01,","0,0.2,",1).encode())
        with self.assertRaisesRegex(ValueError,"MISSING_SOURCE_COLUMNS"):
            aggregate(0,b"intervention,load_in\n1,0.1\n")
        with self.assertRaisesRegex(ValueError,"ARCHIVE_SIZE"):
            read_archive(Path("/tmp/WSP183-no-existing-source.zip"))

    def test_no_paid_or_original_interaction_dependencies(self):
        source=Path(__file__).with_name("physical_offline.py").read_text("utf-8")
        tree=ast.parse(source)
        names={i.name.split(".")[0] for node in ast.walk(tree)
               if isinstance(node,ast.Import) for i in node.names}
        names|={node.module.split(".")[0] for node in ast.walk(tree)
                if isinstance(node,ast.ImportFrom) and node.module}
        self.assertFalse(names&{"requests","boto3","gym","torch","openai","numpy",
                                "causalchamber","causal_gym","pandas"})
        self.assertNotIn("urlopen(",source)
        self.assertNotIn("env.step(",source)
        self.assertNotIn("source_first_use_authority",source)


if __name__=="__main__":
    unittest.main()
