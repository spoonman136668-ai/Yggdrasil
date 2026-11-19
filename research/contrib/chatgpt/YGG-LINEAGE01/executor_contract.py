"""Source-pinned reason why the official Yggdrasil watchdog does not train.

No model execution, controller mutation, scheduler change, or access to host disks.
"""
from __future__ import annotations
import re

SCRIPT_SHA="ecbe954a7b7a8af61ae3b74e4e8f43713b37e60c"
DOC_SHA="3501ef93794dde2e46c21d223782d7f14f450542"
LAUNCHER_SHA="d09e8954c8448f4ea20a601d2ef5465d759e907b"
REASON="gpt-authored-research-required-no-unattended-model"
OBSERVED_RUN=44522000519
SENTINEL="RESEARCH_EXECUTOR_UNATTENDED=NOT_CONFIGURED_NO_MODEL_INVOCATION"

def require(ok,code):
    if not ok:
        raise ValueError("YGG_LINEAGE01_EXECUTOR_"+code)

def inspect(script,launcher,policy):
    require(all(type(x) is str for x in (script,launcher,policy)),
            "DOCUMENT_TYPES")
    notice="Write-Host '"+SENTINEL+"'"
    marker=("Write-CycleResult -Advanced $false -Reason '"
            +REASON+"' -Head $StartSha")
    require(all(x in script for x in (
        "RESEARCH_AGENT_POLICY=GPT_CHAT_GITHUB_SOURCE_ONLY_NO_CODEX_NO_EXTERNAL_APIS",
        notice,marker)),"EXPLICIT_NO_MODEL_POLICY")
    decision=script.index(marker)
    require(notice in script[:decision],"DISABLED_BEFORE_CYCLE_RESULT")
    require(re.match(r"\s+return\b",script[decision+len(marker):])
            is not None,"TERMINAL_RETURN_REQUIRED")
    require(script.find("Invoke-ScientificRun $Out1")>decision,
            "SCIENCE_CALL_BEHIND_TERMINAL_RETURN")
    lower=policy.lower()
    require("do not invoke any model" in lower and
            "unattended" in lower and "not yet" in lower,
            "CODEX_FREE_OWNER_POLICY")
    require("runs-on: [self-hosted, Windows, X64, yggdrasil, research-only]"
            in launcher,"OWNER_RUNNER_QUALIFIER")
    require("if: steps.config.outputs.enabled == 'true' && steps.cycle.outputs.advanced == 'true'"
            in launcher,"ADVANCE_DISPATCH_FENCE")
    require("ref: main" in launcher,"MAIN_CONTROLLER_CHECKOUT")
    return {
        "schema":"yggdrasil.lineage01.owner-executor-status.v1",
        "source_script_git_blob":SCRIPT_SHA,
        "policy_git_blob":DOC_SHA,
        "launcher_git_blob":LAUNCHER_SHA,
        "unattended_model_execution":"DISABLED_BY_EXPLICIT_EARLY_RETURN",
        "cycle_advanced":False,
        "cycle_reason":REASON,
        "dispatch_if_advanced":"SKIPPED_WHEN_FALSE",
        "owner_runner_in_workflow":"self-hosted Windows research-only",
        "code_reaches_scientific_training":False,
        "accepted_checkpoint_verified":False,
        "owner_host_checkpoint_location":"UNVERIFIED",
        "live_log_corroborating_run_id":OBSERVED_RUN,
        "controller_or_schedule_changed":False,
        "new_authority":False,
        "new_science":False,
    }

def inspect_pinned(git,main,expected):
    for path,sha in (
        ("scripts/Invoke-RepoLocalResearchCycle.ps1",SCRIPT_SHA),
        ("docs/research-executor-codex-free.md",DOC_SHA),
        (".github/workflows/research-auto-launch.yml",LAUNCHER_SHA),
    ):
        require(git("rev-parse",main+":"+path)==sha,
                "PINNED_BLOB:"+path)
    require(expected["executor_script_blob"]==SCRIPT_SHA and
            expected["executor_policy_blob"]==DOC_SHA and
            expected["launcher_blob"]==LAUNCHER_SHA and
            expected["observed_run"]==OBSERVED_RUN,
            "MANIFEST_PINS")
    return inspect(
        git("show",main+":scripts/Invoke-RepoLocalResearchCycle.ps1"),
        git("show",main+":.github/workflows/research-auto-launch.yml"),
        git("show",main+":docs/research-executor-codex-free.md"))
