"""Source-free CVH10 public DTR -> *candidate-only* native-shape episode.

No import of a third-party environment, no source constructor/reset/do/step,
no source actor, no owner checkpoint, and no native observe() invocation.
The output NEVER authenticates upstream event birth or authorizes training.
See dtr_candidate_episode_freeze.md (preregistered before implementation).
"""
from __future__ import annotations

from dataclasses import dataclass
from yggdrasil.native_context_basis import canonical, digest, pin
from yggdrasil.native_episode_experience import _views

SOURCE_REPO = "CausalAILab/Causal-Gymnasium"
SOURCE_COMMIT = "c94e9a4cd3641588b6b8507e71ccee5c27032bdf"
SOURCE_DTR_BLOB = "6af2371dce21804140ea141ccb7be14e003ba275"
CVH10_BRIDGE_BLOB = "8431fdae76f4fb6579b6e9cb4df598aea9657688"
FIELDS = ("before", "action", "reward", "after", "terminated", "truncated")
ROW_FIELDS = ("s1", "x1", "s2", "x2", "y")
SCHEMA = "yggdrasil.research.dtr-candidate-public-episode.v1"


def _bit(value, label):
    if type(value) is not int or value not in (0, 1):
        raise ValueError("DTR_CANDIDATE_PUBLIC_BIT_" + label)
    return value


def _row(record):
    if not isinstance(record, tuple) or len(record) != 6:
        raise ValueError("DTR_CANDIDATE_SIX_PUBLIC_FIELDS_REQUIRED")
    if hasattr(record, "_fields") and tuple(record._fields) != FIELDS:
        raise ValueError("DTR_CANDIDATE_FIELD_NAMES")
    before, action, reward, after, terminated, truncated = record
    values = tuple(_bit(v, label) for v, label in zip(
        (before, action, reward, after), FIELDS[:4], strict=True))
    if type(terminated) is not bool or type(truncated) is not bool:
        raise ValueError("DTR_CANDIDATE_BOOLEAN_TERMINATION")
    return values + (terminated, truncated)


@dataclass(frozen=True, slots=True)
class PublicDTRCandidate:
    """Immutable data-only *proposal*, never a source-owner witness receipt."""

    identifier: str
    views: tuple[tuple[int, int], tuple[int, int]]
    row_bits: tuple[int, int, int, int, int]
    candidate_packet_sha256: str
    public_transcript_sha256: str
    schema: str = SCHEMA
    source_repo: str = SOURCE_REPO
    source_commit_git_sha1: str = SOURCE_COMMIT
    source_dtr_git_blob_sha1: str = SOURCE_DTR_BLOB
    cvh10_bridge_git_blob_sha1: str = CVH10_BRIDGE_BLOB
    independent_second_view_observed: bool = False
    terminal_after_is_source_observation: bool = False
    original_source_birth_attested: bool = False
    source_firstuse_execution_allowed: bool = False
    native_ingestion_authorized: bool = False
    canonical_model_updates: int = 0

    def __post_init__(self):
        # Prevent ordinary callers/dataclasses.replace from forging an
        # attested or admissible episode out of this untrusted data class.
        # This is a contract check, NOT a Python process security boundary.
        if (self.schema != SCHEMA or self.source_repo != SOURCE_REPO
                or self.source_commit_git_sha1 != SOURCE_COMMIT
                or self.source_dtr_git_blob_sha1 != SOURCE_DTR_BLOB
                or self.cvh10_bridge_git_blob_sha1 != CVH10_BRIDGE_BLOB
                or self.independent_second_view_observed is not False
                or self.terminal_after_is_source_observation is not False
                or self.original_source_birth_attested is not False
                or self.source_firstuse_execution_allowed is not False
                or self.native_ingestion_authorized is not False
                or self.canonical_model_updates != 0):
            raise ValueError("DTR_CANDIDATE_ADMISSION_FORBIDDEN")
        if (not pin(self.identifier) or not pin(self.candidate_packet_sha256)
                or not pin(self.public_transcript_sha256)
                or type(self.row_bits) is not tuple
                or len(self.row_bits) != len(ROW_FIELDS)
                or any(type(bit) is not int or bit not in (0, 1)
                       for bit in self.row_bits)
                or self.views != ((self.row_bits[0], 0),
                                  (self.row_bits[0], 0))):
            raise ValueError("DTR_CANDIDATE_PROVENANCE_OR_VIEW")
        if digest(canonical([
                self.identifier, self.views, self.as_row()
        ])) != self.candidate_packet_sha256:
            raise ValueError("DTR_CANDIDATE_PACKET_DRIFT")

    def as_row(self):
        """Return a NEW detached dictionary, never a stored mutable one."""
        return dict(zip(ROW_FIELDS, self.row_bits, strict=True))

    def public_receipt(self):
        """Clearly labelled unverified candidate, without native source pin."""
        return {
            "schema": self.schema,
            "identifier": self.identifier,
            "public_transcript_sha256": self.public_transcript_sha256,
            "candidate_packet_sha256": self.candidate_packet_sha256,
            "source_repo": self.source_repo,
            "source_git_commit": self.source_commit_git_sha1,
            "source_dtr_git_blob": self.source_dtr_git_blob_sha1,
            "cvh10_bridge_git_blob": self.cvh10_bridge_git_blob_sha1,
            "independent_second_view_observed": False,
            "terminal_after_is_source_observation": False,
            "original_source_birth_attested": False,
            "source_firstuse_execution_allowed": False,
            "native_ingestion_authorized": False,
            "canonical_model_updates": 0,
        }


