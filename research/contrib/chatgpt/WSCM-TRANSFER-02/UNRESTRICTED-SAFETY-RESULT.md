# WSCM-TRANSFER-02 — unrestricted-wiring fail-closed readout and root test discovery

**Status (2026-11-23): FOCUSED SOURCE-FREE ENGINEERING PASS; COMPLETE NATIVE INTEGRATION AND CROSS-OS FULL REGRESSION UNVERIFIED.** No scientific-gain claim, protected-world action, or deployment.

## Exact custody

- Research branch parent for safety prereg: `8c6f2a7c9f61abb291f4488670de1f7c2d95cd25`, tree `da151d8930013cccfdeb3b700946ce37d92d4406`.
- Frozen safety prereg: `cd8eed72fb4c4c1cff7cb923eff84f2c67936fb5`.
- Source + tests committed at `9cb8f40189e373973fbf48ceee0998d7989d4853`, tree `85ad4e6b4197013424b83a89903d8d8cb0c98e0f`.
- Root-discovery repair prereg: `dd6edd28fe07a005e0303e82bfd04c2223249ea3`.
- Import-only three-test repair committed at `e8dba9f2d3527dd5ebccf51734f3ea7bcd5a6518`, tree `df48165e1141347d757cea418b2c669e27c43dab`.
- Original development proposer `composition_wire_dev.py` remains byte-identical, Git blob `80d379f216279465f63879b38041f91f65b51cd0`.
- New unrestricted readout blob `a29be47fa3531e01ad6215f82bac74f6f9ea4430`; revised new test blob `3b94c315bccf8d971db6461f525256e6e0ed8473`; revised original proposer test blob `979f941e631e52f2a3a2704bb9d2dd5338dd21a8`. Local `git hash-object` matched all four committed blobs.
- Native component test changed **only** its repository-root import preamble; revised blob `0b7a483a96444876e2f54c902c2fc6baaf9c61e8`. It was **not run** on this current source candidate.

## What changed and why

Existing fixed-four-wiring readout gave a `HYPOTHESIS` on the unobserved query after two disclosed traces. The prior exhaustive unrestricted test showed 16 compatible mappings, eight giving bit 0 and eight bit 1. **That single-bit hypothesis was not a justified unrestricted-model conclusion.**

The new, separate `propose_unrestricted_safe_composition` wraps the existing input-validated proposer. On a nonconstant second-action signature at an unobserved query it now returns `ABSTAIN` with null bit, exact compatible-map count and set-valued `[0,1]`. If the fully witnessed second-stage function is constant, a pure conditional `INVARIANT` result is allowed, explicitly **not transfer**. A trace inconsistent with the *restricted* supplied grammar is no longer misreported as contradiction in the unrestricted case; truly conflicting same-state traces still reject. Original native packages and historical proposer are untouched.

### Focused tests actually executed

Environment: isolated local Linux, CPython 3.13.5, no network dependency. Original proposer source plus new wrapper and test modules reconstructed byte-identically from GitHub or from the locally authored Git blob, then verified using `git hash-object`.

- Initially `python -B -m unittest discover -s tests -p 'test_wscm_transfer02_unrestricted_safe_readout.py' -q` with repository-root discovery failed **before running tests**: `ModuleNotFoundError: unrestricted_safe_readout_dev`. Older source-free and native component tests had the same custom research-path assumption. Fix restricted to test import preambles, using `__file__`-relative repo source, was frozen before patch.
- The new 12-test suite also initially had a defective negative fixture choosing the same intermediate as the baseline. That local fixture was corrected **before the source/test commit**. It was a test-fixture issue, **not a failed scientific trial**.
- After fixes: `env -u PYTHONPATH python -B -m unittest discover -s tests -p 'test_wscm_transfer02_*.py' -v` => **24 PASS, 0 FAIL, 0 SKIP** on the locally reconstructed two source-free test modules; same root-discovery command with `python -O -B` => **24 PASS, 0 FAIL, 0 SKIP**.
- Coverage: out-of-class counterexample, exact 16-map set-valued symbolic parity, constant-stage conditional invariant, restricted-grammar mismatch, true contradictory trace, no/one witnessed structure, seen query, absent signature, hidden-label rejection, invalid typed arguments, determinism, no claimed action or source authority. Existing original twelve tests pass unchanged.
- These runs do **not** include the original `NativeEpisodeExperience` integration, full native component tests, source-world authentication, or **mandatory full Windows and Linux regression** on the exact candidate. The current execution sandbox cannot fetch the complete repository checkout. No hosted or self-hosted runner was dispatched.

### Parallel-source drift checkpoint

At this documentation checkpoint, **existing draft PR #1364 had independently advanced** from former `1820b383f43164bf064214cd09cf26a59274f2ff` to `26bb026dbb1e8e6c0ea55ecf78094623b25af15c` (tree `6e0f7cc626509a001cffbb87c4f1ff010df5c28a`). It includes different source work: optional native v9 sparse operator, modified `yggdrasil/native_episode_experience.py` blob `5a77232cdd4a0fda314e47278c9ba0ed109cfd50`, and other files. PR G29 workflow run `45204826436` was `action_required`, **not PASS**. The research branch remained an intentionally frozen, separate descendant of the older original HEAD and has **not** been rebased or independently requalified against new v9. Accepted main remained `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` at the checkpoint. Never inherit old CI success.

## Gate disposition

- ENGINEERING, source-free inference safety: **PASS** 24/24 local both modes on exact source/test blobs; input and negative tests include original predecessor behavior.
- ENGINEERING, full native learner integration: **UNVERIFIED**; parent source changed independently, no full checkout test run.
- ENGINEERING, full final Linux/Windows exact-candidate regression: **UNVERIFIED**.
- SCIENTIFIC: **UNVERIFIED** for novel learning, unfamiliar causal laws, genuine transfer and retained gain. The robust abstention matches a conventional equally informed set-valued symbolic control, so **no measured gain**.
- DEPLOYMENT / accepted-state admission: **HOLD**. Research-only branch, no PR merge, no source-first-use, no runner dispatch, no scheduler, no actor, no external APIs.

**Next gate:** Validate branch compatibility with the newer native v9 episode changes and run all negative, existing, native integration, exact SHA tree and complete dual-platform tests through an explicitly authorized qualification route. If native source or authority is unavailable, report BLOCKED and do not substitute focused source-free PASS for native qualification.
