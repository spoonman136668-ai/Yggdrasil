# UJ-01G — data and comparison development

HellaSwag upstream repository access returned HTTP 451 with a DMCA restriction.
Exclude that source; do not seek a mirror. AQuA source commit
26b64ed1f22208c6742f47df547dfd65088ec30d, train.json Git blob
a805bddefde8d70fdb66ff7ab85a1999bdc3eece, 47570935 bytes; Apache 2.0
license file d7e363d0c7bf685f52c5a172d54aca328ca55d90.
The raw-file acquisition attempt was blocked in this environment. No data
bytes or SHA-256 acquired. Public test examples surfaced in search metadata;
do not use the official AQuA test as a pristine first-use partition.

OpenBookQA is a proposed replacement language/science question-answering
source, not a sentence-continuation benchmark. Its code repository commit
b51971646e9371a61508d9953fc706645e194a71 has Apache 2.0 license file
261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64. Actual data distribution license,
revision and byte digests remain unverified. Do not download its old embeddings
or execute upstream setup scripts. The native owner must approve actual sources,
seal unseen evaluation cohorts, audit near-duplicates, and freeze split hashes.

Converters enforce exact source SHA-256, drop rationale/oracle facts from model
records, retain choice ordering, report length exclusions (no truncation), and
derive normalized-question group IDs. They do not prove semantic isolation.
Recurrent and attention comparison models use the same raw positive pairs as
JEPA, with in-batch contrastive objectives; distinct answers can still be
semantic false negatives. Parameter counts are near matched, not FLOP matched.
No actual data training, symbolic solver qualification, cold retention or full
native qualification. No accepted model or controller changes.
