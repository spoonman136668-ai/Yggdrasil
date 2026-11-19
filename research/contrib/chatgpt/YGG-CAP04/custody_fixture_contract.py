"""CAP04 v2 mock owner-custody contract: engineering fixture only.

Fail-closed rehearsal for preventing source-entropy reuse. Both audit key and
source entropy in the accompanying unit tests are PUBLIC TOY VALUES; this code
cannot request, mint, fetch, persist, authorize, or expose real source secrets.

The in-memory ledger does not establish durable owner custody, protected
source-key independence, CSPRNG strength, or scientific first-use authority.
"""
from __future__ import annotations

import hashlib
import hmac

SCHEMA = "yggdrasil.cap04.v2-custody-engineering-mock.v1"
ENGINEERING_IDENTITIES = frozenset((
    "cap04-v2-engineering-a", "cap04-v2-engineering-b"))
QUALIFIED_SOURCE_SHA = "5d6a04843c53507b316d94993faafcf08dc04afc"
QUALIFIED_SOURCE_TREE = "571cdb44c17cedb0ef6aa35bac9c0a198ae4760a"
FROZEN_PREREG_BLOB = "1d79e222685ea1a6889bff49e5bf405a9aed9580"


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError("CAP04_CUSTODY_" + reason)


def valid_key(value: object) -> bool:
    # Length is not an entropy-quality measure.
    return type(value) is bytes and len(value) == 32


class FixtureCustodyLedger:
    """Ephemeral test-only duplicate-key detector; NEVER a production ledger.

    All secret-like fixture values are deliberately non-secret. The audit key
    and source key must NEVER be committed as science keys or printed by CI.
    No file or network I/O, and no callable scientific unlock.
    """

    __slots__ = ("_audit_key", "_seen_sources", "_seen_fingerprints")

    def __init__(self, fixture_audit_key: bytes):
        require(valid_key(fixture_audit_key), "AUDIT_KEY_SHAPE")
        self._audit_key = fixture_audit_key
        self._seen_sources: set[str] = set()
        self._seen_fingerprints: list[bytes] = []

    def __repr__(self) -> str:
        return (f"FixtureCustodyLedger(mode=ENGINEERING_MOCK_ONLY,"
                f"count={len(self._seen_sources)})")

    def reserve_fixture(
        self,
        source_id: str,
        fixture_entropy: bytes,
        *,
        source_sha: str,
        source_tree: str,
        prereg_blob: str,
    ) -> dict:
        require(type(source_id) is str and
                source_id in ENGINEERING_IDENTITIES,
                "REGISTERED_FIRST_USE_FORBIDDEN")
        require(valid_key(fixture_entropy), "SOURCE_KEY_SHAPE")
        require(source_sha == QUALIFIED_SOURCE_SHA and
                source_tree == QUALIFIED_SOURCE_TREE and
                prereg_blob == FROZEN_PREREG_BLOB,
                "UNQUALIFIED_SOURCE_REFS")
        require(source_id not in self._seen_sources, "SOURCE_REUSE")

        # An audit-keyed, domain-separated private fingerprint can detect
        # identical source entropy even when v2 source IDs are distinct. This
        # fingerprint is NEVER emitted in a receipt or logged by this module.
        fingerprint = hmac.new(
            self._audit_key,
            b"YGG-CAP04/v2/fixture-custody-reuse\x00" + fixture_entropy,
            hashlib.sha256,
        ).digest()
        require(not any(hmac.compare_digest(fingerprint, previous)
                        for previous in self._seen_fingerprints),
                "ENTROPY_REUSE")
        self._seen_sources.add(source_id)
        self._seen_fingerprints.append(fingerprint)

        # No real owner status, CSPRNG attestation or first-use token is issued.
        return {
            "schema": SCHEMA,
            "classification": "ENGINEERING_MOCK_ONLY",
            "source_id": source_id,
            "source_sha": QUALIFIED_SOURCE_SHA,
            "source_tree": QUALIFIED_SOURCE_TREE,
            "prereg_blob": FROZEN_PREREG_BLOB,
            "mock_sources_seen": len(self._seen_sources),
            "source_entropy_quality": "UNVERIFIED",
            "protected_key_custody": "UNVERIFIED",
            "durable_uniqueness": "UNVERIFIED",
            "owner_approval": "UNVERIFIED",
            "registered_first_use": "LOCKED",
            "scientific_efficacy": "UNVERIFIED",
        }

    @staticmethod
    def authorize_registered_first_use(_receipt: object) -> None:
        raise ValueError("CAP04_CUSTODY_REGISTERED_FIRST_USE_FORBIDDEN")
