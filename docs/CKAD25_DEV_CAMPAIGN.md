# CKAD25 — executable developer-only cumulative learner custody

On the existing isolated CKAD24 branch, this invokes native Yggdrasil code
to perform two sequential causal training stages on the same native learner.
Each stage is bounded by exact source/tree, packet SHA256, 60-second limit,
no prior replay and no original scientific first-use. All training evidence is
the already-consumed 3-bit 16-row test fixture.

Eight observations in stage one, four previously unseen observations in stage
two, then four held inputs used for read-only evaluation. Each stage writes
a canonical native checkpoint plus source packet and cumulative receipt.
A separate verifier cold restores the persisted states and reproduces held
scores; provenance and deterministic chain SHA256 survive run-local timing
variation. It reports absolute correct/answered and frozen trivial 0/1
controls, not a claim of intelligence or strong matched baselines.

The command is `python -B -m yggdrasil.native_ckad_dev_campaign --output-directory
<new-directory>`. To verify retained artifacts: same command with
`--verify-existing`. Output directories must not already exist.
The runner does not dispatch another worker, schedule itself, operate FORGE,
contact any external source, promote models, or use paid APIs.

For official autonomous training, FORGE still needs an authenticated stage
permit through its original SingleOwner, independently held checkpoint head,
real outcome/compute receipts, and Yggdrasil-authorized frozen scientific
comparators; synthetic fixture qualification grants none of those privileges.
