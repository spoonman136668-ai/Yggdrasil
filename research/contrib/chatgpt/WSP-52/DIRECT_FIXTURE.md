# WSP52 — direct numerical weight writer, SELFTEST qualification

**Research candidate only.** Parent WSP47 `9e6374119602ea57e479a1b36a35a5c0e932b4e1`; immutable WSP52 preregistration `8cea083b5c230663b9a9dccfc8089a77f1c4c729`.
Original parent PR #943 (draft). No registered DEV, protected PRIMARY, science acceptance, or model training was run.

## Mechanism and interfaces

- `direct_writer.py` consumes *only* learner-facing complete undelimited binary acoustic streams and before/after physical states. The evaluator retains generator codewords, order, true roles, and heldout targets. Its finite 4..6-bit three-segment candidate family is a **preprogrammed structural prior** and not learned arbitrary segmentation or natural-language capability.
- For each observed **changed** physical state, derive entity index and final location *from the visible state difference*. Write integer evidence counts into separate entity-candidate and residual-effect-candidate numerical association matrices; do not execute gradient updates. No-op experiences are charged but do not label a non-observable entity.
- Predict from intersections of grounded entity and residual-effect evidence. Require at least two consistent supporting appearances in both associations; abstain on inconsistent candidate votes or similar competing predictions. Bound hypothesis count to at most 27 stream segmentations and 20,000 numeric weight entries; over-capacity fails explicitly. Do not convert these hand-written constraints into a claim of grammar discovery.
- Snapshot all numeric association counts, evidence-conflict state, action counters and a SHA-256 check. Restore rejects tampering/noncanonical snapshots. The full serialized memory cost is reported, not just numeric weight entries.
- Reuse `fixture_harness.py` evaluator seam and original `run_selftest_controls` unmodified. Add `run_selftest_writer` guarded to SELFTEST and report A, B, post-B retention, exact cold parity, and false-confidence errors.

## Local exploratory fixtures (non-scientific)

The following were obtained only with `build_world('SELFTEST', seed, encoding)` on 2026-11-12, Python 3.13.5. Every condition had 36 phase-A + 6 phase-B charged learning actions and **zero optimizer steps**. No hidden-grammar fields were supplied to the learner. These results must not be used to select thresholds after registered DEV/PRIMARY access.

| Fixture | A correct /60 | A wrong confident | B correct /90 | A retention correct /60 | A retention wrong confident |
|---|---:|---:|---:|---:|---:|
| 9001 identity | 40 | 0 | 2 | 40 | 0 |
| 9001 permuted | 16 | 5 | 0 | 16 | 6 |
| 9001 rotated | 39 | 0 | 3 | 39 | 0 |
| 9002 identity | 45 | 0 | 5 | 45 | 0 |
| 9002 permuted | 41 | 0 | 0 | 41 | 0 |
| 9002 rotated | 40 | 0 | 6 | 40 | 0 |
| **Aggregate** | **221 / 360** | **5** | **16 / 540** | **221 / 360** | **6** |

The exact whole-stream and erased controls score 0 on previously unshown combinations in these source-only fixtures. This does **not** qualify the pure writer against the preregistered strong symbolic or fully trained neural comparator. This early heuristic produces incorrect confident predictions and nearly no phase-B generalization; it **does not meet the WSP52 scientific target**. Keep these negative outcomes visible.

Post-B persistent serialized state ranges 125,424–153,248 bits per condition. Numeric weight entries range 601–766. This is a **different memory/capacity budget** from the existing control arms; no equal-capacity or improved-efficiency claim is made. Whole-process CPU/FLOP and true cost matching are still unmeasured.

## Qualification

Local Python structural unit suite: `python -m unittest -v test_source.py test_direct_writer.py`: 13/13 PASS. Existing `test_controls.py` is preserved and included in the inherited Linux/Windows CI discovery job. The exact final candidate SHA still requires final G29/source-atlas pin and complete Linux/Windows WSP01–47 regression. No protected first-use.

**Next scientific engineering work:** implement fully trained temporal and exhaustive symbolic baselines with capacity/cost receipts, negative controls (including phase-B grammar transfer), independently review source and decide the unidentifiable destination+verb semantics before registered DEV. No official Yggdrasil loop/merge/deployment/runner scheduling authority was exercised.
