# UJ-01F — DEV input-derived anchors

Adds an explicit objective adapter, with aligned anchors, cyclic-misaligned
sham and zero-weight controls. Anchors are deterministic position-bin bit means
from the same observable context/future strings, no extra training observations,
labels, trainable parameters or learned vocabulary. The same extra encoder
passes are present in all three arms; actual compute parity is unmeasured.
The first 8 anchor coordinates encode only two low-order bit channels; this
may lose many distinctions. Anchors can collide and are not semantic targets.

At exact output collapse, the existing variance penalty has zero gradient.
Aligned anchor loss has a nonzero output gradient on the fabricated diverse
fixture, and a zero-initialized linear projection over informative fixed
features recovers nonzero dispersion after one SGD update. This does not
establish recovery of a fully collapsed recurrent encoder, sustained learning,
or improvement over sham on real tasks. The existing learned JEPA objective
and training harness are unchanged; adapter wiring to a full run is pending.
Compare with anchor-only and shuffled controls, report grounding accuracy,
raw rank and variance; never count variance alone as learned knowledge.

No corpus accessed, no protected run, no native acceptance or deployment.
