TITLE: YGGDRASIL ISOLATED EXPERIMENT RUNNER CONTRACT
DATE: 2026-09-23
STATUS: ACTIVE INFRASTRUCTURE BOUNDARY
TRACK: DG-1 / RESEARCH HARNESS

PURPOSE

Provide a reusable execution path for Yggdrasil experiments
without coupling the research loop to KTRADE production
or ckb-plane orchestration.

HARD ISOLATION

The isolated runner is permitted to operate only in:

spoonman136668-ai/Yggdrasil

on branch:

dg1a-ar

through:

research/harness/ydr_experiment_runner.py

and:

.github/workflows/ydr-isolated-experiment-runner.yml

The workflow runs only on:

ubuntu-latest

GitHub-hosted runners.

It must not use:

self-hosted runners;

the Windows KTRADE runner;

ckb-plane worker services;

CKB production queues;

KTRADE repositories;

KTRADE runtime processes;

broker/Coinbase services;

TradeGuard;

deployment/promotion authority;

or Mind-Palace mutation.

WORKFLOW PERMISSIONS

Repository permission:

contents: read.

The workflow does not push commits.

It does not alter accepted refs.

It does not mutate experiment source.

It emits execution evidence only as a GitHub Actions artifact.

TRIGGER

The isolated workflow triggers only when:

research/control/isolated-run.json

changes on:

dg1a-ar.

Ordinary Yggdrasil commits do not trigger it.

KTRADE and ckb-plane activity cannot trigger it.

RUNNER COMMAND BOUNDARY

The harness may execute only:

the current Python interpreter

plus

one repository-local .py experiment entry point
under:

research/applications/

No shell command supplied by the experiment request is executed.

No arbitrary executable path is accepted.

No source outside the Yggdrasil repository is accepted.

PRODUCTION-COUPLED TOKEN GUARD

Requests are rejected if they contain known production-coupled references,
including:

ckb-plane;

KTRADE;

self-hosted;

actions.runner.;

C:\actions-runner.

This is a defense-in-depth guard,
not the sole isolation mechanism.

DETERMINISTIC GATE

The runner:

verifies declared file SHA256 identities;

executes the requested primary twice;

captures stdout and stderr separately;

requires the two primary output files to be byte-identical;

records output bytes and SHA256;

and only after duplicate identity
may invoke an optional external open/qualification operation.

If duplicate outputs differ:

fail closed.

If a declared source/file identity differs:

fail closed.

If the experiment returns nonzero:

fail closed.

If the request tries to escape the repository:

fail closed.

EVIDENCE

Artifacts may include:

primary1.bin;

primary2.bin;

run stdout/stderr;

open output;

open stdout/stderr;

evidence.json;

failure.json.

These files are uploaded as workflow artifacts.

They are not automatically committed to the repository.

Scientific interpretation remains a separate step.

RESOURCE / INTERFERENCE BOUNDARY

This runner consumes GitHub-hosted Actions resources only.

It does not consume:

the user's Windows CPU/GPU;

the user's Windows runner;

the ckb-plane authority process;

the KTRADE production loop;

or local broker/runtime resources.

Therefore Yggdrasil experiment execution through this path
is operationally isolated from the KTRADE / ckb-plane production loop.

KNOWN LIMITATION

GitHub-hosted runner provisioning can fail independently of experiment code.

A job that fails before entering experiment steps
is infrastructure failure,
not scientific failure.

Retries must preserve the exact frozen request/source identities.

DECISION

Use this path for future bounded Yggdrasil duplicate-primary execution
when the experiment fits GitHub-hosted resource limits.

Do not migrate Yggdrasil research execution
onto the KTRADE/ckb-plane self-hosted runner
for convenience.

PLAIN-SPEAK SUMMARY

Yggdrasil now gets its own test lane.

It runs on GitHub's machines,
not yours.

It cannot call into KTRADE or ckb-plane through the runner interface.

It cannot push experiment results back by itself.

It runs the exact test twice,
checks that both results are identical,
and only then opens the result.

That lets the research loop become more automatic
without competing with the production loop.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
