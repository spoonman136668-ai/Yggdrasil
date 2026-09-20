#!/usr/bin/env python3
import argparse
import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

BASE_EDGES = [
    (0,2,7,9),(1,3,6,11),(4,5,9,10),(2,3,5,8),(0,1,4,8),
    (6,7,8,10),(2,4,6,11),(0,3,5,7),(1,7,10,11),(1,5,6,9),
    (3,8,9,10),(0,4,8,11),(0,2,6,10),(1,3,4,7),(2,5,7,11),
    (2,3,4,10),(0,1,5,10),(0,3,9,11),(1,2,8,9),(4,6,7,9),
]
EXPECTED_DEG = (7,7,7,7,7,6,6,7,6,7,7,6)
BLOCKS=12
CHECKS=20
PLANES=4
BASELINE_WEIGHT4_ALL_MIN_NONZERO=60


def normalize_edges(edges):
    return tuple(tuple(sorted(e)) for e in edges)


def columns(edges):
    out=[0]*BLOCKS
    for i,e in enumerate(edges):
        for b in e:
            out[b] |= 1 << i
    return tuple(out)


def degree_vector(edges):
    return tuple(c.bit_count() for c in columns(edges))


def pair_cooccurrence(edges):
    c=Counter()
    for e in edges:
        for a,b in itertools.combinations(e,2):
            c[tuple(sorted((a,b)))] += 1
    return max(c.values()) if c else 0


def gf2_rank(vectors):
    basis={}
    for x in vectors:
        v=int(x)
        while v:
            p=v.bit_length()-1
            if p in basis:
                v ^= basis[p]
            else:
                basis[p]=v
                break
    return len(basis)


def logical_syndromes(cols):
    syn=[0]*(1<<BLOCKS)
    for m in range(1,1<<BLOCKS):
        lsb=m & -m
        b=lsb.bit_length()-1
        syn[m]=syn[m ^ lsb] ^ cols[b]
    return syn


def candidate_topology(block, source, target):
    edges=[list(e) for e in BASE_EDGES]
    assert block in edges[source]
    assert block not in edges[target]
    edges[source].remove(block)
    edges[target].append(block)
    return normalize_edges(edges)


def candidate_triples():
    out=[]
    for b in range(BLOCKS):
        sources=[i for i,e in enumerate(BASE_EDGES) if b in e]
        targets=[j for j,e in enumerate(BASE_EDGES) if b not in e]
        for i in sources:
            for j in targets:
                out.append((b,i,j))
    return tuple(out)


def validate_baseline():
    assert len(BASE_EDGES)==CHECKS
    assert all(len(e)==4 for e in BASE_EDGES)
    assert sum(len(e) for e in BASE_EDGES)==80
    assert degree_vector(BASE_EDGES)==EXPECTED_DEG
    assert pair_cooccurrence(BASE_EDGES)<=2
    return True


def validate_candidate_family():
    validate_baseline()
    triples=candidate_triples()
    assert len(triples)==len(set(triples))
    for b,i,j in triples:
        e=candidate_topology(b,i,j)
        ar=[len(x) for x in e]
        assert len(e)==CHECKS
        assert sum(ar)==80
        assert degree_vector(e)==EXPECTED_DEG
        assert ar[i]==3
        assert ar[j]==5
        assert sum(x==3 for x in ar)==1
        assert sum(x==5 for x in ar)==1
        assert sum(x==4 for x in ar)==18
        diffs=[]
        for k,(base,new) in enumerate(zip(normalize_edges(BASE_EDGES),e)):
            if base!=new:
                diffs.append(k)
        assert sorted(diffs)==sorted([i,j])
    return {
        "candidate_count":len(triples),
        "baseline_checks":CHECKS,
        "baseline_total_incidence":80,
        "degree_vector":list(EXPECTED_DEG),
    }


