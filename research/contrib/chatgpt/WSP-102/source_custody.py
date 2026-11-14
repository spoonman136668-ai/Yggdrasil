"""WSP-102: Wikidata5M immutable-archive provenance preflight, NO DATA TRAINING.

Purposefully does not parse or reveal graph records. Logs only archive hash,
member names and byte lengths to seal source before any later scientific use.
No extraction, model fit, test-set read, paid APIs or persistent download.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tarfile
import tempfile
import time
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

SOURCE_URL = "https://web.informatik.uni-mannheim.de/pi1/kge-datasets/wikidata5m.tar.gz"
SOURCE_HOST = "web.informatik.uni-mannheim.de"
MAX_COMPRESSED = 268435456
MAX_TOTAL_UNCOMPRESSED = 1800000000
MAX_MEMBER_UNCOMPRESSED = 1200000000
MAX_MEMBERS = 256
MAX_SECONDS = 600
SCHEMA = "wsp102.wikidata5m.source-custody.v1"


def _check_url(url: str):
    p = urlsplit(url)
    if (p.scheme != "https" or p.hostname != SOURCE_HOST
            or p.username is not None or p.password is not None
            or p.query or p.fragment or not p.path.startswith("/pi1/kge-datasets/")
            or p.port not in (None, 443)):
        raise ValueError("non-allowlisted external source URL")
    return url


class _SourceRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        _check_url(newurl)
        return super().redirect_request(request, fp, code, msg, headers, newurl)


def inspect_members(path):
    """No tar extraction and no entity/triple row reads."""
    parts = []
    total = 0
    found = set()
    with tarfile.open(path, mode="r:gz") as archive:
        for member in archive:
            if len(parts) >= MAX_MEMBERS:
                raise ValueError("archive member count limit exceeded")
            name = member.name
            parsed = PurePosixPath(name)
            if (not name or len(name) > 256 or name.startswith("/")
                or chr(92) in name or "//" in name or "\x00" in name
                or any(p in ("", ".", "..") for p in name.split("/"))
                or parsed.is_absolute()):
                raise ValueError("unsafe archive member name")
            if name in found:
                raise ValueError("duplicate archive member name")
            found.add(name)
            if member.isdir():
                if member.size != 0:
                    raise ValueError("directory has payload")
                kind = "directory"
            elif member.isfile():
                kind = "file"
            else:
                raise ValueError("archive link or special-file members forbidden")
            if member.size < 0 or member.size > MAX_MEMBER_UNCOMPRESSED:
                raise ValueError("individual archive file too large")
            total += member.size
            if total > MAX_TOTAL_UNCOMPRESSED:
                raise ValueError("expanded archive size limit exceeded")
            parts.append({"path": name, "type": kind, "uncompressed_bytes": member.size})
    if not any(p["type"] == "file" for p in parts):
        raise ValueError("archive has no actual data files")
    return {"members": parts, "total_uncompressed_bytes": total}


def inspect_bytes(archive_bytes):
    """For NEGATIVE unit tests, not the production download."""
    with tempfile.TemporaryDirectory(prefix="wsp102-fixture-") as directory:
        path = Path(directory) / "sample.tar.gz"
        if len(archive_bytes) > MAX_COMPRESSED:
            raise ValueError("compressed archive size bound exceeded")
        path.write_bytes(archive_bytes)
        return inspect_members(path)


def _download_once(destination):
    _check_url(SOURCE_URL)
    opener = build_opener(_SourceRedirect())
    req = Request(SOURCE_URL, headers={
        "User-Agent": "WSP102-Source-Custody/1.0 (research; github.com/spoonman136668-ai/Yggdrasil)",
        "Accept": "application/gzip,application/octet-stream",
    })
    begin = time.monotonic()
    dig = hashlib.sha256()
    byte_count = 0
    with opener.open(req, timeout=35) as response:
        final_url = response.geturl()
        _check_url(final_url)
        if response.status != 200:
            raise ValueError("unexpected HTTP response")
        length = response.headers.get("Content-Length")
        if length and int(length) > MAX_COMPRESSED:
            raise ValueError("declared compressed archive too large")
        content_type = response.headers.get("Content-Type", "").lower()
        if "text/html" in content_type:
            raise ValueError("HTML response instead of KG archive")
        with open(destination, "wb") as output:
            while True:
                if time.monotonic() - begin > MAX_SECONDS:
                    raise TimeoutError("source custody time limit")
                block = response.read(1024 * 1024)
                if not block:
                    break
                byte_count += len(block)
                if byte_count > MAX_COMPRESSED:
                    raise ValueError("stream exceeded frozen compressed bound")
                output.write(block)
                dig.update(block)
    if byte_count < 1024:
        raise ValueError("archive impossibly small")
    return {
        "source_url": SOURCE_URL, "resolved_url": final_url,
        "compressed_sha256": dig.hexdigest(),
        "compressed_bytes": byte_count,
        "download_wall_seconds": time.monotonic() - begin,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-custody-only", action="store_true", required=True)
    args = ap.parse_args()
    with tempfile.TemporaryDirectory(prefix="wsp102-custody-") as directory:
        archive_path = Path(directory) / "wikidata5m.tar.gz"
        meta = _download_once(archive_path)
        listing = inspect_members(archive_path)
        result = {
            "schema": SCHEMA,
            "classification": "READ_ONLY_SOURCE_METADATA_ONLY",
            "original_science_used": False,
            "first_source_rows_read": 0,
            "first_heldout_rows_read": 0,
            "training_runs": 0,
            **meta,
            **listing,
        }
        print("WSP102_SOURCE_CUSTODY=" +
              json.dumps(result, sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    main()
