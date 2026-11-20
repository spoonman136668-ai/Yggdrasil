# ARCHIVE-REGIME-OVERLAP-05 — historical active-context contradiction

Classification: RETROSPECTIVE SOURCE-ONLY ENGINEERING DIAGNOSTIC. The archived 1,025 witnesses were consumed in development training. This report is not independently held scientific evidence or native knowledge acquisition.

## Exact evidence
- Yggdrasil accepted main: 5e74f8db85b2f5839c42148c0dfba69a88b1a2c9; sole canonical Amalgam Work draft: PR #1278. Contributor draft #1326 remains unmerged.
- Original research source commit: e9aa921c57dca836c06c7125e52229cce728620a. Synthetic source file SHA256: 20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef.
- Historical GitHub Actions run #44499793023; artifact #14517860401; ZIP SHA256 b8504c3a9f0e44185380687f7ce3f0a7ad0347c5be03c1cd51dc3aa1bbc1051d.
- Exact original member amalgam-joint-state.json SHA256 576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8; saved native snapshot has 1,025 episodes.
- Read-only native source yggdrasil/native_episode_experience.py blob 5a18b00a4c4131526e71f51d63dfd9eb9471c81e. Its _load_context(start, novel=True) creates a new hypothesis member; _update_context scores each event and revises that member from original context_start onward. Source family/regime labels are not passed to the learner.

## What the preserved checkpoint actually contains
At context_start=891, stream_start=448, refresh_start=832, novel=true, the same active novel hypothesis has 134 already-consumed events crossing two source-world changes:

| Ordinals [start,stop) | Evaluator-only source world | Events |
|---|---|---:|
| [891,912) | terminal_switch regime 0 (tail) | 21 |
| [912,976) | context_switch regime 1 | 64 |
| [976,1024) | invariant regime 0 | 48 |
| [1024,1025) | fixed engineering fixture | 1 |

All 133 CKAD25 rows in the active window have exact recomputed original seed 56101, coverage_active arm, source-event IDs, phase order, binary public views and episode schemas. The final fixed receipt has its exact original identifier.

## Historical A/B/A contrast: same public initial state s1=0
Source phase labels are available to an OFFLINE evaluator only; they are not learned inputs.

| Phase | x1=0: observed P(s2=1) | x1=1: observed P(s2=1) |
|---|---:|---:|
| Before: terminal_switch regime 0 | 2/8 = 25.0% | 6/6 = 100.0% |
| Middle: context_switch regime 1 | 15/17 = 88.2% | 3/18 = 16.7% |
| After: invariant regime 0 | 2/14 = 14.3% | 12/13 = 92.3% |

Both actions reverse during the middle source regime and return near their earlier directions afterward, exactly the kind of cumulative interference/retention challenge that source-free synthetic gates were intended to expose. This observation is a historical source-law change, not a measurement of the native model's competence. A mixture of old models might still forecast correctly; actual learned prediction, selection, cold retention and held-out transfer were NOT evaluated in this audit. No causal gain, benchmark win or resource efficiency improvement can be inferred.

## Reproduction and qualification limits
- New archive_regime_overlap_audit.py is read-only Python standard library: validate original ZIP and member SHA256, schema, context-start identity and every original recent ID, emit ONLY aggregate phase counts. No model import, source generator, action, checkpoint write or trainer.
- New tests/test_amalgam_archive_regime_overlap.py runs eight source-free negative / source-identity checks. Exact Git blobs: source b83490aecf4f8ddcb09d41c5c457cc71642dbcd8; tests 3dc4c442d136c34dec1f5b75f4a188aead5dd29d. Original local archive and focused tests: PASS, 8/8.
- The archived ZIP is not in Git. GitHub CI cannot claim archived-input verification from unit tests alone unless independently provided the exact source artifact.
- Previous candidate full regression fails four frozen Gate25 tests on both OS (run 44715010036); those negatives have not been rewritten or waived. Full exact-final regression must be classified separately; it cannot be accepted unless all inherited tests pass.
- Scientific improvement UNVERIFIED; protected original-world first use remains unauthorized under issue #426. No owner model, checkpoint, accepted main, canonical Amalgam branch, scheduler, merge or deployment affected. This contributor report is not promotion authority.