def topology_metrics(edges):
    cols=columns(edges)
    syn=logical_syndromes(cols)
    rank=gf2_rank(cols)
    kernel=[m for m in range(1,1<<BLOCKS) if syn[m]==0]
    single=min(c.bit_count() for c in cols)
    pair=min((cols[a]^cols[b]).bit_count() for a,b in itertools.combinations(range(BLOCKS),2))
    positive=[x.bit_count() for x in syn[1:] if x]
    return {
        "rank":rank,
        "kernel_count":len(kernel),
        "max_pair_cooccurrence":pair_cooccurrence(edges),
        "single_floor":single,
        "pair_floor":pair,
        "global_positive_floor":min(positive) if positive else None,
        "zero_nonzero_masks":len(kernel),
    }, cols, syn


def feasible(m):
    return (
        m["rank"]==12 and m["kernel_count"]==0 and
        m["max_pair_cooccurrence"]<=2 and
        m["single_floor"]>=6 and m["pair_floor"]>=8
    )


def enumerate_candidates():
    rows=[]
    for b,i,j in candidate_triples():
        edges=candidate_topology(b,i,j)
        m,_,_=topology_metrics(edges)
        row={"block":b,"source_check":i,"target_check":j,**m,"feasible":bool(feasible(m))}
        rows.append(row)
    feas=[r for r in rows if r["feasible"]]
    selected=None
    if feas:
        selected=min(
            feas,
            key=lambda r:(
                -r["global_positive_floor"],
                -r["pair_floor"],
                -r["single_floor"],
                r["max_pair_cooccurrence"],
                r["block"],r["source_check"],r["target_check"],
            ),
        )
    hist={
        "rank":dict(sorted(Counter(r["rank"] for r in rows).items())),
        "max_pair_cooccurrence":dict(sorted(Counter(r["max_pair_cooccurrence"] for r in rows).items())),
        "pair_floor":dict(sorted(Counter(r["pair_floor"] for r in rows).items())),
        "global_positive_floor":dict(sorted(Counter(r["global_positive_floor"] for r in rows).items())),
    }
    return rows,feas,selected,hist


def logical_geometry(edges):
    cols=columns(edges)
    syn=logical_syndromes(cols)
    d=defaultdict(list)
    by_w={w:Counter() for w in range(BLOCKS+1)}
    for m,s in enumerate(syn):
        d[s].append(m)
        by_w[m.bit_count()][s.bit_count()] += 1
    mult=Counter(len(v) for v in d.values())
    out={
        "rank":gf2_rank(cols),
        "distinct_syndromes":len(d),
        "multiplicity_histogram":{str(k):int(v) for k,v in sorted(mult.items())},
        "kernel_masks":[m for m in range(1,1<<BLOCKS) if syn[m]==0],
        "minimum_positive_by_logical_weight":{},
    }
    for w in range(1,BLOCKS+1):
        vals=[]
        for sw,count in by_w[w].items(): vals.extend([sw]*count)
        pos=[x for x in vals if x>0]
        out["minimum_positive_by_logical_weight"][str(w)]={
            "minimum":min(pos) if pos else None,
            "zero_syndrome_count":sum(x==0 for x in vals),
        }
    return out


def numpy_arrays(edges):
    cols=colums(edges)
    syn=logical_syndromes(cols)
    syndromes=np.asarray(syn,dtype=np.uint32)
    lweights=np.asarray([m.bit_count() for m in range(1<<BLOCKS)],dtype=np.int16)
    pc=np.fromiter((i.bit_count() for i in range(1<<CHECKS)),dtype=np.uint8,count=1<<CHECKS)
    return syndromes,lweights,pc


def mask_positions(xs):
    m=0
    for x in xs: m |= 1<<x
    return m


