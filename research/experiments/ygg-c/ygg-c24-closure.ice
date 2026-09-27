YGG-C24 CLOSURE
Run 36304396514 SHA 6aa808496c2f37fe178c4def8a3b4609ebbb3388
Classification: BOTH_FACTORS_INDEPENDENTLY_SUFFICIENT
Valid: true. Duplicate SHA256 da83901b7600f5d645aecd4f049cca4fa482984995d4d206fad09f20ae18057e.
At every level8..16:
- FULL_PARTNER6 rescued.
- remove cell2 only failed.
- neutral remove cell10 only rescued.
- add cell6 only failed.
- neutral add cell14 only rescued.
- inherited replace2->6 failed.
- inherited replace10->14 rescued.
Cardinality controls and all corrected-runtime anchors reproduced.
Interpretation: partner6 cell2 is independently necessary for the rescued basin, and exclusion of replicate8 cell6 is independently necessary. The effect is not generic lesion cardinality.
Plain speak: the repair needs cell2 to stay in and cell6 to stay out. Either mistake alone breaks recovery.
Next: test the symmetric repair direction from the original failing replicate8 lesion: add cell2 only and remove cell6 only, with matched add10/remove14 controls, to see whether either factor is sufficient to repair rather than merely necessary to preserve an already-rescued state.
