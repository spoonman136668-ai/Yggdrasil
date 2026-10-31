# MG94-O equal-capacity control gate

Source commit: c6dcc67a50e4340bed029f777cf140f4a87f7e33
Classification: SYNTHETIC DEVELOPMENT ONLY

Implemented conventional comparator policies: retain first four binary observations, retain most recent four, and seeded four-slot reservoir sampling (seed 1904). All three hold at most four binary observations. Scenario streams: stable, reversed, recurring (24 observations each). Predictions are prequential; abstentions count as incorrect. No oracle, rewards or hidden state.

STATUS: Implementation committed. Exact-head focused execution UNVERIFIED. Comparative result UNVERIFIED. This is not a native distributed-memory candidate; it does not test recurrent or learned selective retention. Full regression and original-world scientific qualification NOT EXECUTED. No acceptance, promotion or experiment dispatch.
