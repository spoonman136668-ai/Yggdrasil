YGG-A45 CLOSURE
Run 36283969522 SHA 974e5799489fe347f59950aa3c849250ea342dbc
Classification: MIXED_PHASE_PAIR_SENSITIVITY
Valid: true. Duplicate SHA256 dc3c192e26e4e5c82094a8c96f9416ca9a617a2c8c1d788c1c4401bd6207183f.
Donor3 base corruption schedule: [16,38,105,113,118,146], with per-phase counts [1,1,0,3,1].
Both U_A0 and U_A25 produced the identical phase-pair result:
- swaps retaining collapse: [0,1],[0,2],[0,4],[1,2],[1,4],[2,4]
- swaps abolishing collapse: [0,3],[1,3],[2,3],[3,4]
Therefore every swap involving phase3 abolishes collapse, while every pair swap leaving phase3 untouched retains collapse.
All ten preregistered swaps, count preservation, within-pair offset preservation, inherited anchors, scientific integrity, duplicate execution and runtime restoration passed.
Interpretation: the donor3 collapse is specifically localized to the phase3 placement of its corruption pattern.
Plain speak: phase3 is the critical developmental window. Move that phase's corruption pattern anywhere else and the cell2 failure disappears; shuffle other phase blocks and it stays.
Next: hold all per-phase corruption counts fixed and circularly shift only the three phase3 corruption offsets within phase3 to test whether exact within-phase timing matters.
