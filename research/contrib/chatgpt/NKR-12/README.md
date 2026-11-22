# NKR-12 — Out-of-family and noisy-feedback falsification

**Goal:** Stress-test the exact existing NKR-11 intervention learner against action–consequence relationships it cannot represent, using independently observed outcomes and an equally informed broader symbolic comparator. This is an engineering and scientific-diagnostic falsification, not an attempt to retune the prior NKR-11 success.

## Frozen provenance

- Parent [NKR-11 draft PR #1145](https://github.com/spoonman136668-ai/Yggdrasil/pull/1145), **exact SHA** `e67a24af2cff1d9b4599c5bb7681813e6740aa05`, tree `3c199979440e7ce2f7b0d3b48e6f9be6289e6d15`.
- NKR-11 finished full regression 118/118 on Ubuntu/Windows, learned 12 designed parity-action worlds at 192/192 cold predictions and retained 384/384 prior observations, but independently fully fitted exhaustive symbolic control tied exactly 192/192. Scientific improvement over strongest control was **zero**, accepted `main=5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` unchanged.
- Frozen NKR-12 prereg **FIRST** commit `7a0342dd9d9a79470887dfa579635147d86dbade`, created before any implementation or results. No new use of the full 21,343,681-row consumed Wikidata historical image, official valid/test, external authentic intervention dataset, or owner-scoped actual runner.

## Exposure: incomplete causal hypothesis family

The existing `yggdrasil.native_intervention_repair.NativeInterventionRepair` fits a **prespecified 10-feature parity/GF(2) family**. It can represent action effects that are parity combinations of individual context bits, but cannot represent a pure conjunction such as “action effect only when both x0 and x1 are true.”

NKR-12 freezes **12** deterministic computational environments with new public outcome

```text
parity(context AND fixed_base_mask) XOR
  (public_action AND int(all bits of fixed_AND_mask are present))
```

The AND masks, in order, are `[3,5,6,9,10,12,7,11,13,14,15,7]`, representing 2-, 3-, and 4-way dependencies. The old memory is trained from all 16 contexts × both actions, then snapshotted. The new learner sees only **16 actual selected and returned public outcomes** on frozen training contexts `[0,1,2,4,8,3,5,10]`. It does not receive a phase flag, true context mask, hidden label or private test target. Source bundles are SHA-pinned, and 8 other contexts `[6,7,9,11,12,13,14,15]`, both actions, remain out of learning and are evaluated after checkpoint update.

This design can show **two distinct failure modes**, both kept:
1. Directly contradictory new outcomes that cannot fit any fixed GF(2) signature, producing a bounded rejected-repair error with the old checkpoint unchanged.
2. A previously unseen conjunction is *not triggered* in training, so the parity learner may fit observed data exactly but report false confidence on an unseen conjunction context.

Both forms are explicitly counted. A rejected repair is *not* silently converted into a science failure of action learning; a confident wrong prediction is a genuine representation/identifiability limitation.

## One misleading observation

Four separate worlds keep the **old environment mechanism unchanged**, but corrupt exactly the first public outcome bit of the new 16-observation bundle. This intentionally causes one false local contradiction. The diagnostic records whether the original native learner refuses inconsistent evidence or incorrectly persists a new mechanism, and confirms unchanged old memory.

The independent stronger comparator does not call the native GF(2) learner. It infers the source-visible parity intercept/main effects, **enumerates every 1..15 conjunction mask**, filters to masks exactly matching the same 16 new outcomes, and predicts a cold consequence only where *every surviving mask agrees*. If multiple evidence-consistent masks disagree, it abstains. This comparator has **the correct conjunction hypothesis family preprogrammed**; success is not de novo operator invention and not superiority for Yggdrasil.

The frozen falsification criterion requires (a) at least one confident wrong native cold prediction, (b) at least one source-bundle rejected for inconsistent new evidence, (c) at least one case where the broader equally informed comparator abstains on native false confidence, (d) the original **384/384** warm memory retained, (e) no false persisted repair on four one-bit-noise worlds, and (f) 12/12 first contradictions. If the preset criteria fail, record the null outcome without changing masks, contexts, thresholds, controls or labels.

## Scope and mandatory acceptance

Only new source-safe experiment/negative-test files and G29 generated-only source-index artifacts. No changes to `yggdrasil.native_intervention_repair`, original YPC1 native cells, NKR-05 full historical fact store, accepted `main`, live cognitive owner, autonomous research controller, runner registration, paid API or scheduled tasks.

- Focused NKR-12 tests and synthetic experiment on existing GitHub-hosted Ubuntu and Windows; source, split, noise injection and strong control checked separately.
- Generate **exactly 3** derived `.ice/code-atlas.{json,ice,html}` artifacts once at a pinned source SHA.
- Mandatory final full root regression and independent G29 on Ubuntu and Windows at exact final SHA/tree, with no source drift.
- Log the frozen result and any failure or null; **no scientific first-use or real-world scientific PASS** can follow from this self-generated deterministic experiment.

**If the fixed-family limitation is exposed**, next worthwhile research is a separately preregistered *new operator-selection mechanism* that recognizes genuine contradictions without overreacting to one corrupted public outcome, and learns novel action/context conjunctions under an actual constrained intervention budget. This PR diagnoses the gap; it does not pretend to have solved it.

**Status initially:** DRAFT / source-safe engineering qualification underway, no accepted native integration or deployment.
