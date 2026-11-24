# UJ-01C: grounded training and scoring interface (DEV)

The corpus interface verifies a caller-supplied SHA-256 before parsing UTF-8
JSONL, requires train/validation/test partitions and rejects cross-split group
or exact-context reuse. It does not prove semantic decontamination; source-family
splits and near-duplicate audits are still mandatory. No real corpus is included
or accessed. A row carries id, group, domain, split, context, options, answer.
Training pairs expose only train positives; evaluation passes only context and
the same candidate options to every scorer. Report expected tie accuracy and
half the multiclass Brier sum (range 0..1) per domain and overall. JEPA can rank
observable alternatives using its conditional latent density. That is a
multiple-choice outcome test, not proof of open-ended generation or reasoning.

Before a confirmatory run, pin licensed language and math data and hashes,
group-disjoint and near-duplicate audits, shared candidate construction and
answer-position balance, trained controls, seeds, compute caps, stopping rules,
checkpoint and cold retention protocol, and evaluation source. Freeze using
the repository experiment template, not a placeholder preregistration.
The proposed +5pp accuracy, <=2pp retention loss, <=0.020 Brier deterioration,
positive transfer and independent reproduction remain unexecuted. No protected
first-use, runner dispatch, official workflow or accepted model modification.

DEV tests: python -m unittest discover -s research/contrib/ujepa/uj-01 -p 'test_grounded_eval.py' -v
