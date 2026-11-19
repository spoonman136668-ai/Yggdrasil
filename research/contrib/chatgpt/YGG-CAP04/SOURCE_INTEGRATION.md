# CAP04 source-auditor integration — isolated engineering candidate

This branch combines the previously qualified independent CAP04 fixture-auditor candidate (PR #1324, source `abb6d8b33997c58726b74f77ba424c64a0413a28`) with the source-contract staging files from `research/ygg-cap04-prospective-source-staging-20261119` at `87e8e39e4a9e37e1660da53f4ec3b55b1ffbb529`.

## Scoped change

- `prospective_source.py`: deterministic, 96-step A/B/A causal source *construction* for **named engineering fixtures only**. Learner-visible rows omit source's hidden phase and latent variables.
- `tests/test_cap04_prospective_source_contract.py`: registered-first-use fail-closed, disjointness, state continuity, and uniform action schedule coverage.
- These files are additive; existing native/JEPA checkpoints, frozen preregistration, original episode histories and the independent fixture auditor remain unchanged.
- The registered DEV/pilot/primary seeds are *not runnable* by this branch's first-use interface; it raises `REGISTERED_FIRST_USE_FORBIDDEN`.

## Qualification boundary

The additive source/test blobs previously passed 3/3 focused fixture tests on Ubuntu and Windows, with byte-equal SHA-256 source identity (Actions run #44540549609). **That earlier pass does not qualify this integrated tree.** This branch requires pinned G29 reanchor followed by a complete new source-exact two-OS regression before any engineering integration claim. The active PR is left untouched; this branch is not accepted, promoted, or running scientific training.

Registered cohorts 99917, 99931, 100017, 100031, 100117, 100131, and 100151 remain unused; further source-first-use requires separate explicit approval and qualification. No Forge/owner/runner/scheduler modifications, no paid model services.
