"""Bounded offline JSONL interface for native local-cell learning."""
import json
import pathlib
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from yggdrasil.cells import DevelopmentalCells

def run(instream,outstream):
    cells=DevelopmentalCells()
    budget=0
    for line in instream:
        budget+=len(line.encode("utf-8"))
        if budget>1_048_576:
            raise ValueError("input budget exceeded")
        if not line.strip():
            continue
        obj=json.loads(line)
        op=obj.get("op")
        if op=="observe" and set(obj)<={"op","bits","consequences","rate"}:
            cells.observe(obj["bits"],obj["consequences"],obj.get("rate",0.038))
        elif op=="predict" and set(obj)=={"op","bits"}:
            outstream.write(json.dumps({"probabilities":cells.predict(obj["bits"])})+"\n")
        elif op=="lesion" and set(obj)=={"op","cell"}:
            cells.lesion(obj["cell"])
        elif op=="neighbor_copy_baseline" and set(obj)=={"op","cell"}:
            cells.neighbor_copy_baseline(obj["cell"])
        elif op=="snapshot" and set(obj)=={"op"}:
            outstream.write(cells.snapshot()+"\n")
        elif op=="restore" and set(obj)=={"op","snapshot"}:
            cells.restore(json.dumps(obj["snapshot"]))
        else:
            raise ValueError("unknown or improperly scoped operation")

if __name__=="__main__":
    try:
        run(sys.stdin,sys.stdout)
    except (ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:
        print(str(exc),file=sys.stderr)
        sys.exit(1)
