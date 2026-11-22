"""Unscored CKAD25 protocol and evidence-guard tests; no source episodes."""
import copy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ckad25_independent_unit", HERE / "independent_audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def toy_seeds():
    seeds = []
    for seed in (101, 202, 303):
        stream = []
        for count in range(0, 193, 16):
            scores = {arm: {"reward_sum":80, "episodes":96, "pooled_brier":[1,4]}
                      for arm in audit.ARMS}
            scores["coverage_active"] = {"reward_sum":86,"episodes":96,"pooled_brier":[1,8]}
            scores["exact_mixture"] = copy.deepcopy(scores["coverage_active"])
            scores["original_active"]["reward_sum"] = 85
            scores["frozen_ckad24"]["reward_sum"] = 75
            stream.append({"count":count,"evaluation":scores})
        seeds.append({"seed":seed,"stream":stream})
    return seeds


class IndependentRetentionContracts(unittest.TestCase):
    def test_unequal_phase_boundaries_and_public_world_fields(self):
        protocol = json.loads((HERE / "prereg.json").read_bytes())
        expectations = {
            0:("context_switch",0), 47:("context_switch",0),
            48:("terminal_switch",0), 79:("terminal_switch",0),
            80:("context_switch",1), 143:("context_switch",1),
            144:("invariant",0), 191:("invariant",0),
        }
        for index, (family,regime) in expectations.items():
            with self.subTest(index=index):
                self.assertEqual(audit.phase_world(protocol,index), {"family":family,"regime":regime})
        for index in (-1,192,True):
            with self.subTest(index=index), self.assertRaisesRegex(RuntimeError,"PHASE_INDEX"):
                audit.phase_world(protocol,index)
        # Held count80 belongs to the just-completed terminal phase; the next
        # acquired episode at index80 belongs to the third source phase.
        self.assertEqual(audit.phase_world(protocol,80-1)["family"],"terminal_switch")
        self.assertEqual(audit.phase_world(protocol,80)["regime"],1)

    def test_nine_frozen_gates_and_exact_arithmetic(self):
        seeds = toy_seeds()
        gates,metrics = audit.development(seeds)
        self.assertEqual(len(gates),9)
        self.assertTrue(all(gates.values()))
        self.assertEqual(metrics["whole_curve_reward"]["coverage_active"],[43,48])
        self.assertEqual(metrics["per_seed_reward_delta"],{str(s):[1,96] for s in (101,202,303)})
        self.assertEqual(metrics["post16_gain_vs_frozen"],[11,96])
        result = {"seeds":seeds,"development_gates":gates,"development_metrics":metrics,
                  "development_pass":True,"classification":"DEVELOPMENT_GO"}
        audit.verify_gates(result)
        damaged = copy.deepcopy(result)
        damaged["development_gates"]["whole_curve_vs_original"] = False
        with self.assertRaisesRegex(RuntimeError,"FROZEN_METRICS_GATES"):
            audit.verify_gates(damaged)

    def test_whole_curve_cannot_be_replaced_by_post16_points(self):
        seeds = toy_seeds()
        selected = {16,64,96,160}
        for case in seeds:
            for row in case["stream"]:
                row["evaluation"]["coverage_active"]["reward_sum"] = 90 if row["count"] in selected else 0
        gates,metrics = audit.development(seeds)
        self.assertTrue(gates["post16_gain_vs_frozen"])
        self.assertFalse(gates["whole_curve_vs_original"])
        self.assertEqual(Fraction(*metrics["whole_curve_reward"]["coverage_active"]), Fraction(4*90,13*96))

    def test_per_replica_floor_rejects_harm_hidden_by_mean(self):
        seeds = toy_seeds()
        # Two replicas each gain13 rewards; the first loses13. The aggregate
        # is positive but the frozen per-replica predicate must fail.
        seeds[0]["stream"][0]["evaluation"]["coverage_active"]["reward_sum"] = 60
        gates,metrics = audit.development(seeds)
        self.assertTrue(gates["whole_curve_vs_original"])
        self.assertFalse(gates["per_seed_whole_curve_no_loss"])
        self.assertEqual(metrics["per_seed_reward_delta"]["101"],[-1,96])

    def test_capacity_guard_receipt_and_rejection_tamper(self):
        event = ["toy", [[1,0],[1,1]], 1,0,0,1]
        ledger = [event for _ in range(1024)]
        pin = "c"*64
        receipt = audit.capacity_receipt(101,ledger,pin)
        case = {"seed":101,"capacity_probe":receipt}
        audit.verify_capacity(case,ledger,pin)
        self.assertFalse(receipt["admitted"])
        self.assertEqual(receipt["source_actions"],0)
        self.assertEqual(receipt["before_sha256"],receipt["after_sha256"])
        copied_row = {"s1":1,"x1":1,"s2":0,"x2":0,"y":1}
        self.assertEqual(receipt["packet_sha256"],audit.sha(audit.canonical(
            [receipt["unit_event_id"],event[1],copied_row])))
        damaged = copy.deepcopy(case)
        damaged["capacity_probe"]["admitted"] = True
        with self.assertRaisesRegex(RuntimeError,"CAPACITY_PROBE"):
            audit.verify_capacity(damaged,ledger,pin)
        with self.assertRaisesRegex(RuntimeError,"CAPACITY_LEDGER_COUNT"):
            audit.verify_capacity(case,ledger[:-1],pin)

    def test_frozen_current_campaign_and_native_parent_custody(self):
        current,parent = "a"*40,"b"*40
        with tempfile.TemporaryDirectory(prefix="ckad25-source-unit-") as directory:
            root = Path(directory)
            (root/".git").mkdir()
            here = root/"research/contrib/chatgpt/CKAD-25"
            here.mkdir(parents=True)
            (here/"prereg.json").write_text(json.dumps({"parent":parent}))
            (here/"campaign.py").write_bytes(b"current campaign\n")
            (root/"yggdrasil").mkdir()
            (root/"yggdrasil/model.py").write_bytes(b"native parent\n")
            relatives = ["research/contrib/chatgpt/CKAD-24/campaign.py",
                         "research/contrib/chatgpt/CKAD-24/prereg.json",
                         "research/contrib/chatgpt/CKAD-20/synthetic_world.py"]
            relatives += [f"research/contrib/chatgpt/CKAD-{era}/{name}.py"
                for era,names in ((19,("independent_audit",)),(20,("campaign","independent_audit")),
                                  (21,("campaign","independent_audit")),(22,("campaign","independent_audit")),
                                  (23,("independent_audit",)),(24,("campaign","independent_audit")))
                for name in names]
            for relative in relatives:
                path = root/relative
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(b"qualified inherited source\n")
            requested = []
            def git_show(arguments, **kwargs):
                self.assertEqual(arguments[:2],["git","show"])
                revision,relative = arguments[2].split(":",1)
                self.assertIn(revision,(current,parent))
                requested.append((revision,relative))
                return (root/relative).read_bytes()
            with patch.object(audit,"ROOT",root), patch.object(audit,"HERE",here), \
                    patch.object(audit.subprocess,"check_output",side_effect=git_show):
                self.assertTrue(audit.verify_training_source(current))
            self.assertIn((current,"research/contrib/chatgpt/CKAD-25/campaign.py"),requested)
            self.assertIn((current,"research/contrib/chatgpt/CKAD-25/prereg.json"),requested)
            self.assertIn((parent,"yggdrasil/model.py"),requested)
            def damaged_show(arguments, **kwargs):
                if arguments[2] == current+":research/contrib/chatgpt/CKAD-25/campaign.py":
                    return b"different frozen campaign\n"
                return git_show(arguments,**kwargs)
            with patch.object(audit,"ROOT",root), patch.object(audit,"HERE",here), \
                    patch.object(audit.subprocess,"check_output",side_effect=damaged_show):
                with self.assertRaisesRegex(RuntimeError,"FROZEN_TRAINING_BYTES_research/contrib/chatgpt/CKAD-25/campaign.py"):
                    audit.verify_training_source(current)

    def test_stable_hash_excludes_cost_but_keeps_capacity_evidence(self):
        value = {"scientific_pass":False,"capacity_probe":{"admitted":False,"count":1024},
                 "resource_accounting":{"child":{"cpu_seconds":1.2}},
                 "whole_wall_seconds":3.0,"parent_peak_rss_bytes":100,
                 "source_candidate_sha":"a"*40,"stable_sha256":"b"*64}
        self.assertEqual(audit.stable(value),{"scientific_pass":False,
                         "capacity_probe":{"admitted":False,"count":1024}})


if __name__ == "__main__":
    unittest.main()
