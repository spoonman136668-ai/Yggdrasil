YGG-B33 PREREGISTRATION — COMPOSITION-PRESERVING RECIPROCAL SWAP
Parent: YGG-B32 run 36248716226, valid MULTIPLE_POSITIONS_SUFFICIENT.
Question: do the B32 sufficient destination effects persist when the exact binding multiset is preserved, distinguishing positional order from one-way identity-composition/duplication effects?
Frozen: exact B32/B31 model, training and evaluation generator; seed 222; queried write position 4; inherited threshold 0.90; 120 parameters; 32 persistent state scalars; deterministic Torch; no online adaptation, architecture/capacity/threshold change, or baseline mutation.
Frozen B31 permutation rule: for query position 4, non-query positions are [0,1,2,3,5,6]; shift=1+((222+4)%6)=5; destination mapping is 0<-6, 1<-0, 2<-1, 3<-2, 5<-3, 6<-5.
B32 sufficient one-way destinations: 0,5,6.
Design: reproduce original and full B31-permuted endpoints. Run exactly three reciprocal-swap arms, fixed before outcomes:
  arm D0: swap original binding blocks at positions 0 and 6.
  arm D5: swap original binding blocks at positions 5 and 3.
  arm D6: swap original binding blocks at positions 6 and 5.
Each arm preserves the exact seven-binding multiset and changes only order among the named pair; query position 4 remains untouched.
Classification:
  ORDER_SUFFICIENT_ALL if all three reciprocal arms reach >=0.90;
  ORDER_SUFFICIENT_PARTIAL if one or two reach >=0.90;
  COMPOSITION_EFFECT_REQUIRED if none reaches >=0.90 while inherited full permutation remains >=0.90;
  FULL_EFFECT_NOT_REPRODUCED if inherited full permutation is <0.90;
  OTHER_VALID_PATTERN otherwise.
Validity: inherited mechanical gate; exact seed/query/threshold/state/parameter counts; original endpoint 0.8322368264198303 reproduced; full endpoint 0.90625 reproduced; exactly three fixed reciprocal arms; exact per-row binding multiset preserved in each arm; duplicate complete execution byte-identical.
Scientific negatives are valid. No post-result tuning.
