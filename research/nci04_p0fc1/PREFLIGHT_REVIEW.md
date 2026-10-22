# P0F-C1 protocol preflight — fail-closed source audit

**Status:** DESIGN REVIEW FAILED / EXECUTION NOT AUTHORIZED. This is an engineering static review attached to the isolated protocol-only branch, not independent scientific validation or a retroactive amendment of the original protocol. The protocol file `PROTOCOL_DESIGN.md` remains immutable at original blob `bd347fde2042d03b40414057d92ed240f3f0f39d` (commit `188dd247e8762aac4fb232db663667feb5700d52`). Exact branch parent is protected `main` `9b069040feeddd9f509ab2c8ac9656d0a2c07d77`. Work item [#407](https://github.com/spoonman136668-ai/Yggdrasil/issues/407).

## Check A — native model/target interface: FAIL

Yggdrasil S4C1 `research/nci04_s4c1/native_predictive_quotient.py`, blob `32d090785f7f3b95c132ebba5ca965b3ece2bc95`, exact S4C1 head `8e1561eb1a542e21307bac669c42435cf48e59bd`:
- `PARAMETERS=45`; `g` shape `(3,7)` = 21 weights and `roles` shape `(8,3)` = 24, one retained state scalar per cell.
- `cell_public_features(x)` specifically requires `x.shape == (23,)`; existing original `forward(episode)` emits `ps.shape == (steps,8)` with eight independent Bernoulli probabilities `p=1/(1+exp(-u))`.
- `analytic_bptt` and `bernoulli_ce` explicitly expect old eight-bit original-target `y`; no implementation of a normalized categorical next-public-value decoder, 256-way softmax or corresponding gradients.
- The new protocol requires `steps x 147 x 256` categorical probabilities for Farama (37,632 probabilities per step), and `steps x 70 x 256` for Pycolab (17,920 per step). The existing model emits **8** values, not these distributions. The existing lossy 23-feature encoder also does not equip its state with a full-current-public input. A decoder that adds new learned coefficients changes original S4C1's 45-slot constraint and cannot be silently introduced. A fixed/shared/structured decoder is not disproven theoretically, but does **NOT** exist or have a qualified resource/equivalence audit.
- **Decision:** Block the 45-slot Ygg architectural comparison arm. No attempt at retraining S4C1 or reclassifying its failed exact cross-run checkpoint reproducibility. A distinct successor model with a properly accounted output interface requires its own prior protocol review, independent source cohorts and separately qualified implementation.

## Check B — conventional-control reproducibility: FAIL

`PROTOCOL_DESIGN.md` requires genuinely trained **complete-current-public** memoryless, recurrent, Bayesian and symbolic controls, but does not specify their exact output parameterization, architecture/capacity, initialization seeds, optimizer and convergence budget, checkpoint-selection metric, training-side hyperparameter selection space, categorical class smoothing, resource caps or stop rules. These degrees of freedom must be frozen **before** training or held-development data are generated. Complete-public frame sizes differ by original source (147 Farama vs 70 masked Pycolab), requiring distinct declared input-head contracts. Thus it is not ready as an executable falsifiable experiment even after choosing to omit the 45-slot candidate.

**Decision:** Block native model and conventional-control experimental execution pending a complete, prospective versioned protocol. Do not exploit consumed MR34F/S4C0/S4C1 held outcomes to tune those settings. Keep the 0.005 nats/byte, 8/12 cluster, paired 95% CI and cross-platform tolerance from the original design attached as *proposed criteria*; no acceptance threshold adjustment from new outcomes.

## Check C — prospective reset-seed arithmetic and bounded collision search: PARTIAL PASS, not custody-qualified

The original file lists:
- Engineering resets (4): 699901, 699907, 699911, 699931.
- Training resets (24): 700101, 700103, 700109, 700127, 700129, 700171, 700181, 700201, 700211, 700223, 700237, 700249, 700271, 700277, 700279, 700303, 700307, 700319, 700333, 700339, 700361, 700369, 700381, 700391.
- Held DEV resets (12): 701101, 701107, 701111, 701117, 701147, 701159, 701171, 701181, 701201, 701209, 701213, 701219.

All 40 distinct integers are unique across those three partitions. No proposed reset integer was present in the historical frozen protocol **file contents examined at the exact pinned PR heads**:
- S4A #394 `research/nci04_s4a/frozen_protocol.json`, blob `fff3a1982f1ebda916dcd6153396ab2c47e92209`;
- MR34E #395 `research/mr34e/frozen_protocol.json`, blob `80e77cb06d91fa3f80103244d443c792504c8a61`;
- MR34F #396 `research/mr34f/frozen_protocol.json`, blob `f0c757b91017799a3112c7d0587b0ccd91bd9fad`;
- S4C0 #398 `research/nci04_s4c0/frozen_protocol.json`, blob `8c0a1636b0bb10b9aec36863cf88195b079fd0b6`;
- S4C1 #400 `research/nci04_s4c1/frozen_protocol.json`, blob `a77ff940887b18de3260955cefd68aa27b837f51`.

GitHub default-branch code searches for representative 699901/700101/701101/701219 returned no matches; default-branch code search cannot establish absence in all unmerged branches, independent custody ledgers, other repositories, earlier offline experiments, or protected-first-use allocations. **Independent source-birth ledger review is REQUIRED; full collision-clearance NOT VERIFIED.** The present provisional seeds must not be consumed or considered assigned first-use cohorts.

## Check D — source custody, replay and scientific authority: PENDING

The publicly pinned original source Git SHA requests can be source-audited, but no new 4× Windows/Linux qualification, runtime categorical-output feasibility, actor-intervention coverage, upstream license clearance, trained-control adequacy, G29 source atlas or final whole-tree regression has been executed for P0F-C1. CKB-plane remains sole execution authority. Historical qualified MR34E source observational aliases are valid *development* opportunity, not proof of history's prospective predictive necessity; MR34F strict NO-GO and S4C1 strict checkpoint NO-GO unchanged.

## Overall preflight

`P0FC1_PROTOCOL_STATIC_REVIEW=FAIL_CLOSED`
`P0FC1_SEEDS_INTERNAL_UNIQUE=PASS_40_OF_40`
`P0FC1_SEEDS_HISTORIC_5_PROTOCOLS_NO_COLLISION=PASS_BOUNDED`
`P0FC1_REPOSITORY_WIDE_CONSUMED_LEDGER=NOT_VERIFIED`
`P0FC1_NATIVE_45_SLOT_CATEGORICAL_DECODER=NOT_IMPLEMENTED`
`P0FC1_CONVENTIONAL_CONTROLS_FULLY_FROZEN=FALSE`
`P0FC1_SCIENTIFIC_FIRST_USE=BLOCKED`
`P0FC1_NEW_SOURCE_EXECUTION=NONE`

**Next permissible bounded step:** Revise the design as a **separately versioned protocol, BEFORE any source execution**, with (1) an executable, capacity-costed categorical output interface and complete-current-public competent comparator details, and (2) independent consumed-ledger witness/custody review. The qualified next research question may be **conventional public-history information necessity only**; native 45-slot self-organizing state cannot be claimed on this categorical task without a new model whose source, training, readout, and resource terms independently qualify. Preserve original protocol and this negative; do not promote, merge, or bypass admission controls.
