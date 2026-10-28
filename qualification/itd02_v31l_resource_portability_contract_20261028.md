# V31L — Windows POSIX-only resource portability (qualification-only; freeze before code)

Exact parent: V31K draft #635 at `6ceac70a1e827fb1fdb72503e1ff767f47e376ab`, with G29 index already qualified on both Windows and Ubuntu. This is the first V31L commit before code or tests. Native original, V22, V31I/V31J learners, sources, reserved holdouts, protected main and all prior experiments are immutable.

## Diagnosed failures

The V31K Ubuntu 138-test full regression was green; exact generated G29 Windows/Linux was green. Windows full discovery encountered THREE `ModuleNotFoundError: resource` errors: `test_free_fanout_sidecar`, `test_nci04g6_native_credit`, `test_nci04g7_source_producer`. The first imports POSIX `resource` from a Linux-only workflow's candidate-sidecar script; the latter two import it in resource observation tests. Neither the Linux child peak RSS nor POSIX `ru_utime/ru_stime` accounting is implemented on Windows. This gate chooses the explicitly documented Yggdrasil issue #517 OPTION A: Windows resource measurement **unsupported/fail-closed**, not an unqualified native Windows measurement provider.

## Frozen implementation contract

- Keep `scripts/free_fanout_sidecar.py` Linux behavior and its real `resource.getrusage(RUSAGE_CHILDREN)`, `ru_maxrss`, elapsed and CPU checks unchanged. Make optional import possible on Windows but reject `run_candidate` immediately with `FREE_FANOUT_RESOURCE_ACCOUNTING_UNAVAILABLE` **before any candidate config/output/source process spawn**, when the module is unavailable. No zero, None, hidden fallback, guessed measurements or partial results.
- Allow Windows to execute the sidecar's offline schema, manifest, path and static workflow tests. Only the two tests requiring a genuine resource-accounted candidate subprocess may be **explicitly skipped** on non-POSIX. Add a cross-platform negative test that replaces the resource dependency with unavailable and verifies fail-closed before any candidate dispatch. On POSIX these two real subprocess tests must continue to pass unchanged.
- Allow Windows to execute NCI-04G6/G7 non-resource structural/negative tests. Only `test_existing_roles_learn_from_own_measured_residual_only` and `test_separate_native_model_output_and_equal_information_controls` may be **explicitly skipped** when `resource` is absent. Keep actual POSIX `resource.getrusage` observations and metric comparisons unchanged on Linux. No test deletion, silent test omission or pretense that all Windows resource evidence is qualified.
- Strict source delta: THIS note, the single sidecar Python module, exactly three test modules (sidecar, G6, G7), and an isolated one-shot G29/source qualification workflow. An automated bot may add only the three derived `.ice/code-atlas.{json,html,ice}` files on the exact source commit. Model weights/learning semantics, Linux resource bounds, science data, source origin and FORGE/CKB-plane are out of scope.

## Acceptance

Before G29 generation, run targeted POSIX tests and negative boundary. Source-only branch and first-commit provenance must be pinned. One-shot derived Atlas commit must pin source and pass G29 checks; then **full Linux test discovery** with all original runtime/resource tests must pass, **full Windows test discovery with exactly four explicit resource-dependent skips and zero import errors/failures** must pass, including the new fail-closed negative. Collect exact test counts and note that Windows skipped tests are unqualified, not passed. Repeat source-specific V31I/V31J invariant checks and independent cross-host G29 readback. All changes DRAFT/unmerged/NO SCIENCE; no production/model promotion, controller/runner/queue edits, new experimental holdout, or accepted-ref mutation.

**No scientific first-use** is granted. The previous V31J 112,128 unmetered simulated scalar hops remain intact; this gate does not certify retail CPU/RAM, physical network bytes, or any self-improvement result.
