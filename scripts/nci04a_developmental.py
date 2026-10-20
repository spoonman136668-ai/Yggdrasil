"""Offline opt-in source-free developmental candidate. No authority or model API."""
import json
import pathlib
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from yggdrasil.developmental import LocalGenome

def run(instream,outstream):
    model=LocalGenome()
    budget=0
    for line in instream:
        budget+=len(line.encode("utf-8"))
        if budget>1_048_576: raise ValueError("input budget exceeded")
        if not line.strip(): continue
        event=json.loads(line)
        op=event.get("op")
        if op=="observe" and set(event)<={"op","bits","consequences","rate"}:
            model.observe(event["bits"],event["consequences"],event.get("rate",.035))
        elif op=="predict" and set(event)=={"op","bits"}:
            outstream.write(json.dumps({"probabilities":model.predict(event["bits"])})+"\n")
        elif op=="lesion" and set(event)=={"op","cell"}:
            model.lesion(event["cell"])
        elif op=="snapshot" and set(event)=={"op"}:
            outstream.write(model.snapshot()+"\n")
        elif op=="restore" and set(event)=={"op","snapshot"}:
            model.restore(json.dumps(event["snapshot"]))
        elif op=="cell_roles" and set(event)=={"op","cell"}:
            outstream.write(json.dumps({"role_weights":model.role_weights(event["cell"])})+"\n")
        else:
            raise ValueError("unknown or improperly scoped developmental operation")

if __name__=="__main__":
    try:
        run(sys.stdin,sys.stdout)
    except (ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:
        print(str(exc),file=sys.stderr)
        sys.exit(1)
