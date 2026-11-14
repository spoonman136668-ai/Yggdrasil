#!/usr/bin/env python3
"""Optional explicit CLI for H05 synthetic development result; no model changes."""
import argparse
import json
from headroom_h05_experiment import audit

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed-dev-only", action="store_true", required=True)
    parser.parse_args()
    print("WSP101_H05_DEV_RESULT=" +
          json.dumps(audit(), sort_keys=True, separators=(",", ":")), flush=True)
