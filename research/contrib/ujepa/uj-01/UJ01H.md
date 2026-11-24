# UJ-01H — symbolic control and acquisition disposition

Explicit arithmetic control uses bounded AST interpretation and exact rational
arithmetic; unsupported language, syntax, ambiguous answers or invalid choices
abstain uniformly. Report both coverage and all-row performance, never compare
the solved subset alone. Not an AQuA word-problem solver or strong control for
natural-language reasoning. Its score scale 20 is a development choice and
must be frozen or calibrated on validation only before a primary run.

Data custody: AQuA train.json at 26b64ed1f22208c6742f47df547dfd65088ec30d,
Git blob a805bddefde8d70fdb66ff7ab85a1999bdc3eece, returned zero content bytes
through the connector. Direct raw.githubusercontent.com retrieval failed DNS
in the local Linux sandbox. OpenBookQA source repository script
scripts/download_and_prepare_data.sh at b51971646e9371a61508d9953fc706645e194a71
identifies the official archive, but its payload digest and distribution terms
remain unverified. Do not run that setup script or expose protected labels.
The owner must supply approved train-only source bytes and independently seal
unseen evaluation data. No dataset hash or split identity fabricated.

Execution: direct-research-qualification.yml is restricted to
research/autonomy-yggdrasil-active and an exact two-commit package under
research/applications/plane plus .yggdrasil requests; U-JEPA contribution
branch is not eligible. Runner inventory endpoint rejected. Existing CI
run 45386695612 failed with zero job records; no root cause established.
Do not reuse active branch, mutate workflow, dispatch or replay unrelated work.

No confirmatory preregistration until source terms, hashes, disjointness,
baseline convergence, measured compute budget, cold retention design and
owner first-use authority are established. Full native regression still needed.
No accepted model changes.
