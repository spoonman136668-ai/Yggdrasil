YGG-B64 CLOSURE
Run 36353597874 SHA 0ae82d154523e71248269ec975394639f44d5c8f
Classification: SIGNAL_TIMING_STRICTLY_BETTER
Valid: true. Duplicate SHA256 477b00187d7b133685acf24c78d6a4d8deab8ddc0937e23591e46c56b5ddaf81.
Fresh seed block [2333,2444,2555,2666,2777],300 trajectories.
Failures by depth6:
CONTROL=300
FIXED_D1=300
FIXED_D2=300
FIXED_D3=287
FIXED_D4=207
FIXED_D5=198
GATED=174
Interventions:
D1=300,D2=300,D3=288,D4=251,D5=130,GATED=272.
Interpretation: the frozen native warning supplies useful timing information. Its one-shot intervention produces fewer failures than every blind fixed-depth one-shot schedule, not merely the no-intervention control.
Plain speak: acting when the system warns works better than refreshing at any fixed time.
Next: compare GATED directly against the strongest blind schedule FIXED_D5 on a new seed block while scoring all seven stored bindings at the end. Isolate intervention-specific collateral by comparing each branch against its matched CONTROL final state.
