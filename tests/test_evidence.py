import json

import pytest

from yggdrasil.evidence import write_evidence


def test_evidence_writer_is_json_and_atomic(tmp_path) -> None:
    path = write_evidence(tmp_path / "run.json", {"value": 1.25})
    loaded = json.loads(path.read_text())

    assert loaded["value"] == 1.25
    assert loaded["schema"]


def test_evidence_rejects_nonfinite(tmp_path) -> None:
    with pytest.raises(ValueError, match="non-finite"):
        write_evidence(tmp_path / "bad.json", {"value": float("nan")})
