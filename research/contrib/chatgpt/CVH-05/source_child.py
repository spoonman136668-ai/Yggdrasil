"""CVH-05 original-source OS worker: constructor ONLY, no reset/do.

The ORIGINAL unchanged causal_gym.envs.mdp.MDPPCH object is constructed only
inside this isolated short-lived process, using the exact byte-pinned FKP25
verification and CVH03 factory. It is NEVER sent to a policy/parent process.

This is NOT an original-world action executor, scheduler, service, sandbox,
first-use permission or scientific evaluation endpoint. Any command other
than the single public 'close' request fails closed. There is deliberately no
method capable of selecting or executing a physical original source action.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
PARENT_FACTORY=HERE.parent/"CVH-03"/"source_binding.py"
SCHEMA="cvh05.original-source-constructor-only.v1"
MAX_BYTES=4096
HELLO_KEYS={"schema","kind","source_sha","source_blobs",
            "original_objects","source_resets","source_actions"}
CLOSE_KEYS={"schema","kind"}


def emit(obj):
    sys.stdout.write(json.dumps(obj,sort_keys=True,
                                separators=(",",":"),allow_nan=False)+"\n")
    sys.stdout.flush()


def reject(code):
    emit({"schema":SCHEMA,"kind":"error","code":code})
    return 2


def parse_close(raw):
    if (type(raw) is not bytes or not raw.endswith(b"\n")
            or not 0<len(raw)<=MAX_BYTES):
        raise ValueError("CVH05_CLOSE_BAD_FRAME")
    try:
        command=json.loads(raw)
    except (ValueError,TypeError,UnicodeError) as e:
        raise ValueError("CVH05_CLOSE_BAD_JSON") from e
    if (type(command) is not dict or set(command)!=CLOSE_KEYS
            or command.get("schema")!=SCHEMA or command.get("kind")!="close"):
        raise ValueError("CVH05_CLOSE_COMMAND_DENIED")
    return True


def source_factory():
    """Load the existing exact original-source factory without importing source.

    Source classes are first imported inside its verified context, not here.
    """
    if not PARENT_FACTORY.is_file():
        raise ValueError("CVH05_REQUIRED_QUALIFIED_CVH03_FACTORY_ABSENT")
    spec=importlib.util.spec_from_file_location(
        "cvh05_inherited_exact_source_binding",PARENT_FACTORY)
    if spec is None or spec.loader is None:
        raise ValueError("CVH05_INHERITED_FACTORY_IMPORT_UNAVAILABLE")
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(spec.name,None)
        raise
    return module.verified_original_factory


def execute_constructor_only(checkout,read_command):
    """Run once, seal the verified object in this process, await close only."""
    gate=source_factory()
    with gate(checkout) as (factory,receipt):
        original_object=factory()
        if factory.constructed!=1 or original_object is None:
            raise ValueError("CVH05_ORIGINAL_FACTORY_CONSTRUCT_COUNT")
        if (receipt["source_action_calls"]!=0
                or receipt["source_reset_calls"]!=0
                or receipt["source_first_use"] is not False
                or receipt["scientific_pass"] is not False):
            raise ValueError("CVH05_ORIGINAL_WORLD_ACTION_DISALLOWED")
        ready={
          "schema":SCHEMA,"kind":"ready",
          "source_sha":receipt["source_sha"],
          "source_blobs":receipt["source_blobs_verified"],
          "original_objects":factory.constructed,
          "source_resets":0,"source_actions":0,
        }
        if set(ready)!=HELLO_KEYS:
            raise ValueError("CVH05_PUBLIC_ACK_SCHEMA_DRIFT")
        emit(ready)
        # No world-object method is callable from this protocol. Any extra
        # metadata, action, reset or missing close ends the process.
        try:
            parse_close(read_command(MAX_BYTES+1))
        except ValueError:
            return reject("ONLY_EXPLICIT_CLOSE_ALLOWED")
        emit({"schema":SCHEMA,"kind":"closed"})
    return 0


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--checkout",required=True)
    parser.add_argument("--constructor-only",action="store_true")
    args=parser.parse_args()
    if not args.constructor_only:
        return reject("SOURCE_ACTIONS_AND_WORLD_FIRSTUSE_DISARMED")
    # No import, checkout, source constructor or original action before the
    # explicit constructor-only flag is validated.
    try:
        return execute_constructor_only(args.checkout,sys.stdin.buffer.readline)
    except BaseException:
        # Fail closed with deliberately generic error; never leak private
        # traceback/source law to parent stdout. A bounded child exits.
        return reject("EXACT_ORIGINAL_SOURCE_CUSTODY_OR_CONSTRUCTOR_FAILED")


if __name__=="__main__":
    raise SystemExit(main())
