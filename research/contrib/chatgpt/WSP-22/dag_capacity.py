"""WSP22 external bounded DAG oracle with independent numerical witnesses.

The search merges response sets ONLY on the six public observations. It is
not a learner, and a search miss is never reported as an UNSAT certificate.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import platform
import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]/'WSP-15'))
from structural import PlasticNand,context,LENGTHS

OBSERVED=(0,1,2,4,7,3)
TARGETS=(1,14,17,30,32,33,40,41,46,49,62)
MAX_STATES=500000
MAX_TRANSITIONS=10000000


def project(table):
    return sum(int(table[i])<<j for j,i in enumerate(OBSERVED))


RAW=tuple(project(tuple(context(i)[j] for i in range(8))) for j in range(3))


def parent_module():
    p=Path(__file__).resolve().parents[1]/'WSP-21'/'capacity.py'
    spec=importlib.util.spec_from_file_location('wsp22_parent_capacity',p)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod


def check_certificate(cert):
    """Independent checker: real 75-synapse execution and Boolean graph.

    Search-state signatures are not trusted. Only the emitted wiring is used.
    """
    if type(cert) is not dict or set(cert)!={'signature','mode','gates','output'}:
        raise ValueError('WSP22_BAD_CERTIFICATE')
    signature,mode,gates,output=(cert[k] for k in ('signature','mode','gates','output'))
    if (type(signature) is not int or signature not in range(64)
            or mode not in ('connected','allow_disconnected') or type(gates) is not list
            or len(gates)>6 or type(output) is not int or not 0<=output<3+len(gates)):
        raise ValueError('WSP22_BAD_CERTIFICATE')
    model=PlasticNand()
    for g,pair in enumerate(gates):
        if type(pair) is not list or len(pair)!=2:
            raise ValueError('WSP22_BAD_GATE')
        for side,source in enumerate(pair):
            if (type(source) is not int or not -1<=source<3+g
                    or (source==-1 and mode!='allow_disconnected')):
                raise ValueError('WSP22_ILLEGAL_SOURCE')
            model.rows[2*g+side]=[int(i==source) for i in range(3+g)]
    model.rows[-1]=[int(i==output) for i in range(9)]
    if not model.canonical():raise ValueError('WSP22_NONCANONICAL')
    table=[]
    for index in range(8):
        values=[bool(v) for v in context(index)]
        for a,b in gates:
            av=False if a==-1 else values[a]
            bv=False if b==-1 else values[b]
            values.append(not(av and bv))
        symbolic=int(values[output]);numeric=model.predict(context(index))
        if numeric!=symbolic:raise AssertionError('WSP22_RUNTIME_DISAGREEMENT')
        table.append(symbolic)
    # Reconstruct observed signature independently of the search projection.
    observed=sum(table[index]*(2**position) for position,index in enumerate(OBSERVED))
    if observed!=signature:raise ValueError('WSP22_WRONG_OBSERVED_FUNCTION')
    raw=model.snapshot();cold=PlasticNand.restore(raw)
    if cold.snapshot()!=raw or any(cold.predict(context(i))!=table[i] for i in range(8)):
        raise AssertionError('WSP22_COLD_MISMATCH')
    return {'table':table,'sites':len(gates),'checkpoint_bytes':len(raw),
            'checkpoint_sha256':hashlib.sha256(raw).hexdigest()}


def make_certificate(signature,mode,state,root,parents,last_pair):
    path=[]
    cursor=state
    while cursor!=root:
        previous,a,b=parents[cursor]
        path.append((a,b,63^(a&b)));cursor=previous
    path.reverse();a,b=last_pair;path.append((a,b,signature))
    addresses={value:j for j,value in enumerate(RAW)}
    if mode=='allow_disconnected':addresses[0]=-1
    gates=[]
    for a,b,value in path:
        gates.append([addresses[a],addresses[b]])
        addresses[value]=3+len(gates)-1
    return {'signature':signature,'mode':mode,'gates':gates,'output':3+len(gates)-1}


def search(mode,targets=TARGETS,max_sites=6,max_states=MAX_STATES,max_transitions=MAX_TRANSITIONS):
    if (mode not in ('connected','allow_disconnected') or type(max_sites) is not int
            or max_sites not in range(7) or type(max_states) is not int or max_states<1
            or type(max_transitions) is not int or max_transitions<0
            or any(type(x) is not int or x not in range(64) for x in targets)):
        raise ValueError('WSP22_BAD_SEARCH_CONFIG')
    wanted=set(targets);sources=set(RAW)
    if mode=='allow_disconnected':sources.add(0)
    root=sum(1<<v for v in sources);parents={root:None};frontier=[root]
    found={v:{'signature':v,'mode':mode,'gates':[],'output':j}
           for j,v in enumerate(RAW) if v in wanted}
    transitions=0;status='DEPTH_LIMIT_UNRESOLVED';depth=0
    for depth in range(1,max_sites+1):
        following=[]
        for state in sorted(frontier):
            values=[v for v in range(64) if state&(1<<v)]
            for i,a in enumerate(values):
                for b in values[i:]:
                    if transitions==max_transitions:
                        status='TRANSITION_CAP_UNRESOLVED';break
                    transitions+=1;value=63^(a&b)
                    # Output witnesses must precede pruning: null input0 is
                    # available but may not be selected directly as output.
                    if value in wanted and value not in found:
                        found[value]=make_certificate(value,mode,state,root,parents,(a,b))
                    if wanted.issubset(found):status='ALL_TARGETS_CERTIFIED';break
                    if state&(1<<value):continue
                    new_state=state|(1<<value)
                    if new_state in parents:continue
                    if len(parents)==max_states:
                        status='STATE_CAP_UNRESOLVED';break
                    parents[new_state]=(state,a,b);following.append(new_state)
                if status!='DEPTH_LIMIT_UNRESOLVED':break
            if status!='DEPTH_LIMIT_UNRESOLVED':break
        if status!='DEPTH_LIMIT_UNRESOLVED':break
        frontier=following
        if not frontier:status='FRONTIER_EXHAUSTED_UNRESOLVED';break
    return {'mode':mode,'status':status,'states':len(parents),'transitions':transitions,
            'reached_depth':depth,'unresolved':sorted(wanted-set(found)),
            'certificates':[found[v] for v in sorted(found)]}


def brute_depth_two(mode):
    """Independent unmerged graph enumeration on full8-bit Boolean arrays."""
    raw=[tuple(bool(context(i)[j]) for i in range(8)) for j in range(3)]
    initial=raw+([(False,)*8] if mode=='allow_disconnected' else [])
    found={sum(int(row[i])<<j for j,i in enumerate(OBSERVED)) for row in raw}
    def visit(values,remaining):
        if remaining==0:return
        for i,a in enumerate(values):
            for b in values[i:]:
                output=tuple(not(x and y) for x,y in zip(a,b))
                found.add(sum(int(output[index])<<j for j,index in enumerate(OBSERVED)))
                visit(values+[output],remaining-1)
    visit(initial,2)
    return found


def run():
    start=time.perf_counter();parent=parent_module();base={};unresolved=[]
    for sig in range(64):
        cost,mask,tree=parent.select(parent.evidence(sig))
        if cost<=6:base[sig]=[parent.embed(tree).predict(context(i)) for i in range(8)]
        else:unresolved.append(sig)
    if tuple(unresolved)!=TARGETS or len(base)!=53:raise AssertionError('WSP22_PARENT_DRIFT')
    arms={}
    for mode in ('connected','allow_disconnected'):
        tick=time.perf_counter();result=search(mode);result['seconds']=time.perf_counter()-tick
        tables=dict(base);checks=[]
        for cert in result['certificates']:
            checked=check_certificate(cert);tables[cert['signature']]=checked['table'];checks.append(checked)
        result['independently_checked']=len(checks)
        result['cold_restores']=len(checks)
        result['public_correct']=len(checks)*6
        result['numeric_symbolic_queries']=len(checks)*8
        result['certificate_sha256']=hashlib.sha256(json.dumps(result['certificates'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
        result['complete_domain_signatures']=len(tables)
        if len(tables)==64:
            hidden=0
            for mask in range(256):
                sig=sum(((mask>>i)&1)<<j for j,i in enumerate(OBSERVED))
                hidden+=sum(tables[sig][i]==((mask>>i)&1) for i in (5,6))
            if hidden!=256:raise AssertionError('WSP22_HIDDEN_LEAK')
            result['hidden_correct_of512']=hidden
        else:result['hidden_correct_of512']=None
        audited=search(mode,tuple(range(64)),max_sites=2)
        if {c['signature'] for c in audited['certificates']}!=brute_depth_two(mode):
            raise AssertionError('WSP22_DEDUP_AUDIT_FAILURE')
        result['independent_depth_two_audit']='PASS';arms[mode]=result
    canonical=len(arms['allow_disconnected']['certificates'])==11
    connected=len(arms['connected']['certificates'])==11
    report={'schema':'wsp22.six-site-dag-capacity.v1','engineering':'PASS',
            'capacity_status':'RESOLVED_SAT' if canonical else 'UNRESOLVED',
            'sharing_without_null_sufficient':connected,'arms':arms,
            'scientific_superiority':'NONE; external capacity certificates do not improve native learning',
            'parent_sha':'c497d935955950710237b22feeec03632c32ff14',
            'resident_synaptic_scalars':75,'max_sites':6,'observed_indices':OBSERVED,'targets':TARGETS,
            'seconds':time.perf_counter()-start,'environment':{'python':sys.version,'platform':platform.platform()},
            'limits':'No UNSAT assertion from misses/caps. Six-observation state merging does not identify hidden truth. External oracle answers are not supplied to the learner; zero new learning/transfer/superiority claims.'}
    print(json.dumps(report,sort_keys=True,indent=2));return report


if __name__=='__main__':run()
