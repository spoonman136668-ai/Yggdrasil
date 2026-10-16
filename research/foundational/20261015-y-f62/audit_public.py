"""Source-independent Y-F62 public-prefix and packed-memory replay auditor.

Never imports the F62 generator, its learner, historical model, or codec.
Checks the public arrivals, lossless 12-byte format, all causal memory
transitions and recorded question claims. Input is a supplied immutable
row/trace, NOT a source dispatch. Does not certify original-source custody.
"""
from __future__ import annotations
import collections, struct

CAP=12
LIMIT=6

def decode(payload):
    if not isinstance(payload,str) or len(payload)!=24:
        raise AssertionError("BAD_12_BYTE_HEX_RECEIPT")
    try:
        raw=bytes.fromhex(payload)
    except ValueError as exc:
        raise AssertionError("BAD_HEX") from exc
    assert len(raw)==12
    start,end=struct.unpack("<II",raw[:8])
    packed=int.from_bytes(raw[8:11],"little")
    length=raw[11]
    assert 1<=length<=LIMIT and (packed>>(3*length))==0, "NONCANONICAL_PACKING"
    codes=tuple((packed>>(3*i))&7 for i in range(length))
    return (start,end,codes)

def encode(rec):
    a,b,codes=rec
    assert 0<=a<2**32 and 0<=b<2**32
    assert 1<=len(codes)<=LIMIT and all(0<=c<8 for c in codes)
    packed=sum(x<<(3*i) for i,x in enumerate(codes))
    return (struct.pack("<II",a,b)+packed.to_bytes(3,"little")+
            bytes([len(codes)])).hex()

def inverse(rec):
    a,b,c=rec
    return b,a,tuple(x^1 for x in reversed(c))

def combine(a,b):
    if a[1]!=b[0] or len(a[2])+len(b[2])>LIMIT:
        return None
    return a[0],b[1],a[2]+b[2]

def proposals(before,event):
    assert len(event)==3, "PRIVATE_TAG_ENTERED_ONLINE"
    a,role,b=event
    assert 0<=role<=3 and 0<=a<2**32 and 0<=b<2**32
    incoming=(a,b,(role*2,))
    offered=[(-1,incoming)]
    for i,prev in enumerate(before):
        possibilities=((prev,incoming),(incoming,prev),
                       (inverse(prev),incoming),(incoming,inverse(prev)),
                       (prev,inverse(incoming)),(inverse(incoming),prev))
        for left,right in possibilities:
            merged=combine(left,right)
            if merged is not None and len(merged[2])>1 and merged[0]!=merged[1]:
                offered.append((i,merged))
    valid=set()
    for prior_index,rec in offered:
        retained=tuple(x for j,x in enumerate(before) if j!=prior_index)
        before_eviction=retained+(rec,)
        drops=(-1,) if len(before_eviction)<=CAP else range(len(before_eviction))
        for drop in drops:
            candidate=tuple(x for j,x in enumerate(before_eviction) if j!=drop)
            if len(candidate)<=CAP:
                valid.add(candidate)
    return valid

def prefix_witness(rec,seen_edges):
    """Verify a complete public role/direction path, never private labels."""
    start,end,codes=rec
    endpoints={start}
    for code in codes:
        role=code//2
        backwards=code&1
        remaining=set()
        for a,r,b in seen_edges:
            if r!=role:
                continue
            src,dst=(b,a) if backwards else (a,b)
            if src in endpoints:
                remaining.add(dst)
        endpoints=remaining
        if not endpoints:
            return False
    return end in endpoints

def solve(records,question):
    remaining=tuple(2*r+(direction==-1) for r,direction in question["ops"])
    at=question["start"]
    visited=set()
    while remaining:
        eligible=set()
        for rec in records:
            for item in (rec,inverse(rec)):
                a,b,c=item
                if a==at and tuple(remaining[:len(c)])==c:
                    eligible.add(item)
        if len(eligible)!=1:
            return None
        a,at,c=next(iter(eligible))
        remaining=remaining[len(c):]
        marker=(at,remaining)
        if marker in visited:
            return None
        visited.add(marker)
    return at

def public_question_witness(edges,question):
    """Ground claimed answer solely in public graph without private paths."""
    states={question["start"]}
    for role,direction in question["ops"]:
        assert 0<=role<=3 and direction in (-1,1)
        nxt=set()
        for a,r,b in edges:
            if r==role:
                src,dst=(a,b) if direction==1 else (b,a)
                if src in states:
                    nxt.add(dst)
        states=nxt
        if not states:
            break
    assert states=={question["answer"]}, "QUESTION_NOT_PUBLICLY_UNIQUE"
    return True

def verify(public_events,question,prefix_hex,expected_final=None):
    """Return read-only forensic counts after checking every online prefix."""
    assert len(public_events)==72 and len(prefix_hex)==len(public_events)
    assert all(len(event)==3 for event in public_events), "PRIVATE_TAG_IN_STREAM"
    assert len(set(tuple(x) for x in public_events))==72
    before=()
    seen=[]
    max_bytes=0
    verified=0
    for index,(event,snapshot) in enumerate(zip(public_events,prefix_hex)):
        assert len(snapshot)<=CAP, "SERIALIZED_PAYLOAD_OVERFLOW"
        after=tuple(decode(value) for value in snapshot)
        assert len(set(after))==len(after), "DUPLICATE_RETAINED_RECORD"
        assert after in proposals(before,tuple(event)), "NONCAUSAL_MEMORY_TRANSITION"
        seen.append(tuple(event))
        for rec in after:
            assert prefix_witness(rec,seen), "RECORD_USES_UNSEEN_OR_FUTURE_EDGE"
            assert encode(rec) in snapshot, "LOSSLESS_RECEIPT_DRIFT"
            verified+=1
        bytes_used=len(snapshot)*12
        assert bytes_used<=144
        max_bytes=max(max_bytes,bytes_used)
        before=after
    public_question_witness(public_events,question)
    if expected_final is not None:
        assert tuple(expected_final)==tuple(prefix_hex[-1]), "FINAL_RECEIPTS_NOT_SNAPSHOT"
    observed=solve(before,question)
    return dict(prefixes=len(public_events),max_payload_bytes=max_bytes,
                reconstructed_records=verified,
                retained_question_prediction=observed,
                publicly_grounded_question=True,
                source_independent_F3=False)
