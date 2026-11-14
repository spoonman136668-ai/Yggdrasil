#!/usr/bin/env python3
"""Standalone H04 DEV receipt; no original scientific world first use."""
import argparse
import json
from headroom_h04_experiment import audit

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fixed-dev-only", action="store_true", required=True)
    p.parse_args()
    print("WSP101_H04_DEV_RESULT="+json.dumps(audit(),sort_keys=True,separators=(",",":")),flush=True)

if __name__=="__main__":
    main()
