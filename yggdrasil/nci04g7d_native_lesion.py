"""NCI-04G7D: native-owned structural transition observed by an adjacent survivor.

Development-only information boundary. The existing LocalTaskRuntime owns the
lesion and its damaged-state transition. This is actual *structural* evidence,
NOT an observed unknown task function, an independent external sensor, or
proof that the lost function can be recovered. Never use the lost cell's
target output, role weights or a predictor's guess as a learning label.
"""
from dataclasses import dataclass
import hashlib
import pathlib
import subprocess
from .task_runtime import LocalTaskRuntime

SOURCE_FILES = ("yggdrasil/task_runtime.py", "yggdrasil/developmental.py")


@dataclass(frozen=True)
class NeighborLesionEvidence:
    source_commit: str
    source_sha256: tuple
    sender: int
    neighbor: int
    before_neighbor_damaged: int
    after_neighbor_damaged: int
    before_snapshot_sha256: str
    after_snapshot_sha256: str
    sequence: int
    evidence_basis: str = "NATIVE_RUNTIME_OWNED_STRUCTURAL_LESION_NOT_FUNCTIONAL_LABEL"


class NativeNeighborLesionObserver:
    """Opt-in one-event local witness of a genuine LocalTaskRuntime.lesion()."""

    __slots__ = ("runtime", "root", "_emitted")

    def __init__(self, runtime, root):
        if type(runtime) is not LocalTaskRuntime:
            raise TypeError("requires the project-native LocalTaskRuntime")
        self.runtime = runtime
        self.root = pathlib.Path(root).resolve(strict=True)
        self._emitted = False

    def _source_receipt(self):
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.root, check=True,
            capture_output=True, timeout=10).stdout.decode("ascii").strip()
        if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
            raise ValueError("native source commit invalid")
        hashes = []
        for name in SOURCE_FILES:
            file = self.root / name
            if not file.is_file() or file.is_symlink():
                raise ValueError("missing or untrusted native source")
            committed = subprocess.run(
                ["git", "show", commit + ":" + name], cwd=self.root,
                check=True, capture_output=True, timeout=10).stdout
            current = file.read_bytes()
            if current != committed:
                raise ValueError("native transition source changed")
            hashes.append(hashlib.sha256(current).hexdigest())
        return commit, tuple(hashes)

    def intervene_and_measure(self, sender, neighbor):
        """The producer measures native before/after; caller passes no outcome."""
        if self._emitted:
            raise ValueError("native structural-event budget exhausted")
        if (type(sender) is not int or type(neighbor) is not int
                or not 0 <= sender < 8 or not 0 <= neighbor < 8
                or neighbor not in self.runtime.neighbors[sender]
                or sender in self.runtime.damaged
                or neighbor in self.runtime.damaged):
            raise ValueError("only intact sender and adjacent intact target allowed")
        commit, hashes = self._source_receipt()
        before = self.runtime.snapshot()
        own_role_before = tuple(self.runtime.core.roles[sender])
        # Observe only the neighboring target's availability, not its function.
        observed_before = int(neighbor in self.runtime.damaged)
        if observed_before != 0:
            raise ValueError("no intact neighbor to lesion")
        # This native method, not a caller label or another predictor,
        # owns and executes the structural state transition.
        self.runtime.lesion([neighbor])
        after = self.runtime.snapshot()
        observed_after = int(neighbor in self.runtime.damaged)
        if (observed_after != 1 or before == after
                or own_role_before != tuple(self.runtime.core.roles[sender])
                or sender in self.runtime.damaged):
            raise ValueError("native structural transition inconsistency")
        self._emitted = True
        return NeighborLesionEvidence(
            source_commit=commit, source_sha256=hashes, sender=sender,
            neighbor=neighbor, before_neighbor_damaged=observed_before,
            after_neighbor_damaged=observed_after,
            before_snapshot_sha256=hashlib.sha256(before.encode()).hexdigest(),
            after_snapshot_sha256=hashlib.sha256(after.encode()).hexdigest(),
            sequence=1)
