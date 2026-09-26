YGG-B38 CLOSURE
Run 36268329756 SHA 74d8729747dd39b4602ca13ae6d58738705c5d58
Classification: MULTISOURCE_DESTINATION4
Valid: true. Duplicate SHA256 b000e4ace56197b1f8ae486b616482e59d9c011d0352018208a3a2923564c8da.
Frozen seeds [111,222,333,444,555], destination4, query position4, threshold 0.90, 120 parameters, 32 persistent-state scalars.
Portable capability counts by reciprocal source into destination4: source0=0/5; source1=0/5; source2=0/5; source5=5/5; source6=5/5.
The frozen 5<->4 B35 anchor reproduced exactly in all five seeds. Source6<->4 reached accuracy 1.0 in all five seeds. Exact binding multiset preserved in every arm; duplicate execution byte-identical.
Interpretation: source5 is not uniquely responsible for destination4 rescue. The rescue window is asymmetric: destination3 is source5-specific under the tested sources, whereas destination4 admits both source5 and source6 as portable rescuing sources.
Plain speak: position 4 behaves differently from position 3. At position 4, either of the two latest memory items can rescue performance; at position 3, only the item from position 5 worked reliably.
Next: test the 6<->4 rescue against destination specificity using fixed destinations 0..3 plus the known positive destination4, to determine whether source6 is intrinsically strong or specifically compatible with destination4.
