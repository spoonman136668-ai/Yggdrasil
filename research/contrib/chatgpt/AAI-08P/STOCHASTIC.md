## Stochastic custody extension, AAI-08P

The unmodified upstream `Bridge.step` uses NumPy's **legacy process-global** `np.random.choice`. The official `env.reset(seed)` therefore does not control stochastic movement by itself. The `stochastic_custody.py` adapter applies a reproducible experiment-level `np.random.seed(seed)` before constructing and resetting one rollout, and restores the caller's entire original global NumPy RNG state afterwards. It does not patch or replace the external simulator.

Sixteen *new reserved mechanical seeds*, 996100–996115, test repeated exact replay under a real official transition distribution shift `[1,0,0] → [.15,.70,.15]` at t=3, a stationary control, independent seeds producing distinct outcomes, unchanged first three outcomes, and exact restoration of caller RNG state. Every output is from actual NS-Gym `step`. No learner and no scientific seeds. This is a deterministic harness qualification only, not a proof that upstream Gymnasium reset seeds its own global random sampler.

The run is source-pinned separately on Ubuntu and Windows. Scientific work must freeze an experiment-level RNG isolation policy and model/control action budget before using randomized transitions.
