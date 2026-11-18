"""Seals exactly one original CKAD30 B run artifact; never reruns primary or adjusts model."""
import argparse
import json
from pathlib import Path

from audit_primary import audit_raw

HERE = Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-result",type=Path,required=True)
    args=parser.parse_args()
    raw=args.source_result.read_bytes()
    report=audit_raw(raw)
    (HERE/"primary_result.json").write_bytes(raw)
    (HERE/"primary_audit.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps(report,sort_keys=True))


if __name__=="__main__":
    main()
