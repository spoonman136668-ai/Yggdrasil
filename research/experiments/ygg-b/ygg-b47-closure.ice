YGG-B47 CLOSURE
Run 36285541091 SHA cbd1ff9ecbf523d74ee64154c3270e50f00d4a67
Classification: GENERAL_EXTRA_WRITE_COLLATERAL
Valid: true. Duplicate SHA256 023465d10ada4a05ba2b9454463efffc65ab6629226f43f67fc7c9f0d2cf3272.
Inherited target/control target-query anchors reproduced exactly.
Target refresh:
- collateral NEW_ERROR 3724
- collateral REPAIR 2009
Control refresh:
- collateral NEW_ERROR 2862
- collateral REPAIR 1819
Both transformed arms used exactly one added write under the same fixed 32-scalar state and 120-parameter model.
Interpretation: collateral redistribution is not specific to targeted correction; an unrelated extra write also perturbs other stored bindings. Targeted refresh causes more collateral new errors in aggregate but uniquely rescues the requested old binding.
Plain speak: the memory system pays a price whenever you add another write. The targeted rewrite is special because it fixes what you asked for, not because it avoids collateral damage.
Next: exhaustively sweep which of the seven existing bindings is rewritten for each old query, measuring target rescue and collateral counts under the same fixed capacity.
