"""NCI-04G7A: bounded *simulated environment*, NOT an external sensor.

This process owns the next-state consequence and returns ONLY a locally
surviving cell's measured bit. It does not use or consult any learned model.
It never sends the damaged cell's outcome. Counterfactual action changes
the sender's transition. The rule is intentionally simple and source-free;
its task-family status is DEVELOPMENT ONLY, not independent scientific data.
"""
import json
import sys

N=8
MAX_BYTES=512

def bitvec(v):
    return type(v)==list and len(v)==N and all(type(x)==int and x in (0,1) for x in v)

def measure(event):
    if type(event)!=dict or set(event)!={"prior","action","sender","damaged"}:
        raise ValueError("invalid environment request")
    prior=event["prior"]
    action=event["action"]
    sender=event["sender"]
    damaged=event["damaged"]
    if not bitvec(prior) or type(action)!=int or action not in (0,1):
        raise ValueError("invalid bounded sensor input")
    if type(sender)!=int or type(damaged)!=int or not 0<=sender<N or not 0<=damaged<N:
        raise ValueError("invalid sender or damaged identity")
    if sender not in ((damaged-1)%N,(damaged+1)%N):
        raise ValueError("sender is not one hop from damaged target")
    # One-hop surviving neighbor OTHER than the damaged cell, plus sender's
    # own prior state and intervention. Never read damaged's state.
    other=(sender-1)%N if (sender+1)%N==damaged else (sender+1)%N
    outcome=prior[sender] ^ prior[other] ^ action
    return {"schema":"yggdrasil.nci04g7a.native-world.v1",
            "sender":sender,"damaged":damaged,"action":action,
            "observed_sender_next_bit":outcome,
            "source":"SOURCE_PINNED_SIMULATED_ENVIRONMENT_NOT_EXTERNAL_SENSOR"}

def main():
    data=sys.stdin.buffer.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES:
        raise ValueError("environment input budget exceeded")
    event=json.loads(data)
    out=measure(event)
    sys.stdout.write(json.dumps(out,sort_keys=True,separators=(",",":"))+"\n")

if __name__=="__main__":
    try:main()
    except (ValueError,TypeError,KeyError,UnicodeError,json.JSONDecodeError) as exc:
        print("NCI04G7A_ENV_FAIL_CLOSED "+str(exc),file=sys.stderr)
        sys.exit(1)
