"""Read-only checkpoint scan for an immutable upstream TD-MPC2 .pt ZIP.

NEVER unpickles, loads torch, constructs models or interprets pickle opcodes.
Every result is metadata/custody-only, not extracted model weights or science.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import pickletools
import re
import sys
import zipfile

SCHEMA = "yggdrasil.dwsa31.static-torch-checkpoint-scan.v1"
EXPECTED_SHA256 = "40c3eac2ac86d73c5931536dcf6d65b341f17524d5be74ca97d6e4d9d0f9c56e"
EXPECTED_SIZE = 7_956_767
EXPECTED_SOURCE = "nicklashansen/tdmpc2@0d1dfdda7e529f6d3f942787ce2825eccad38935:multitask/mt30-1M.pt"
MAX_ARCHIVE = 16 * 1024 * 1024
MAX_MEMBERS = 10000
MAX_ENTRY = 16 * 1024 * 1024
MAX_UNCOMPRESSED = 64 * 1024 * 1024
MAX_PICKLE = 8 * 1024 * 1024
MAX_OPCODES = 1_000_000


class UnsafeOrUnverified(ValueError):
    """No checkpoint interpretation is permitted on failed custody/format checks."""


def _sha256_bytes(path: Path) -> tuple[bytes, str]:
    if not path.is_file() or not 0 < path.stat().st_size <= MAX_ARCHIVE:
        raise UnsafeOrUnverified("DWSA31_SIZE_LIMIT")
    raw = path.read_bytes()
    return raw, hashlib.sha256(raw).hexdigest()


def _find_data_pickle(names: list[str]) -> str:
    candidates = [n for n in names if n.endswith("/data.pkl") and n.count("/") == 1]
    if len(candidates) != 1:
        raise UnsafeOrUnverified("DWSA31_PICKLE_MEMBER_MISSING_OR_AMBIGUOUS")
    return candidates[0]


def scan(path: Path, *, expected_sha256: str = EXPECTED_SHA256,
         expected_size: int = EXPECTED_SIZE) -> dict[str, object]:
    """Verify an EXACT pinned byte sequence and statically list its pickle globals.

    Scanning opcodes is NOT unpickling: REDUCE/BUILD/PERSID are just strings
    here; no callable dispatch, no Python class reconstruction, no storage map.
    """
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise UnsafeOrUnverified("DWSA31_INVALID_EXPECTED_HASH")
    if not 0 < expected_size <= MAX_ARCHIVE:
        raise UnsafeOrUnverified("DWSA31_INVALID_EXPECTED_SIZE")
    raw, actual = _sha256_bytes(path)
    if actual != expected_sha256 or len(raw) != expected_size:
        raise UnsafeOrUnverified("DWSA31_SOURCE_BYTE_IDENTITY_MISMATCH")

    try:
        with zipfile.ZipFile(io.BytesIO(raw), "r") as zf:
            infos = zf.infolist()
            if not 2 <= len(infos) <= MAX_MEMBERS:
                raise UnsafeOrUnverified("DWSA31_MEMBER_COUNT")
            names = [x.filename for x in infos]
            if len(names) != len(set(names)):
                raise UnsafeOrUnverified("DWSA31_DUPLICATE_MEMBER")
            if any(x.flag_bits & 1 or x.compress_type != zipfile.ZIP_STORED or
                   x.file_size > MAX_ENTRY or x.file_size < 0 or
                   x.filename.startswith("/") or "\\" in x.filename or
                   any(part in ("", ".", "..") for part in x.filename.split("/"))
                   for x in infos):
                raise UnsafeOrUnverified("DWSA31_UNSAFE_ZIP_MEMBER")
            if sum(x.file_size for x in infos) > MAX_UNCOMPRESSED:
                raise UnsafeOrUnverified("DWSA31_UNCOMPRESSED_LIMIT")
            member = _find_data_pickle(names)
            if zf.getinfo(member).file_size > MAX_PICKLE:
                raise UnsafeOrUnverified("DWSA31_PICKLE_TOO_LARGE")
            pickle_data = zf.read(member)
            globals_seen: set[str] = set()
            opcode_count = 0
            last_position = -1
            terminal_stop = False
            for op, arg, pos in pickletools.genops(pickle_data):
                opcode_count += 1
                if opcode_count > MAX_OPCODES:
                    raise UnsafeOrUnverified("DWSA31_PICKLE_OP_LIMIT")
                last_position = pos
                if op.name == "GLOBAL":
                    globals_seen.add(str(arg).replace(" ", ".", 1))
                elif op.name in ("EXT1", "EXT2", "EXT4", "PERSID"):
                    # Arbitrary registered-extension references cannot be
                    # mechanically screened as text and are not required.
                    raise UnsafeOrUnverified("DWSA31_OPAQUE_EXTENSION_OR_PERSISTENT_ID")
                elif op.name == "STOP":
                    terminal_stop = True
            if not terminal_stop or not opcode_count:
                raise UnsafeOrUnverified("DWSA31_PICKLE_NO_STOP")
            # Reject invisible trailing material instead of ignoring it.
            if last_position != len(pickle_data) - 1:
                raise UnsafeOrUnverified("DWSA31_PICKLE_TRAILING_DATA")
            # STACK_GLOBAL is reported as an unresolved risk rather than
            # executing a stack interpreter to resolve its runtime operands.
            stack_globals = sum(op.name == "STACK_GLOBAL"
                                for op, _, _ in pickletools.genops(pickle_data))
            storages = [x for x in infos if re.fullmatch(r"[^/]+/data/[0-9]+", x.filename)]
            return {
                "schema": SCHEMA,
                "original_source": EXPECTED_SOURCE,
                "verified_full_file_sha256": actual,
                "file_bytes": len(raw),
                "zip_members": len(infos),
                "raw_storage_member_count": len(storages),
                "raw_storage_bytes": sum(x.file_size for x in storages),
                "data_pickle_sha256": hashlib.sha256(pickle_data).hexdigest(),
                "pickle_opcode_count": opcode_count,
                "static_global_references": sorted(globals_seen),
                "unresolved_stack_global_count": stack_globals,
                "status": "ORIGINAL_BYTES_AUTHENTIC_STATIC_ONLY",
                "deserialization_executed": False,
                "teacher_forward_calls": 0,
                "environment_actions": 0,
                "weights_extracted": False,
                "scientific_gain_verified": False,
                "native_integration_authorized": False,
            }
    except (zipfile.BadZipFile, zipfile.LargeZipFile, EOFError, ValueError, OSError,
            IndexError, TypeError, UnicodeError) as e:
        if isinstance(e, UnsafeOrUnverified):
            raise
        raise UnsafeOrUnverified("DWSA31_ARCHIVE_OR_PICKLE_INVALID") from e


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    args = parser.parse_args(argv)
    try:
        result = scan(args.checkpoint)
    except (UnsafeOrUnverified, OSError) as e:
        print("DWSA31_FAIL_CLOSED:" + str(e), file=sys.stderr)
        return 3
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
