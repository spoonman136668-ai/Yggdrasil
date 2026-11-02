import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("repair_atlas", ROOT / "scripts/repair_code_atlas.py")
repair = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(repair)


class AtlasRepair(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ygg-atlas-repair-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.control = self.base / "control"
        self.control.mkdir()
        repair.git(self.control, "init", "-q")
        repair.git(self.control, "config", "user.name", "Fixture")
        repair.git(self.control, "config", "user.email", "fixture@example.invalid")
        for path in repair.GUARDS:
            dest = self.control / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes((ROOT / path).read_bytes())
        (self.control / "source.py").write_bytes(b"def original():\n    return 1\n")
        self.original = self.commit(self.control)
        atlas = repair.builder(self.control)
        for path, value in atlas.render(atlas.snapshot(self.control, self.original)).items():
            dest = self.control / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(value.encode("utf-8"))
        self.valid = self.commit(self.control)
        (self.control / "source.py").write_bytes(b"def changed():\n    return 2\n")
        self.source = self.commit(self.control)
        self.candidate = self.clone("candidate", self.source)

    def commit(self, root):
        repair.git(root, "add", "--all")
        repair.git(root, "commit", "-qm", "fixture")
        return repair.text(root, "rev-parse", "HEAD")

    def clone(self, name, rev):
        root = self.base / name
        repair.git(self.base, "clone", "-q", "--no-hardlinks", "--no-checkout", str(self.control), str(root))
        repair.git(root, "checkout", "-q", "--detach", rev)
        repair.git(root, "config", "user.name", "Fixture")
        repair.git(root, "config", "user.email", "fixture@example.invalid")
        return root

    def strict_check(self, root):
        return subprocess.run([os.sys.executable, "-B", str(self.control / repair.GUARDS[0]),
                               "--root", str(root), "--check"], capture_output=True)

    def test_stale_atlas_repaired_by_exact_metadata_only_child(self):
        self.assertNotEqual(self.strict_check(self.candidate).returncode, 0)
        receipt = repair.prepare(self.candidate, self.control, self.source)
        self.assertEqual(receipt["changed"], sorted(repair.OUTPUTS))
        self.assertEqual(receipt["atlas_source"], self.source)
        self.assertEqual(repair.text(self.candidate, "rev-parse", "HEAD^"), self.source)
        self.assertEqual(repair.git(self.candidate, "show", "HEAD:source.py"),
                         repair.git(self.candidate, "show", self.source + ":source.py"))
        self.assertEqual(self.strict_check(self.candidate).returncode, 0)
        data = json.loads((self.candidate / repair.OUTPUTS[0]).read_text("utf-8"))
        self.assertEqual(data["source_reviewed_labels"], 0)
        self.assertFalse(data["wingless_evidence_imported"])
        repair.verify(self.candidate, receipt)

    def test_commit_and_receipt_are_deterministic_across_checkouts(self):
        other = self.clone("other", self.source)
        first = repair.prepare(self.candidate, self.control, self.source)
        second = repair.prepare(other, self.control, self.source)
        self.assertEqual(first, second)

    def test_privileged_reconstruction_never_checks_out_the_companion(self):
        other = self.clone("no-checkout", self.source)
        expected = repair.prepare(self.candidate, self.control, self.source)
        result = repair.prepare(other, self.control, self.source, checkout=False)
        self.assertEqual(expected, result)
        self.assertEqual(repair.text(other, "rev-parse", "HEAD"), self.source)
        self.assertEqual(repair.git(other, "status", "--porcelain"), b"")

    def test_valid_atlas_is_noop(self):
        root = self.clone("valid", self.valid)
        result = repair.prepare(root, self.control, self.valid)
        self.assertEqual(result["companion"], self.valid)
        self.assertEqual(result["changed"], [])
        repair.verify(root, result)

    def test_dirty_or_wrong_head_refused(self):
        with self.assertRaisesRegex(RuntimeError, "exact source"):
            repair.prepare(self.candidate, self.control, self.valid)
        (self.candidate / "unexpected.txt").write_bytes(b"unexpected")
        with self.assertRaisesRegex(RuntimeError, "dirty source"):
            repair.prepare(self.candidate, self.control, self.source)

    def test_builder_and_acceptance_guard_changes_refused(self):
        for index, path in enumerate(repair.GUARDS):
            root = self.clone("guard" + str(index), self.source)
            file = root / path
            file.write_bytes(file.read_bytes() + b"\n# changed guard\n")
            changed = self.commit(root)
            with self.assertRaisesRegex(RuntimeError, "changed guard"):
                repair.prepare(root, self.control, changed)

    def test_symlink_entry_refused_even_without_os_symlink_support(self):
        blob = repair.git(self.candidate, "hash-object", "-w", "--stdin", data=b"source.py").strip().decode()
        repair.git(self.candidate, "update-index", "--add", "--cacheinfo", "120000", blob, "alias.py")
        repair.git(self.candidate, "commit", "-qm", "symlink fixture")
        source = repair.text(self.candidate, "rev-parse", "HEAD")
        # git read-tree makes a portable clean checkout (Windows may represent
        # a symbolic link as an ordinary file; the Git mode remains 120000).
        repair.git(self.candidate, "reset", "--hard", source)
        with self.assertRaisesRegex(RuntimeError, "nonregular Git entry"):
            repair.prepare(self.candidate, self.control, source)

    def test_post_qualification_artifact_tampering_refused(self):
        receipt = repair.prepare(self.candidate, self.control, self.source)
        file = self.candidate / repair.OUTPUTS[0]
        file.write_bytes(file.read_bytes() + b" ")
        with self.assertRaisesRegex(RuntimeError, "qualification drift"):
            repair.verify(self.candidate, receipt)

    def test_publication_requires_both_matching_os_receipts(self):
        receipts = self.base / "receipts"
        receipts.mkdir()
        with mock.patch.object(repair, "lease"), self.assertRaisesRegex(RuntimeError, "both OS"):
            repair.publish(self.candidate, self.control, self.source, 1, receipts)

    def test_existing_wrong_companion_cannot_be_overwritten(self):
        expected = repair.prepare(self.candidate, self.control, self.source)
        repair.git(self.candidate, "checkout", "--detach", self.source)
        receipts = self.base / "receipts"
        for name in ("linux", "windows"):
            directory = receipts / ("atlas-qualification-" + name)
            directory.mkdir(parents=True)
            (directory / "receipt.json").write_text(json.dumps(expected), encoding="utf-8")
        jobs = {"jobs": [{"name": "atlas-qualification (" + name + ")",
                          "status": "completed", "conclusion": "success"}
                         for name in ("linux", "windows")]}
        with mock.patch.object(repair, "lease"), mock.patch.object(repair, "api", side_effect=[
                jobs, {"object": {"sha": "0" * 40}}]) as api, mock.patch.dict(os.environ, GITHUB_RUN_ID="1"):
            with self.assertRaisesRegex(RuntimeError, "existing companion differs"):
                repair.publish(self.candidate, self.control, self.source, 1, receipts)
            self.assertTrue(all(call.args[1:] == () for call in api.call_args_list))

    def test_stale_or_fork_pr_lease_refused(self):
        pr = {"state": "open", "user": {"login": repair.OWNER}, "author_association": "OWNER",
              "head": {"repo": {"full_name": repair.REPOSITORY}, "sha": self.source, "ref": "research/source"},
              "base": {"repo": {"full_name": repair.REPOSITORY}}}
        with mock.patch.object(repair, "api", return_value=pr):
            repair.lease(1, self.source)
            with self.assertRaisesRegex(RuntimeError, "lease changed"):
                repair.lease(1, self.valid)
            pr["head"]["repo"]["full_name"] = "other/fork"
            with self.assertRaisesRegex(RuntimeError, "lease changed"):
                repair.lease(1, self.source)

    def test_idempotent_publication_dispatches_only_the_exact_companion(self):
        expected = repair.prepare(self.candidate, self.control, self.source)
        repair.git(self.candidate, "checkout", "--detach", self.source)
        receipts = self.base / "receipts"
        for platform in ("linux", "windows"):
            directory = receipts / ("atlas-qualification-" + platform)
            directory.mkdir(parents=True)
            (directory / "receipt.json").write_text(json.dumps(expected), encoding="utf-8")
        jobs = {"jobs": [{"name": "atlas-qualification (" + name + ")",
                          "status": "completed", "conclusion": "success"}
                         for name in ("linux", "windows")]}
        with (mock.patch.object(repair, "lease"), mock.patch.object(repair, "api", side_effect=[
                jobs, {"object": {"sha": expected["companion"]}}, {"workflow_runs": []}, None]) as api,
                mock.patch.dict(os.environ, GITHUB_RUN_ID="1")):
            repair.publish(self.candidate, self.control, self.source, 1, receipts)
            writes = [call for call in api.call_args_list if len(call.args) > 1]
            self.assertEqual(len(writes), 1)
            self.assertEqual(writes[0].args[1:], ("POST", {"ref": "atlas/automatic/" + self.source}))
            self.assertTrue(writes[0].args[0].endswith("/yggdrasil-g29-atlas.yml/dispatches"))

    def test_disagreeing_os_receipt_refused_before_any_api_write(self):
        expected = repair.prepare(self.candidate, self.control, self.source)
        repair.git(self.candidate, "checkout", "--detach", self.source)
        receipts = self.base / "receipts"
        for platform in ("linux", "windows"):
            directory = receipts / ("atlas-qualification-" + platform)
            directory.mkdir(parents=True)
            value = dict(expected)
            if platform == "windows":
                value["companion"] = "0" * 40
            (directory / "receipt.json").write_text(json.dumps(value), encoding="utf-8")
        with mock.patch.object(repair, "lease"), mock.patch.object(repair, "api") as api:
            with self.assertRaisesRegex(RuntimeError, "independent reconstruction"):
                repair.publish(self.candidate, self.control, self.source, 1, receipts)
            api.assert_not_called()


if __name__ == "__main__":
    unittest.main()
