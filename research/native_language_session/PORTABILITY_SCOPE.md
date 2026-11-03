# Fanout portability repair scope

Engineering-only continuation of the native-session draft, frozen before repair.

Parent: 47975c04280db80f2bdb360099168c3d2a5b8c48
Original sidecar blob: 8e6e6172208539f961c072278c28156e534214c0
Original test blob: ff16dfb224a22e0b6241efd3bc5dbbba613b0ef0
Existing execution workflow blob: 5db0347302ef56ee1460bbdcbf50208c5fc6afaa

Observed failure: the Windows public regression cannot import the fanout module because Python's resource module is unavailable. The existing manual read-only fanout workflow executes on Ubuntu only.

Allow portable manifest/result validation and aggregation to import without resource. Reject run_candidate before filesystem creation or subprocess launch if resource accounting is unavailable. Do not fabricate measurements or add a Windows execution backend. Preserve existing Linux execution, limits, environment, workflow and authority.

The two real-subprocess worker tests remain required on the supported resource-accounting platform. On Windows report them explicitly UNSUPPORTED/skipped, and separately require the fail-closed nonexecution and portable-import tests. Run the complete public regression on both platforms and the native-session tests; report platform coverage separately. This does not qualify Windows fanout execution.

Original R7 learner, fixtures, controls, seeds, retention threshold, result and scientific gate remain unchanged. Overall scientific acceptance remains blocked by the original negative. Do not change Wingless, any accepted main, FORGE live owner, scientific authority, controller, queue or runtime activation.

Refresh the advisory Atlas from exact source, preserve clean-source validation and G29 acceptance, and record immutable qualification refs in the existing draft.
