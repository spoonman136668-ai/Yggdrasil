# UJ-01E DEV: snapshot and representation diagnostics

Five focused tests executed on exact-source Linux CPU copies. Restore reconstructs
a fresh model from finite float32 JSON weight state, with supplied source/corpus
SHA-256 identities and digest. Both modes preserve predictions bit-exact in
same-process restoration after a weight update. The caller must provide actual
trusted identities and persist bytes; a digest is integrity, not authentication.
No optimizer, RNG or training cursor checkpoint, atomic disk writes, or claim
of cold knowledge retention. Report raw online/target standard deviations and
effective rank; rank ceiling is min(batch size minus one, latent dimension).

The existing variance penalty is 0.19 at exactly collapsed representations and
has zero gradient there. This is an analytic negative fixture, not a measured
scientific outcome on real data. A future isolated comparison should test
independent noncollapsed anchors or other symmetry-breaking anti-collapse
mechanisms with matched information, frozen thresholds and matched controls;
do not silently change the current objective or restart a consumed trial.

Real corpus acquisition, remaining control architectures, complete native
regression, cold-process retention and scientific first-use are outstanding.
No changes outside the contribution lane.
