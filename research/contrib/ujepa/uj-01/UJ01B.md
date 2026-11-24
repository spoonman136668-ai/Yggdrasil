# UJ-01B — learned representation development only

Adds an optional PyTorch CPU prototype beside the dependency-free UJ-01 head. Raw
bytes become eight binary signal channels, with a recurrent encoder rather than
token embeddings or attention. The online encoder learns through the prediction
objective; the target is a gradient-free exponential moving average. Variance
pressure is a mitigation, not a guarantee against collapse. The collapsed-state
diagnostic is mandatory before any future scored run.

Mixture and pooled Gaussian modes share identical architecture and trainable
parameter counts, initial weights when copied, context/target data and regularizer.
Both use proper likelihood in the common latent coordinate system within each
model. Raw latent NLL across separately learned representations is not a sufficient
science metric; evaluate both against identical externally grounded outcomes.
Compute parity, trained recurrent/transformer/symbolic controls, real data, seed
schedule, cold retention and transfer are still missing. No first-use or native
model integration authorized.

Focused engineering command (requires existing PyTorch installation):
python -m unittest discover -s research/contrib/ujepa/uj-01 -p 'test_*.py' -v

No dependency installation, official workflow, accepted ref or checkpoint change.
No scientific result. Parent 8afd576ffb6818cfc5f6e2aabd8e14ed44707ec9.
