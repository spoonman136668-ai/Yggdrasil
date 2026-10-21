"""MR8: atomic same-epoch native neighbor observation and label-free repair.

A small opt-in integration adapter. The original MR7 *consecutive* packet
failure remains immutable. This adapter obtains two real G7A native-world
sender measurements from independent copies of ONE verified pre-transition
runtime, so both original G5 packets legitimately bind the same snapshot.

No target-function answer is supplied. No source-authentication guard, model
parameter, packet format, genome size or existing learner is weakened.
Internally generated G7A world events are NOT externally attested sensors.
"""
import hashlib
import time

from .task_runtime import LocalTaskRuntime
from .nci04g7a_environment_adapter import BoundedLocalEnvironment
from .nci04g5_local_residual import LocalResidualAdapter
from .nci04h_local_repair import LocalCausalRepair
from .developmental import N, K, valid


class NativeAtomicPairRepair:
    __slots__ = ("root", "runtime")

    def __init__(self, root, runtime):
        if type(runtime) is not LocalTaskRuntime:
            raise TypeError("exact existing native runtime required")
        self.root = root
        self.runtime = runtime

    def observe_and_repair(self, bits, action, cell, sequence):
        rt = self.runtime
        valid(bits)
        if (type(cell) is not int or not 0 <= cell < N or
            cell not in rt.damaged or type(action) is not int or
            action not in (0, 1) or type(sequence) is not int or
            not 0 <= sequence <= 65535):
            raise ValueError("invalid local causal observation envelope")
        senders = rt.neighbors[cell]
        if (len(senders) != 2 or senders[0] == senders[1] or
            any(i in rt.damaged for i in senders)):
            raise ValueError("two distinct intact immediate neighbors required")

        source = rt.snapshot()
        base = LocalTaskRuntime.restore(source)
        packets = []
        forks = []
        source_identity = None
        wall_start = time.perf_counter_ns()
        cpu_start = time.process_time_ns()
        # Each G7A world process and ORIGINAL sender-update logic executes
        # separately against the SAME pre-epoch snapshot. This is NOT
        # reusing sequential S0 -> S1 -> S2 packets from MR7.
        for sender in senders:
            fork = LocalTaskRuntime.restore(source)
            packet, proof = BoundedLocalEnvironment(self.root, fork).observe(
                bits, action, cell, sender, sequence
            )
            witness = proof["producer"]
            if (witness["external_sensor_attestation"] is not False or
                proof["postlesion_damaged_target_labels"] != 0 or
                proof["wire_bytes"] != 38 or
                proof["observed_world"] != "DETERMINISTIC_SIMULATED_CAUSAL_TRANSITION"):
                raise ValueError("world consequence provenance not admissible")
            identity = (witness["source_commit"], witness["environment_sha256"])
            if source_identity is None:
                source_identity = identity
            elif source_identity != identity:
                raise ValueError("two native world observations differ in source identity")

            # The unmodified G6 update must alter ONLY its own intact
            # sender role and one event counter, not the damaged target,
            # topology, shared genome or any other cell.
            if (fork.neighbors != base.neighbors or
                fork.damaged != base.damaged or
                fork.steps != base.steps or
                fork.core.genome != base.core.genome or
                fork.core.events != base.core.events + 1 or
                any(fork.core.roles[i] != base.core.roles[i]
                    for i in range(N) if i != sender)):
                raise ValueError("isolated native sender mutated foreign state")
            evidence = LocalResidualAdapter(base).verify(packet, source)
            if (evidence["sender"] != sender or
                evidence["recipient"] != cell or
                evidence["sequence"] != sequence or
                evidence["own_next_bit"] != proof["measured_sender_next_bit"]):
                raise ValueError("original same-epoch wire evidence mismatch")
            packets.append(packet)
            forks.append(fork)

        # A live concurrent or unrelated state mutation fails closed.
        if rt.snapshot() != source:
            raise ValueError("live native source changed during atomic observation")

        # Run the original H learner on a disposable exact-state successor.
        # Contradictory/nonidentifiable signals abstain without any commit.
        fused = LocalTaskRuntime.restore(source)
        local_prior = (bits[cell], bits[senders[0]], bits[senders[1]])
        result = LocalCausalRepair(fused).observe_and_recover(
            cell, local_prior, packets, source
        )
        if result["abstained"] or not result["changed"]:
            if rt.snapshot() != source:
                raise ValueError("native live source drift on abstention")
            return {
                "classification": "ATOMIC_NATIVE_PAIR_ABSTAINED",
                "changed": False, "reason": result["reason"],
                "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                "original_wire_bytes": 76,
                "external_sensor_attested": False,
                "scientific_first_use": False,
            }
        if result["wire_bytes"] != 76:
            raise ValueError("native message budget changed")

        # Commit each intact sender's OWN native G6 update, formed on the
        # same pre-epoch, after damaged-cell label-free H repair. Never
        # borrow a lost-function parameter, a target label or new capacity.
        for sender, fork in zip(senders, forks):
            fused.core.roles[sender] = list(fork.core.roles[sender])
        fused.core.events = base.core.events + len(senders)
        if (fused.core.genome != base.core.genome or
            fused.neighbors != base.neighbors or
            fused.damaged != base.damaged or
            len(fused.core.genome) * len(fused.core.genome[0]) +
            sum(len(row) for row in fused.core.roles) != 45 or
            any(fused.core.roles[i] != base.core.roles[i]
                for i in range(N) if i not in (*senders, cell))):
            raise ValueError("native atomic proposal exceeded fixed locality/capacity")
        final = fused.snapshot()
        if LocalTaskRuntime.restore(final).snapshot() != final:
            raise ValueError("native atomic snapshot not restorable")
        if rt.snapshot() != source:
            raise ValueError("native live source changed before commit")
        rt.core = fused.core
        rt.steps = fused.steps
        return {
            "classification": "ATOMIC_NATIVE_PAIR_TRANSPORT_INTEGRATION_ONLY",
            "changed": True, "messages": 2, "wire_bytes": 76,
            "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
            "source_commit": source_identity[0],
            "world_sha256": source_identity[1],
            "parent_wall_ns": time.perf_counter_ns() - wall_start,
            "parent_cpu_ns": time.process_time_ns() - cpu_start,
            "external_sensor_attested": False,
            "new_learned_coefficients": 0,
            "scientific_first_use": False,
            "functional_regeneration_proven": False,
            "matched_all_in_process_cpu_rss": "NOT_QUALIFIED",
        }
