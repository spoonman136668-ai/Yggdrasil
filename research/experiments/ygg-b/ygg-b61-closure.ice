YGG-B61 CLOSURE
Run 36334960750 SHA 8bb7c47ea4251cbeac18394d92ee2233be31bd8e
Classification: HELDOUT_MARGIN_GATE_REPLICATES
Valid: true. Duplicate SHA256 2310b34d41cfc4c56f52edc32e1b1df37315def838655f198f7f9cda0bf857f5.
Held-out seeds [666,777,888,999,1111], disjoint from B60 calibration seeds.
Frozen B60 gate T=2.6009554862976074, no refitting.
Held-out:
failure transitions=300; survival transitions=979.
AUROC=0.9606945863.
TP263 TN884 FP95 FN37.
Sensitivity=0.8766666667.
Specificity=0.9029622063.
Balanced accuracy=0.8898144365.
Interpretation: the native pre-failure top1-top2 margin warning generalizes to unseen seeds. It is not a perfect separator, but the preregistered threshold clears all held-out replication criteria.
Plain speak: before the memory visibly breaks, its own confidence usually warns us—and the warning held up on new runs.
Next: on new seeds, freeze a one-intervention policy: at the first pre-write state where margin<=T while target is still capable, apply exactly one target refresh before that competing write. Compare against a no-intervention clone of the same trajectory and record prevented imminent failures, false interventions, horizon change, and collateral.
