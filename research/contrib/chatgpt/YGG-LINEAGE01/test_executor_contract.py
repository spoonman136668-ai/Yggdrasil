"""Negative controls for source-bound official Yggdrasil owner executor state."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("lineage_executor",HERE/"executor_contract.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

SCRIPT=(
 "Write-Host 'RESEARCH_AGENT_POLICY=GPT_CHAT_GITHUB_SOURCE_ONLY_NO_CODEX_NO_EXTERNAL_APIS'\n"
 "Write-Host 'RESEARCH_EXECUTOR_UNATTENDED=NOT_CONFIGURED_NO_MODEL_INVOCATION'\n"
 "Write-CycleResult -Advanced $false -Reason 'gpt-authored-research-required-no-unattended-model' -Head $StartSha\n"
 "    return\n"
 "    Invoke-ScientificRun $Out1\n"
)
LAUNCHER=(
 "name: Yggdrasil research continuation launcher\n"
 "runs-on: [self-hosted, Windows, X64, yggdrasil, research-only]\n"
 "ref: main\n"
 "if: steps.config.outputs.enabled == 'true' && steps.cycle.outputs.advanced == 'true'\n"
)
POLICY="Not yet authorized for unattended tasks; do not invoke any model."

class OwnerExecutorTests(unittest.TestCase):
    def test_intentional_no_model_contract(self):
        r=mod.inspect(SCRIPT,LAUNCHER,POLICY)
        self.assertFalse(r["cycle_advanced"])
        self.assertFalse(r["new_science"])

    def test_missing_return_rejected(self):
        with self.assertRaisesRegex(ValueError,"TERMINAL_RETURN_REQUIRED"):
            mod.inspect(SCRIPT.replace("    return\n",""),LAUNCHER,POLICY)

    def test_missing_no_model_sentinel_rejected(self):
        with self.assertRaisesRegex(ValueError,"EXPLICIT_NO_MODEL_POLICY"):
            mod.inspect(SCRIPT.replace(mod.SENTINEL,"MODEL_READY"),LAUNCHER,POLICY)

    def test_missing_advance_fence_rejected(self):
        with self.assertRaisesRegex(ValueError,"ADVANCE_DISPATCH_FENCE"):
            mod.inspect(SCRIPT,LAUNCHER.replace(" && steps.cycle.outputs.advanced == 'true'",""),POLICY)

    def test_unauthorized_unattended_override_rejected(self):
        with self.assertRaisesRegex(ValueError,"CODEX_FREE_OWNER_POLICY"):
            mod.inspect(SCRIPT,LAUNCHER,"Model execution is configured")

if __name__=="__main__":
    unittest.main()