def candidate_from_public_episode(rows, *, identifier):
    """Map exactly two *already public* CVH10 records to a shape-only candidate.

    First record:  (S1, X1, 0, S2, False, False).
    Second record: (S2, X2, Y, 0, True, False).
    The last 'after=0' is CVH10's terminal absence sentinel, NOT observed S3.
    The second native view duplicates one known public S1 bit and adds no facts.
    Neither the original source SHA nor any owner admission is fabricated.
    """
    if not pin(identifier):
        raise ValueError("DTR_CANDIDATE_OPAQUE_IDENTIFIER")
    if type(rows) not in (tuple, list) or len(rows) != 2:
        raise ValueError("DTR_CANDIDATE_TWO_STAGE_EPISODE_REQUIRED")
    first, second = (_row(value) for value in rows)
    s1, x1, first_reward, s2, first_done, first_trunc = first
    second_before, x2, y, final_after, final_done, final_trunc = second
    if first_reward != 0 or first_done or first_trunc:
        raise ValueError("DTR_CANDIDATE_STAGE0_NONTERMINAL_ZERO_REWARD")
    if second_before != s2:
        raise ValueError("DTR_CANDIDATE_HISTORY_MISMATCH")
    if not final_done or final_trunc:
        raise ValueError("DTR_CANDIDATE_STAGE1_TERMINAL_REQUIRED")
    if final_after != 0:
        raise ValueError("DTR_CANDIDATE_TERMINAL_ABSENCE_SENTINEL")
    # Intentionally degenerate; second view carries NO independently
    # observed second bit. Nothing about source latent confounder U is known.
    views = ((s1, 0), (s1, 0))
    _views(views)  # Validate against the actual unmodified native grammar.
    bits = (s1, x1, s2, x2, y)
    row = dict(zip(ROW_FIELDS, bits, strict=True))
    public_digest = digest(canonical([list(first), list(second)]))
    # This is a hash of a SHAPE-COMPATIBLE CANDIDATE, not owner evidence.
    packet = digest(canonical([identifier, views, row]))
    return PublicDTRCandidate(
        identifier=identifier,
        views=views,
        row_bits=bits,
        candidate_packet_sha256=packet,
        public_transcript_sha256=public_digest,
    )
