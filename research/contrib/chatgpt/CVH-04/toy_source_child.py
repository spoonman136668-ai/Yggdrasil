"""CVH-04 source-free toy process implementing a strict public event wire.

Short-lived subprocess launched only by explicit local/CI tests; never a
scheduler, owner loop, remote source service, or original CausalGym world.
There are deliberately no imports of any original environment package.
All original-source seeds and all original reset/do calls are refused.
"""
from __future__ import annotations

import argparse
import json
import sys
import time

SCHEMA="cvh04.public-event-wire.v1"
SEEDS=tuple(range(1,7))
LIMIT=6
MAX_LINE=4096


def write(value):
    sys.stdout.write(json.dumps(value,sort_keys=True,separators=(",",":"))+"\n")
    sys.stdout.flush()


def fail(code):
    # Generic code only, never send internal source state or private data.
    write({"schema":SCHEMA,"kind":"error","code":code})
    return 2


def main():
    parser=argparse.ArgumentParser(description="EXPLICIT MOCK ONLY: no original source")
    parser.add_argument("--mock-only",action="store_true")
    parser.add_argument("--toy-seed",type=int,required=True)
    parser.add_argument("--fault",choices=("none","private","wrong_action","wrong_seq","stall"),default="none")
    cfg=parser.parse_args()
    if not cfg.mock_only or cfg.toy_seed not in SEEDS:
        return fail("NOT_AUTHORIZED_ORIGINAL_SOURCE")
    state=cfg.toy_seed%2
    # Opaque private variable remains exclusively inside this subprocess.
    private_source_salt=cfg.toy_seed*107+19
    write({"schema":SCHEMA,"kind":"ready","before":state,"mock_seed":cfg.toy_seed})
    seq=0
    while seq<LIMIT:
        raw=sys.stdin.buffer.readline(MAX_LINE+1)
        if not raw or len(raw)>MAX_LINE:
            return fail("EMPTY_OR_OVERSIZE_REQUEST")
        try:
            obj=json.loads(raw)
        except (UnicodeError,ValueError):
            return fail("BAD_JSON_REQUEST")
        if (type(obj) is not dict or set(obj)!={"schema","kind","seq","action"}
                or obj["schema"]!=SCHEMA or obj["kind"]!="act"
                or type(obj["seq"]) is not int or obj["seq"]!=seq+1
                or type(obj["action"]) is not int or obj["action"] not in (0,1)):
            return fail("BAD_PUBLIC_ACTION_REQUEST")
        seq+=1
        action=obj["action"]
        before=state
        # All outcomes occur ONLY after a chosen public action arrives.
        state=before^action^((seq+cfg.toy_seed)&1)
        reward=int(seq>=3 and (seq+action+private_source_salt)%3==0)
        event={"schema":SCHEMA,"kind":"event","seq":seq,
               "before":before,"action":action,"reward":reward,
               "after":state,"terminated":False,"truncated":seq==LIMIT}
        if cfg.fault=="private":
            event["private_source_salt"]=private_source_salt
        elif cfg.fault=="wrong_action":
            event["action"]=1-action
        elif cfg.fault=="wrong_seq":
            event["seq"]=seq+1
        elif cfg.fault=="stall":
            time.sleep(4)
        write(event)
        if cfg.fault!="none":
            return 3
    return 0


if __name__=="__main__":
    raise SystemExit(main())
