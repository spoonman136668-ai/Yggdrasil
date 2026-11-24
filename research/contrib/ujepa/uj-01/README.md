# UJ-01: distributional latent prediction (DEV only)

Parent: 5e74f8db85b2f5839c42148c0dfba69a88b1a2c9; tree 180008502f6bdfe5a06c3d0d6f47f941dd01f20b.

This contribution is a narrow trainable conditional density head, not a complete JEPA or a native Yggdrasil learner. A one-component Gaussian head is an initial deterministic-mean control; a two-component head can represent competing futures. Inputs must be continuous bounded latent vectors; no tokenizer, transformer, external API, controller, checkpoint integration or source dataset is included. All parameters are fixed-size and only observed targets update them.

Engineering fixture command from repository root: `python -m unittest discover -s research/contrib/ujepa/uj-01 -p 'test_*.py' -v`. No scientific result is produced. The two-component head has more parameters than the one-component head; this is NOT a capacity-matched comparison.

Before confirmatory science: freeze exact source and dataset manifests (language and math initially), split hashes, learned non-token encoder and target encoder design, capacity/compute-matched trained controls (deterministic and regularized JEPA, recurrent byte-level, transformer and symbolic where applicable), scoring, 5 seeds, compute caps, stop rules, calibration, retention and transfer tasks. Proposed gates from UJ-01: >=5 percentage points improvement over strongest applicable control; retention loss <=2pp; Brier deterioration <=0.020; positive cross-domain transfer and independent reproduction. These are not a frozen preregistration until the missing details and exact identities are recorded in prereg.json using the repository template. No protected first-use authorized by this commit.

Status: development prototype only; not integrated, scientific UNVERIFIED, deployment HOLD. No official control files, workflows or accepted model changes.