def equal_cost_check_only(edges):
    syndromes,lweights,pc=numpy_arrays(edges)
    result={}
    for w in range(1,5):
        counts=Counter()
        n=0
        for comb in itertools.combinations(range(CHECKS),w):
            s=mask_positions(comb)
            residual=pc[np.bitwise_xor(syndromes,np.uint32(s))].astype(np.int32)
            costs=lweights.astype(np.int32)+residual
            mc=int(costs.min())
            minima=np.flatnonzero(costs==mc)
            zero_in=bool(np.any(minima==0))
            if zero_in and len(minima)==1: counts["zero_unique"]+=1
            elif zero_in: counts["zero_tied"]+=1
            else: counts["all_minima_nonzero"]+=1
            n+=1
        assert n==math.comb(CHECKS,w)
        result[str(w)]={
            "patterns":n,
            "zero_unique":int(counts["zero_unique"]),
            "zero_tied":int(counts["zero_tied"]),
            "all_minima_nonzero":int(counts["all_minima_nonzero"]),
            "zero_unique_fraction":float(counts["zero_unique"]/n),
            "zero_tied_fraction":float(counts["zero_tied"]/n),
            "all_minima_nonzero_fraction":float(counts["all_minima_nonzero"]/n),
        }
    return result


def incident(edges,b):
    return [i for i,e in enumerate(edges) if b in e]


def classify_check4(edges,b):
    syndromes,lweights,pc=numpy_arrays(edges)
    slots=incident(edges,b)[:4]
    assert len(slots)==4
    s=mask_positions(slots)
    residual=pc[np.bitwise_xor(syndromes,np.uint32(s))].astype(np.int32)
    costs=lweights.astype(np.int32)+residual
    mc=int(costs.min())
    minima=np.flatnonzero(costs==mc)
    zero_in=bool(np.any(minima==0))
    if zero_in and len(minima)==1: cls="TRUE_CHECK_ONLY_UNIQUE_MINIMUM"
    elif zero_in: cls="TRUE_CHECK_ONLY_TIEDÓRS’SUSH‚ˆ[ÙNˆÛÏH••QWÐÒPÒ×ÓÓ“WÓ“ÕÓRS’SUSH‚ˆ™]\›ˆÂˆ˜›ØÚÈŽ˜‹™YÜ™YHŽ›[Š[˜ÚY[
