# NKR-02 — Native relationship transfer, stronger controls and generalization boundary

**Purpose:** Independently qualify the isolated [NKR-01 native Yggdrasil relationship bridge](https://github.com/spoonman136668-ai/Yggdrasil/pull/1092) before any proposal to apply persistent relationships to accepted Yggdrasil main.

## Frozen design and true baseline

First commit `2aedc2a5ab0da62563fca1c8dbd079a18a634f6d` froze this comparison **before the test source, scripts or any outcomes**. Native source parent `dcbc41ca50d9913e682a24833ba0190c66be5ae0`, tree `d278762d20636b13343fa2b3bc63b9b4c309233d`. The native relationship implementation itself, existing `PublicCausalCells`, and all native tests are unchanged by this follow-on research PR. Old YPC1 snapshots remain exactly 164 bytes.

**What this actually tests:** 16 separately SHA256-derived context/action worlds with four binary context variables, two binary actions and 10 observed consequences per world from actual calls to the existing Yggdrasil native observation interfaces. The five training contexts are 0,1,2,4,8, both actions; eleven entirely unobserved test contexts are 3,5,6,7,9,10,11,12,13,14,15, giving **176 disjoint unseen action choices per family**. Duplicate aliases and contradictory evidence cannot manufacture extra learning.

**The independently authored strongest controls:** old Yggdrasil context-free decision policy with exactly the same public observations; algebraic exact symbolic GF2 fitted independently for each action from all its actual observations; a real **2000-step Adam-trained NumPy tanh neural network (32 hidden units)** per source slot with identical public training examples and no test outcomes; and the conservative evidence-only incumbent fallback. GPU/paid APIs/hidden WSP114–115 source data are not used.

**Out-of-family failure probe:** a second independent cohort introduces a contextual quadratic pair effect absent from every public single-bit observation. Its heldout labels cannot be inferred from those public observations by the native method or exact linear symbolic method. By construction this exposes the risk of **confident wrong extrapolation** beyond the native 10-weight grammar, which is a scientific limitation and not a harness error. Record the negative rather than retuning the frozen source or silently adding features. The frozen promotion-safety criterion requires 95% on both distinct source families and no regression versus incumbent.

**Additional checks:** unique evidence vs duplicated aliases; two action predictions vs true consequences; program-level cold replay and exact YPC1 snapshot; no bleed across retained/active cell updates; 16-slot fixed capacity; checkpoint byte costs, full CPU/wall/tracemalloc resource diagnostics. Unit source tests are public fabricated-only and do not consume a protected v1/v2 original. This study **does not test open-domain real-world knowledge**, provider provenance trust, broad understanding, or sufficient science for accepted model promotion.

**First reproducible qualification:** `python -m pip install numpy==2.2.6`, `python -m unittest discover -s research/contrib/chatgpt/NKR-02 -p 'test_*.py' -v`, followed by `python -m unittest discover -s tests -p 'test_*.py' -v`.

**Frozen source-pinned CI**: fabricated prereg fixture Linux/Windows, G29 three generated-only .ice companions pinned to exact source, mandatory full root regression and independent G29 both OS on exact candidate, then one independent original public DEV comparison job; no new controller/scheduler or merge.

**Decision:** In-family success and out-of-family negative closes **MIXED / NO PROMOTION**. Even synthetic two-family success would be DEV only, not automatic production model data ingestion. Native NKR-01 code and Yggdrasil main remain unchanged pending truly independent qualified source and acceptance authority.
