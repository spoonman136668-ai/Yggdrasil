# WSP-17: persistent numerical program bank

This tests storage and reuse of independently acquired, potentially imperfect NAND computations. Four separately stored75-synapse graphs, four3-bit routing keys and four occupancy synapses cost316 binary scalars. Keys are supplied task context; they are not discovered task identities. Numeric equality and first-free gates perform selection and masked writes. No candidate task dictionary is used. Generic Python simulates the network and serializes checkpoints.

All32 frozen operations are included, even those whose WSP15/WSP16 acquisition failed. Sequential retention, cold restore, localized key1 repair and rejection of a fifth task must preserve the other stored programs. Keeping an imperfect computation is retention, not correcting its errors. There is an explicit fourfold graph-capacity increase relative to the single-slot interference control. Exact symbolic storage receives the same imperfect outputs and is expected to tie. The fully trained control receives the identical actual observations.

Remote preregistration `c5d23f3ae3e44f9bd7cb7d18d15d0cc0c517398f` preceded implementation and first primary WSP17 evaluation. The frozen parent WSP16 source is `16568dca58437ad72b67bea8b8b38eaf000c4639`; WSP16 science remains negative. The parent evidence files preserve WSP15 dual-platform receipts and WSP16's first complete local result, without changing either predecessor source or protocol.

Run `python -m unittest discover -s research/contrib/chatgpt/WSP-17 -p 'test_*.py' -v`, then `python research/contrib/chatgpt/WSP-17/run_dev.py`.

Final qualification requires all original+WSP01-17 unit tests, frozen WSP17 DEV, permanent G29 atlas and clean source on hosted Windows2022 and Ubuntu at one exact candidate. Prior predecessor DEV may be reused only for byte-identical blobs and inputs. No merge, accepted-state change, controller/owner/queue/scheduler change, private runner, paid API, integration or protected first-use.
