"""Opt-in NCI-04D2 project-native task execution over JSONL.

No filesystem, protected scientific original, controller or network operation.
"""
import json
import pathlib
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from yggdrasil.task_runtime import LocalTaskRuntime, LocalCountControl

def run(instream,outstream):
    task=None
    control=None
    size=0
    seen=0
    for line in instream:
        size+=len(line.encode("utf-8"));seen+=1
        if size>1_048_576 or seen>4096: raise ValueError("task input budget exceeded")
        if not line.strip(): continue
        event=json.loads(line)
        if type(event)!=dict:raise ValueError("invalid event")
        op=event.get("op")
        if op=="init" and set(event)<={"op","neighbors"} and task is None:
            task=LocalTaskRuntime(event.get("neighbors"))
            control=LocalCountControl(task.neighbors)
        elif op=="restore" and set(event)=={"op","snapshot"}:
            if task is not None: raise ValueError("reinitialization prohibited")
            task=LocalTaskRuntime.restore(json.dumps(event["snapshot"]))
            # A historical conventional control cannot be forged from a
            # candidate's checkpoint. Must separately retrain the comparator.
            control=None
        elif task is None:
            raise ValueError("initialize task first")
        elif op=="observe" and set(event)<={"op","bits","outcomes","rate"} and "bits" in event and "outcomes" in event:
            task.observe(event["bits"],event["outcomes"],event.get("rate",.035))
            if control is not None: control.observe(event["bits"],event["outcomes"])
        elif op=="predict" and set(event)=={"op","bits"}:
            row={"candidate":task.predict(event["bits"])}
            if control is not None: row["count_control"]=control.predict(event["bits"])
            outstream.write(json.dumps(row,sort_keys=True)+"\n")
        elif op=="lesion" and set(event)=={"op","cells"}:
            task.lesion(event["cells"])
        elif op=="repair_unlabeled" and set(event)<={"op","bits","steps","rate"} and "bits" in event:
            outstream.write(json.dumps({"candidate_after_repair":task.repair_unlabeled(event["bits"],event.get("steps",1),event.get("rate",.05))},sort_keys=True)+"\n")
        elif op=="snapshot" and set(event)=={"op"}:
            outstream.write(task.snapshot()+"\n")
        else:raise ValueError("unsupported task operation or post-lesion training")

if __name__=="__main__":
    try:run(sys.stdin,sys.stdout)
    except (ValueError,TypeError,KeyError,json.JSONDecodeError) as exc:
        print(str(exc),file=sys.stderr)
        sys.exit(1)
