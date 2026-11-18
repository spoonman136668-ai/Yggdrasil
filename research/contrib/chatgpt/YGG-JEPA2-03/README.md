# YGG-JEPA2-03 — Native cumulative temporal JEPA research

**Current gate: source-frozen engineering preflight and development-only continual training.**

This isolated development branch starts from the actual trained YGG-JEPA2-02 native models at their sealed GitHub checkpoint SHAs. No old model weights, original native source ledger, or learned abilities are reset. It introduces *two additional independent temporal-history latent learners* (transition and terminal), which train alongside both existing JEPA heads and the original native `NativeEpisodeExperience` on witnessed intervention consequences. Each temporal expert reads the last eight authentic source events, the currently public views, and chosen actions. The hidden generator regime and scoring phase never enter a learner.

The experiment uses genuinely new **development-only** deterministic source seeds `88901` and `88917` from Yggdrasil's existing CKAD37 intervention generator, two sequential causal worlds per seed, and measures actual prequential consequence prediction against the original cumulative native and fully fitted adaptive conventional controls. These are *not* independently novel physical worlds, scientific first-use, or a replacement for Yggdrasil's general-intelligence target.

The complete protocol and thresholds were committed **before implementation** at `475649fc5eb44b0ecddd41b705a31c02a81661c2`. The frozen success criterion requires a gain over *both* the continuing native learner and strongest matched conventional predictor on *both* replicas, with stable old-source knowledge, cold state persistence, paired-vs-mispaired negative controls and no early-shift/return regression.

**No model promotion on an engineering-only success.** In particular, a negative development result will be preserved without retuning on the consumed source or changing the decision threshold. Accepted `main`, protected source owners, other project models, Forge/controller and runtime remain unchanged.
