YGG-A56 CLOSURE
Run 36316830109 SHA 6acb8fddb9c678b9c96b1e8e6f060adcbf109bfc
Classification: DISTRIBUTED_STREAM_SENSITIVITY
Valid: true. Duplicate SHA256 7bd3cfa461754d9eb1a9ffc25dc0f8de9b2199c2c9b6102593cefc11a1a052f2.
Native replicate6 phase3 collapse reproduced in both U_A0 and U_A25.
Of the 32 exact single stream-label flips over requests96..127, 24 abolished collapse:
96,97,98,99,100,101,102,104,107,108,109,110,112,113,114,115,116,118,119,120,122,124,126,127.
Eight single flips retained collapse:
103,105,106,111,117,121,123,125.
The sensitive sets were identical across modes. Known A55/A52 positions97,116,118,119,120 reproduced as sensitive.
Interpretation: collapse depends on a broadly distributed exact phase3 stream schedule. Sensitivity is not localized to the immediate 118..120 neighborhood and is not reducible to stream identity alone; seven insensitive positions are native-S and one (106) is native-C.
Plain speak: most individual changes anywhere in phase3 are enough to prevent the failure. Only eight positions can be changed one at a time without effect.
Next: exhaustively flip every pair among those eight individually tolerant positions. This tests whether they are truly irrelevant or whether their effects are redundant/higher-order and only appear in combination.
