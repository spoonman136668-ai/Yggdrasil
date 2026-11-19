# CKAD43 — Persistent native causal-rule specialists and old-rule recovery

**Research development only**, stacked on CKAD42-EXACT source on draft PR #1296 at `d477f4f2c4eec401c66cb6b66fffc6d78edd8a39`. **Frozen preregistration first:** `8f94cffb5e61be109038ba6f3611ee209161ce1c`, committed before code and original DEV observations. Original CKAD42 science remains `DEV_NO_GO` and is not replayed.

## Hypothesis, not a working capability

CKAD42 direct tokenless causal intervention weights improved prediction against original native on a couple of development seeds, but the all-purpose mixture was inferior to its best fixed discounted component and suffered early return-to-A retention. This isolated successor tests whether **two persistent, independently source-trained rule hypotheses** can retain old A while acquiring changed B, then recognize a returning A solely from prequential genuine outcomes.

A continuous original Yggdrasil `NativeEpisodeExperience(repair=True)` trains on all observations without modification. Independently, the existing CKAD42 exact-restoration `NativeInterventionRelations` trains on all observations and supplies fully trained full/discount0.93/dual baselines. The candidate starts one causal A specialist; after 48 warm real synthetic episodes, if its previous 12 witnessed prequential two-stage Brier scores average more than 0.21, it allocates an untrained B specialist. There is **no reinitialization of A** and no old-source observation replay masquerading as fresh source. From then on only the currently selected specialist learns from each newly revealed public action/transition/terminal consequence.

When B has learned at least 16 genuine observations and 8 events have elapsed since activation, the previous 12 **prequential** losses of both A and B models determine whether one is a minimum 0.035 Brier better. A/B identity, world number, source-generation rule, future outcomes and change boundaries are never part of the learned readout; private regime and phase tags are only used after forecasts for evaluator reporting.

Every observed event trains the original continuous model and baseline control models once and **exactly one candidate specialist**. No paid inference, large language model, transformer or tokenization is involved. This doubles/triples some learning and forecast compute; efficiency is not a claim.

## Mandatory comparisons and frozen DEV stop

Same genuinely observed stochastic synthetic A→B→A source events and actions in every control: unchanged original native, cumulative learned causal full, discounted .93, dual, independently fitted Beta full/window12/24/48/discount85/95 plus their prequential Hedge, "always A" and "never switch B" candidate ablations, sham.

Fresh source DEV seeds **43111,43112**, two worlds each. Pilots **43211,43212** and primary **43311,43312,43313** are inaccessible from the CLI. No prior CKAD39–42 seeds are run.

The candidate must, **on each DEV seed**, reach pooled late B + late return A Brier <= 0.15 and improvement >= 0.01 against **the best** trained original/native/causal/Beta/Hedge comparator. Additionally late-return A Brier must beat original native by >= 0.02; early-return A Brier may worsen by no more than 0.005 and late-B by no more than 0.005. Both worlds must preserve two trained specialist checkpoint sources, existing original native source, exact byte-identical cold restoration and source conflict atomicity. Any failure is **DEV_NO_GO**; no original seed replays or post-result tuning. A development success would be `DEV_FEASIBLE_NOT_SCIENTIFIC` until independent unfamiliar-world tests and scientific owner acceptance.

This is **not** a novel-world transfer benchmark: it intentionally reuses existing binary stochastic worlds so that a single new recurrence mechanism can be falsified against established strong controls. No accepted main, native checkpoint ABI, autonomous Forge/Yggdrasil loop, or official first-use state is altered.

## Reproduce isolated DEV

```bash
PYTHONPATH=. python -B -m unittest discover -s research/contrib/chatgpt/CKAD-43 -p test_ckad43.py -v
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-43/campaign.py --mode preflight
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-43/screen_dev.py
```

GitHub workflow runs independently on Ubuntu and Windows from an exact source SHA and only on the `ci(ckad43): frozen source development-only qualification` commit. The final DEV classification must be preserved as an in-repo receipt, including all negative results, platform checkpoint hashes, exact source/tree, and measured wall/CPU time. No full final repo regression, merge, owner scientific first-use, runtime controller, scheduled task or paid API is implied by this standalone development screen.