YÙ\ËŠJKš[˜ÚY[ØÚXÚÜÈŽœÛÝËˆ›Z[š[][WØÛÜÝŽ›XË›Z[š[][WØÛÝ[Žš[
[ŠZ[š[XJJKˆ˜Û\ÜÚYšXØ][ÛˆŽ˜ÛË›Z[š[][WÛÙÚXØ[ÛX\ÚÜÈŽ–Ú[

H›Üˆ[ˆZ[š[XVÎŒÌ—WKˆB‚‚™YˆÜ›ÜÜÜ[™JYÙ\ÊN‚ˆÛÛÏXÛÛ[[œÊYÙ\ÊBˆ›ÝÜÏV×Bˆ›Üˆˆ[ˆ˜[™ÙJ“ÐÒÔÊN‚ˆ[˜ÏZ[˜ÚY[
YÙ\ËŠBˆÚXÚÛX\ÚÏ[X\Ú×ÜÜÚ][ÛœÊ[˜ÊBˆ›Üˆ[ˆ˜[™ÙJKS‘TÊÌJN‚ˆÙÚXØ[VØÛÛÖØ—HYˆÏ[ÙH›ÜˆÈ[ˆ˜[™ÙJS‘TÊWBˆÚXÚÏVØÚXÚÛX\ÚÈYˆÏ[ÙH›ÜˆÈ[ˆ˜[™ÙJS‘TÊWBˆ›ÝÜË˜\[™
Âˆ˜›ØÚÈŽ˜‹œ[™\ÈŽœ™YÜ™YHŽ›[Š[˜ÊKˆ™^XÝÜÞ[™›ÛYWÙ\]X[]HŽ˜›ÛÛ
ÙÚXØ[OXÚXÚÊKˆ›ÙÚXØ[Ù˜][Øš]ØÛÝ[Žœˆš[YÜš]WÙ˜][Øš]ØÛÝ[Ž›[Š[˜ÊJœˆš[YÜš]WØÚ[›™[Ù]™[ØÛÝ[Ž›[Š[˜ÊKˆJBˆ™]\›ˆÈœ›ÝÜÈŽœ›ÝÜË™^XÝÛZ[ZX×Ù^\ÝÈŽ˜›ÛÛ
[žJ–È™^XÝÜÞ[™›ÛYWÙ\]X[]H—H›Üˆˆ[ˆ›ÝÜÊJ_B‚‚™YˆZ[ÜÙ[XÝYÙYÙ\ÊÙ[XÝY
N‚ˆ™]\›ˆØ[™Y]WÝÜÛÙÞJÙ[XÝYÈ˜›ØÚÈ—KÙ[XÝYÈœÛÝ\˜ÙWØÚXÚÈ—KÙ[XÝYÈ\™Ù]ØÚXÚÈ—JB‚‚™Yˆ[Š
N‚ˆYXÚ[šXØ[]˜[Y]WØØ[™Y]WÙ˜[Z[J
Bˆ˜\Ù[[™WÛY]šXÜËËÏ]ÜÛÙÞWÛY]šXÜÊ›Ü›X[^™WÙYÙ\ÊTÑWÑQÑTÊJBˆ›ÝÜË™X\ËÙ[XÝY\ÝY[[Y\˜]WØØ[™Y]\Ê
Bˆ\ÜÙ\[Š›ÝÜÊOO[YXÚ[šXØ[È˜Ø[™Y]WØÛÝ[—BˆYˆÙ[XÝY\È›Û™N‚ˆÙ[XÝYÙYÙ\ÏS›Û™BˆÛÝ]S›Û™BˆÚYÛ˜[Ï^Âˆœ\š]WØœ›ÚÙ[—Ù™X\ÚX›HŽ‘˜[ÙKˆœÙ[XÝYÙ[Ü˜[šÈŽ‘˜[ÙKˆœÙ[XÝYÚÙ\›™[Ùœ™YHŽ‘˜[ÙKˆ›ØØ[Ù›ÛÜœ×Ü™\Ù\™YŽ‘˜[ÙKˆœZ\—ØÛÛØØÝ\œ™[˜ÙWÜ™\Ù\™YŽ‘˜[ÙKˆ™ÛØ˜[Ù\Ý[˜ÙWÚ[\›Ý™YŽ‘˜[ÙKˆ˜ÚXÚÍÙ\]X[ØÛÜÝÛ›ÝÝÛÜœÙHŽ‘˜[ÙKˆ˜Ü›ÜÜÜ[™WØ\˜š]˜\žWØÛÜœ™[][Û—ÜÛÛ™YŽ‘˜[ÙKˆBˆ[ÙN‚ˆÙ[XÝYÙYÙ\ÏXZ[ÜÙ[XÝYÙYÙ\ÊÙ[XÝY
BˆÙ[XÝYÛY]šXÜËËÏ]ÜÛÙÞWÛY]šXÜÊÙ[XÝYÙYÙ\ÊBˆ˜\ÙWØÚXÚÏY\]X[ØÛÜÝØÚXÚ×ÛÛ›J›Ü›X[^™WÙYÙ\ÊTÑWÑQÑTÊJBˆÙ[ØÚXÚÏY\]X[ØÛÜÝØÚXÚ×ÛÛ›JÙ[XÝYÙYÙ\ÊBˆÛÝ]^Âˆ˜˜\Ù[[™WÛÙÚXØ[ÙÙ[ÛY]žHŽ›ÙÚXØ[ÙÙ[ÛY]žJ›Ü›X[^™WÙYÙ\ÊTÑWÑQÑTÊJKˆœÙ[XÝYÛÙÚXØ[ÙÙ[ÛY]žHŽ›ÙÚXØ[ÙÙ[ÛY]žJÙ[XÝYÙYÙ\ÊKˆ˜˜\Ù[[™WÙ\]X[ØÛÜÝØÚXÚ×ÛÛ›HŽ˜˜\ÙWØÚXÚËˆœÙ[XÝYÙ\]X[ØÛÜÝØÚXÚ×ÛÛ›HŽœÙ[ØÚXÚËˆ˜˜\Ù[[™WØÚXÚÍÙˆŽ˜Û\ÜÚYžWØÚXÚÍ
›Ü›X[^™WÙYÙ\ÊTÑWÑQÑTÊKJKˆœÙ[XÝYØÚXÚÍÙˆŽ˜Û\ÜÚYžWØÚXÚÍ
Ù[XÝYÙYÙ\ËJKˆ˜˜\Ù[[™WØÚXÚÍÙÈŽ˜Û\ÜÚYžWØÚXÚÍ
›Ü›X[^™WÙYÙ\ÊTÑWÑQÑTÊKŠKˆœÙ[XÝYØÚXÚÍÙÈŽ˜Û\ÜÚYžWØÚXÚÍ
Ù[XÝYÙYÙ\ËŠKˆœÙ[XÝYØÜ›ÜÜÜ[™HŽ˜Ü›ÜÜÜ[™JÙ[XÝYÙYÙ\ÊKˆBˆÚYÛ˜[Ï^Âˆœ\š]WØœ›ÚÙ[—Ù™X\ÚX›HŽ˜›ÛÛ
[Š™X\ÊOŒ
KˆœÙ[XÝYÙ[Ü˜[šÈŽ˜›ÛÛ
Ù[XÝYÛY]šXÜÖÈœ˜[šÈ—OOLLŠKˆœÙ[XÝYÚÙ\›™[Ùœ™YHŽ˜›ÛÛ
Ù[XÝYÛY]šXÜÖÈšÙ\›™[ØÛÝ[—OOL
Kˆ›ØØ[Ù›ÛÜœ×Ü™\Ù\™YŽ˜›ÛÛ
Ù[XÝYÛY]šXÜÖÈœÚ[™ÛWÙ›ÛÜˆ—OMˆ[™Ù[XÝYÛY]šXÜÖÈœZ\—Ù›ÛÜˆ—ON
KˆœZ\—ØÛÛØØÝ\œ™[˜ÙWÜ™\Ù\™YŽ˜›ÛÛ
Ù[XÝYÛY]šXÜÖÈ›X^ÜZ\—ØÛÛØØÝ\œ™[˜ÙH—OLŠKˆ™ÛØ˜[Ù\Ý[˜ÙWÚ[\›Ý™YŽ˜›ÛÛ
Ù[XÝYÛY]šXÜÖÈ™ÛØ˜[ÜÜÚ]]™WÙ›ÛÜˆ—O˜˜\Ù[[™WÛY]šXÜÖÈ™ÛØ˜[ÜÜÚ]]™WÙ›ÛÜˆ—JKˆ˜ÚXÚÍÙ\]X[ØÛÜÝÛ›ÝÝÛÜœÙHŽ˜›ÛÛ
Ù[ØÚXÚÖÈ—VÈ˜[ÛZ[š[XWÛ›Ûž™\›È—OPTÑSS‘WÕÑRQÒÐSÓRS—Ó“Ó–‘T“ÊKˆ˜Ü›ÜÜÜ[™WØ\˜š]˜\žWØÛÜœ™[][Û—ÜÛÛ™YŽ˜›ÛÛ
›ÝÛÝ]ÈœÙ[XÝYØÜ›ÜÜÜ[™H—VÈ™^XÝÛZ[ZX×Ù^\ÝÈ—JKˆBˆ™]\›ˆÂˆœØÚ[XHŽˆžYÙÙ˜\Ú[™Ì\‹LZË\\š]KXœ›ÚÙ[‹]ÜÛÙÞKŒH‹ˆ›YXÚ[šXØ[Ý˜[YŽ•YKˆ›YXÚ[šXØ[Ž›YXÚ[šXØ[ˆ˜˜\Ù[[™WÛY]šXÜÈŽ˜˜\Ù[[™WÛY]šXÜËˆ˜Ø[™Y]WÜÝ[[X\žHŽžÂˆ˜Ø[™Y]WØÛÝ[Ž›[Š›ÝÜÊKˆ™™X\ÚX›WØÛÝ[Ž›[Š™X\ÊKˆ›Y]šX×Ú\ÝÙÜ˜[\ÈŽš\ÝˆœÙ[XÝYŽœÙ[XÝYˆ™™X\ÚX›WØØ[™Y]\ÈŽ™™X\ËˆKˆœÙ[XÝYÙYÙ\ÈŽ–Û\Ý
JH›ÜˆH[ˆÙ[XÝYÙYÙ\×HYˆÙ[XÝYÙYÙ\È\È›Ý›Û™H[ÙH›Û™KˆšÛÝ]ŽšÛÝ]ˆœÚYÛ˜[ÈŽœÚYÛ˜[ËˆÜÛÙÞWÜÜÚ]]™HŽ˜›ÛÛ
ˆÚYÛ˜[ÖÈœ\š]WØœ›ÚÙ[—Ù™X\ÚX›H—H[™ÚYÛ˜[ÖÈœÙ[XÝYÙ[Ü˜[šÈ—H[™ˆÚYÛ˜[ÖÈœÙ[XÝYÚÙ\›™[Ùœ™YH—H[™ÚYÛ˜[ÖÈ›ØØ[Ù›ÛÜœ×Ü™\Ù\™Y—H[™ˆÚYÛ˜[ÖÈœZ\—ØÛÛØØÝ\œ™[˜ÙWÜ™\Ù\™Y—H[™ÚYÛ˜[ÖÈ˜ÚXÚÍÙ\]X[ØÛÜÝÛ›ÝÝÛÜœÙH—Bˆ
Kˆ˜Ø[›ÛšXØ[ÜØÚY[YšX×Ù^XÝ][ÛˆŽ‘˜[ÙKˆœÝXŒNÜŒWÝÝXÚYŽ‘˜[ÙKˆB‚‚™Yˆ[˜ÛÙWÚœÛÛŠÊNˆ™]\›ˆœÛÛ‹™[\ÊËÛÜÚÙ^\ÏUYKÙ\\˜]ÜœÏJ‹‹ŽˆŠK[œÝ\™WØ\ØÚZOQ˜[ÙJB‚‚™YˆXZ[Š
N‚ˆ\X\™Ü\œÙK\™Ý[Y[\œÙ\Š
NÈ\˜YØ\™Ý[Y[
‹K[Ý]‹™\]Z\™YUYJNÈOX\œ\œÙWØ\™ÜÊ
BˆØš\[Š
NÈ˜]ÏJ[˜ÛÙWÚœÛÛŠØšŠJÈ—ˆŠK™[˜ÛÙJ]‹NŠNÈ]
K›Ý]
KÜš]WØž]\Ê˜]ÊBˆš[
[˜ÛÙWÚœÛÛŠÈ›Ý]]Ž˜K›Ý]œÚLMˆŽš\ÚX‹œÚLMŠ˜]ÊKš^YÙ\Ý

K›YXÚ[šXØ[Ý˜[YŽ›Øš–È›YXÚ[šXØ[Ý˜[Y—KœÚYÛ˜[ÈŽ›Øš–ÈœÚYÛ˜[È—KÜÛÙÞWÜÜÚ]]™HŽ›Øš–ÈÜÛÙÞWÜÜÚ]]™H—K˜Ø[™Y]WØÛÝ[Ž›Øš–È˜Ø[™Y]WÜÝ[[X\žH—VÈ˜Ø[™Y]WØÛÝ[—K™™X\ÚX›WØÛÝ[Ž›Øš–È˜Ø[™Y]WÜÝ[[X\žH—VÈ™™X\ÚX›WØÛÝ[—KœÙ[XÝYŽ›Øš–È˜Ø[™Y]WÜÝ[[X\žH—VÈœÙ[XÝY—_JJB‚‚šYˆ×Û˜[YW×ÏOH—×ÛXZ[—×ÈŽˆXZ[Š
B