# WSCM-TRACE-01 — a bounded eligibility-trace falsification

**Disposition: MECHANISM_EQUIVALENCE_NO_UNIQUE_GAIN.** This is an independently coded conventional-mechanism comparison, *not* a test of native Yggdrasil learning, long-term memory, or unfamiliar-world transfer.

## Custody and freeze
- Existing research contributor: [WSCM-01 PR #1364](https://github.com/spoonman136668-ai/Yggdrasil/pull/1364) stacked on [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278), itself not accepted production.
- Original source W=16 ring pinned to Git blob `c010d7a74cf95cd579223e0b09f09f1d6cbb899c`, from `053bafd38531aee961dadf240ca6164a5dab0ef3`.
- **Pre-scoring protocol commit:** `02cfcf273c706f000175d7aab274db83b4b957c3`; `prereg.json` Git blob `9602fe948924833685ad4ccc9f075e0f39319757`.
- **Code committed before scored run:** `db3f98bbc50598e34da9cab8fde62d39eb1ffd87`; `trial.py` Git blob `71774f29eb6d6f7b99b93f89469e8d115033bdce`. Exactly three local control tests passed before the primary run.
- Primary scored pass: local CPython 3.13.5, Linux x86_64, one deterministic pass after both frozen commits, no protected source action or external model call. Source blob was verified at runtime. The preregistration was independently verified on GitHub; a local copy was not mounted during the scored run, so the trial's optional local prereg blob recheck was not exercised.

## Question and matched conventional control
Could the isolated WSCM W=16 eligibility proposal produce distinctive credit-assignment outputs beyond a conventional finite-horizon TD(λ=0.5) eligibility trace? The conventional control uses the **same** public event history, explicit target-event ID, observed binary outcome, Q8 predicted target probability and surprise threshold. It computes Q15 eligibility iteratively and independently; no ring internal output is used by the control.

Frozen exhaustive deterministic enumeration: prefix lengths 1–17; each target position; target Q8 in [0, 64, 128, 192, 256]; binary observations 0 or 1; one new ring per case. The 17-event prefixes contain 10 expired-target negatives.

## Primary result
- **1,530 / 1,530 exact case matches; 0 mismatches.** Of those, 1,520 were comparable and 10 were expired-target reject cases. The two methods agreed on all 5,712 individual credit-proposal tuples.
- Surprise-gated nonempty proposals: 912 cases; empty due to the same gate: 608 cases. No original-world/protected actions.
- Deterministic trial transcript SHA256: `1d52c98aa3e2cadbb958ba6bb3c3b05a10d816b069457d7337f0b2e9310205ad`.
- Exact `result.json` SHA256: `a609789e6a2158f8ffac39ccde36aee802b07359d54fbc64d117e39d2a74de19`.
- Classification per preregistration: **MECHANISM_EQUIVALENCE_NO_UNIQUE_GAIN**. Stop claiming W16 surprise-gated delayed credit as a distinct learning mechanism. A future full Wake–Sleep successor needs a *different*, prospectively testable gain.

## Reproduction
From the Yggdrasil repository checkout containing this contributor branch:
```sh
python -m unittest discover -s tests -p test_wscm_trace01.py -v
python research/contrib/chatgpt/WSCM-TRACE-01/trial.py --output /tmp/wscm-trace-result.json --provenance /tmp/wscm-trace-provenance.json
```
Output JSON is deterministic for `result.json`. Local runtime environment metadata in `provenance.json` will differ across hosts. The trial refuses altered ring source bytes, and validates the exact prereg blob when checked out alongside it.

## Limitations and disposition
No real charged do-intervention evidence, authenticated role templates, unique learning/update rule, causal necessity analysis, reward-policy improvement, multi-regime retention, open-world transfer, original source first-use, or second operating-system test. The target-event ID is directly available to both methods in these synthetic fixtures; this does not validate latent-cause discovery. Exact tuple equality demonstrates a mechanism tie only; it does **not** prove equal downstream model quality or disprove every possible Wake–Sleep design.

**ENGINEERING**: exact local control test PASS and source-pinned 1,530-case comparison PASS; full parent dual-OS regression UNVERIFIED. **SCIENTIFIC**: mechanistic uniqueness NO-GO; actual training/retention/transfer gains UNVERIFIED. **DEPLOYMENT**: UNVERIFIED, draft unmerged and no Genome, native source, runner, or accepted ref mutation.
