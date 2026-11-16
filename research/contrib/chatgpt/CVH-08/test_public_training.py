"""CVH08 source-free validation of generic public training (no real first use)."""
from __future__ import annotations
from collections import namedtuple
import json
import pathlib
import unittest

import public_training as p


class FrozenPublicAdmissionTests(unittest.TestCase):
    def test_prereg_first_source_custody_unopened(self):
        q=json.loads((p.HERE/"prereg.json").read_text())
        self.assertEqual(q["schema"],"yggdrasil.cvh08.public-training-firstuse-disarmed-prereg.v1")
        self.assertEqual(q["parent"]["sha"],p.PARENT)
        self.assertEqual(p.PREREG_FIRST,"987a413bce8722f43458a654f78271cad6e70372")
        self.assertFalse(q["science"]["original_source_first_use_authorized"])
        self.assertFalse(q["science"]["owner_signed_seed_lease"])
        d=json.loads((p.HERE.parent/"CVH-06"/"source_first_use_NOT_AUTHORIZED.json").read_text())
        self.assertEqual(d["state"],"NOT_AUTHORIZED_NO_ORIGINAL_SOURCE_ACTIONS")
        self.assertEqual(d["train_seed_ids"],[])
        self.assertTrue(all(not v for v in d["held_seed_ids_by_arm"].values()))
        self.assertTrue(all(not v for v in d["transfer_seed_ids_by_arm"].values()))
        self.assertEqual(d["actual_source_interventions_this_gate"],0)

    def test_synthetic_public_training_is_64_complete_variable_size_episodes(self):
        episodes=tuple(p.synthetic_public_episode(i) for i in range(p.TRAIN_EPISODES))
        lengths=[len(e) for e in episodes]
        self.assertEqual(len(episodes),64)
        self.assertEqual(set(lengths),{1,4,8,31,32})
        self.assertEqual(len(p.validate_completed_train(episodes)),64)
        self.assertTrue(all(e[-1].truncated for e in episodes))
        self.assertEqual(len(p.validate_completed_train(episodes)[0]),1)
        for ep in episodes:
            for i,r in enumerate(ep):
                self.assertEqual(tuple(r._fields),tuple(p.PublicConsequence._fields))
                self.assertTrue(all(type(v) is int and v in (0,1) for v in r[:4]))
                if i:
                    self.assertEqual(ep[i-1].after,r.before)

    def test_accepted_public_training_is_not_the_old_96_toy_fit(self):
        episodes=tuple(p.synthetic_public_episode(i) for i in range(64))
        # The historical CVH07 fixed experiment remains frozen/reproducible.
        original=p.ConventionalPublicRNN()
        with self.assertRaisesRegex(ValueError,"FIXED_96_SOURCEFREE_TRAIN_EPISODES"):
            original.fit(episodes)
        # New genuine public-data interface is deliberately separate.
        candidate=p.SourceIndependentPublicTrainRNN()
        self.assertFalse(candidate.trained)
        self.assertEqual(candidate.epochs_completed,0)
        self.assertEqual(len(episodes),64)

    def test_arbitrary_public_64_train_fits_frozen_bptt_and_strong_controls(self):
        report=p.sourcefree_training_receipt()
        train=report["full_public_source_train"]
        self.assertEqual(report["classification"],"SOURCE_FREE_PUBLIC_TRAINING_ADAPTER_ENGINEERING_ONLY")
        self.assertEqual(train["train_public_episode_count"],64)
        self.assertGreater(train["train_public_event_count"],64)
        self.assertEqual(train["train_epoch_count"],48)
        self.assertGreaterEqual(train["brier_improvement"],0.02)
        self.assertEqual(set(train["training_model_hashes"]),{"native","fourcell","recurrent"})
        self.assertTrue(all(len(x)==64 for x in train["training_model_hashes"].values()))
        self.assertEqual(report["original_causalgym_do_calls"],0)
        self.assertFalse(report["source_original_first_use_authorized"])
        self.assertFalse(report["science_pass"])
        self.assertFalse(report["native_accepted"])
        self.assertFalse(report["deployed"])
        self.assertEqual(report["receipt_sha256"],
                         p.digest({k:v for k,v in report.items() if k!="receipt_sha256"}))

    def test_model_states_fit_identical_public_episode_count_and_cold_restore(self):
        episodes=tuple(p.synthetic_public_episode(i) for i in range(64))
        models,metrics=p.fit_all_learned_arms_on_public(episodes)
        events=sum(map(len,episodes))
        self.assertEqual(events,metrics["train_public_event_count"])
        self.assertEqual(models["native"].memory.seen,events)
        self.assertEqual(models["fourcell"].seen,events)
        self.assertEqual(models["recurrent"].epochs_completed,48)
        self.assertTrue(models["recurrent"].trained)
        self.assertEqual(sum(models["fourcell"].count),events)
        self.assertEqual(sum(models["fourcell"].attempts),events)
        flat=tuple(r for ep in episodes for r in ep)
        self.assertEqual(
            (models["fourcell"].count,models["fourcell"].total),
            tuple(p.independent_fourcell_public_batch(flat)))
        for model in models.values():
            raw=model.snapshot()
            self.assertEqual(type(model).restore(raw).snapshot(),raw)
        with self.assertRaisesRegex(ValueError,"TRAIN_ONCE_NO_POST_HOLD_RETUNING"):
            models["recurrent"].fit_public(episodes)

    def test_extra_private_fields_forbidden_before_weights_change(self):
        episodes=list(p.synthetic_public_episode(i) for i in range(64))
        private=namedtuple("PrivateEvent",tuple(p.PublicConsequence._fields)+("hidden_graph",))
        ep=list(episodes[0])
        r=ep[0]
        ep[0]=private(*r,99)
        episodes[0]=tuple(ep)
        m=p.SourceIndependentPublicTrainRNN()
        with self.assertRaisesRegex(ValueError,"PUBLIC_FIELDS_ONLY"):
            m.fit_public(tuple(episodes))
        self.assertFalse(m.trained)
        self.assertEqual(m.epochs_completed,0)
        self.assertEqual(m.snapshot(),p.SourceIndependentPublicTrainRNN().snapshot())

    def test_early_terminal_incomplete_and_continuity_fail(self):
        base=list(p.synthetic_public_episode(i) for i in range(64))
        with self.assertRaisesRegex(ValueError,"FROZEN_64_PUBLIC"):
            p.validate_completed_train(tuple(base[:63]))
        with self.assertRaisesRegex(ValueError,"PUBLIC_EPISODE_LENGTH"):
            p.validate_completed_train(tuple([tuple()]+base[1:]))
        e=list(base[1])
        last=e[-1]
        e[-1]=p.PublicConsequence(last.before,last.action,last.reward,
                                  last.after,False,False)
        with self.assertRaisesRegex(ValueError,"UNCLOSED_PUBLIC"):
            p.validate_completed_train(tuple([base[0],tuple(e)]+base[2:]))
        e=list(base[2])
        first=e[0]
        e[0]=p.PublicConsequence(first.before,first.action,first.reward,
                                 first.after,False,True)
        with self.assertRaisesRegex(ValueError,"PREMATURE_END"):
            p.validate_completed_train(tuple(base[:2]+[tuple(e)]+base[3:]))
        e=list(base[3])
        v=e[1]
        e[1]=p.PublicConsequence(1-e[0].after,v.action,v.reward,v.after,
                                 v.terminated,v.truncated)
        with self.assertRaisesRegex(ValueError,"DISCONTINUITY"):
            p.validate_completed_train(tuple(base[:3]+[tuple(e)]+base[4:]))

    def test_original_action_adapter_still_restricts_4_already_consumed_seeds(self):
        fkp24=p.HERE.parent/"FKP-24"/"native_public_mdp.py"
        source=fkp24.read_text(encoding="utf-8")
        self.assertIn("MECHANICAL_PUBLIC_SEEDS=(996100,996101,996102,996103)",source)
        self.assertIn('raise PermissionError("FKP24_UNAUTHORIZED_OR_PROTECTED_WORLD")',source)
        body=(p.HERE/"public_training.py").read_text(encoding="utf-8")
        self.assertNotIn("import causal_gym",body)
        self.assertNotIn("env.reset(",body)
        self.assertNotIn("env.do(",body)
        self.assertNotIn("ctf_do(",body)
        self.assertNotIn("subprocess.",body)
        self.assertNotIn("requests.",body)

    def test_no_training_can_consume_protected_seed_as_fixture_selector(self):
        for i in (996100,996101,996102,996103,996500,996531,996600,996663,-1,64):
            with self.assertRaises(PermissionError):
                p.synthetic_public_episode(i)

    def test_persisted_exact_result_if_present(self):
        file=p.HERE/"result.json"
        if not file.exists():
            self.skipTest("Frozen result not yet committed; exact comparison enforced in final commit")
        self.assertEqual(json.loads(file.read_text()),p.sourcefree_training_receipt())


if __name__=="__main__":
    unittest.main()
