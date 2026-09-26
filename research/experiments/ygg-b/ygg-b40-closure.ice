YGG-B40 CLOSURE
Run 36270587677 SHA 86bb740de5a65ee9dc278618b10c72a54d6053af
Classification: DESTINATION4_ONLY
Valid: true. Duplicate SHA256 b3deb3623ae03b76fc5d4977add500044c934477979d24b0771aef954da8c54b.
Frozen seeds [111,222,333,444,555], source6, query position4, threshold 0.90.
6<->4 reproduced accuracy 1.0 in all five seeds. 6<->5 capability was 0/5 with accuracies 0.8564013839, 0.8388158083, 0.8495867848, 0.8419243693, 0.8571428657.
Exact binding multiset preserved every arm; duplicate execution byte-identical.
Interpretation: source6 portable rescue is bounded to destination4 across tested destinations0..5. Because destination4 is also the queried first-read event position in this stratum, absolute-position and query-relative explanations remain confounded.
Plain speak: moving the last item to slot4 fixes every seed, but moving it to the neighboring slot5 fixes none. The important next question is whether slot4 itself is special or whether rescue happens whenever that item is moved into whichever slot is being queried.
Next: query-relative source6 alignment test across frozen query-position strata.
