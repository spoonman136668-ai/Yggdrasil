YGG-B35 CLOSURE
Run 36257434829 SHA 7f1ccdff0309d103e22ad42a9b6c13c361fb6ec3
Classification: ALTERNATE_DESTINATION_PORTABLE
Valid: true. Duplicate SHA256 0da1805f3cbe05eef74025c2c187a2f26200a15428428a698c2ffa1c5a5d001a.
Frozen seeds [111,222,333,444,555], query position 4, threshold 0.90, 120 parameters, 32 persistent-state scalars.
Portable capability counts: destination2=0/5; destination3=5/5; destination4=5/5.
5<->3 B34 anchor reproduced exactly in all five seeds. 5<->4 also crossed threshold in all five seeds and exceeded 5<->3 accuracy in every seed. 5<->2 crossed threshold in none. Exact binding multiset preserved in every arm; duplicate execution byte-identical.
Interpretation: the rescue is not unique to destination 3. Under the frozen seeds it occupies at least a local positional window including destinations 3 and 4, while destination 2 is outside that portable window.
Plain speak: moving the same memory item to either position 3 or 4 reliably rescues memory, but moving it farther back to position 2 does not. The useful effect looks like a positional zone, not one magic slot.
Next: test whether rescue reappears at still-earlier destinations 0 or 1, using destination2 as the frozen negative anchor and destination3 as the frozen positive anchor.
