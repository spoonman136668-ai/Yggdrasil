"""Independent scalar witness for the WSP135 exact source-grammar bank.

Does not import oracle or source; validates vectorized candidate generation.
This knowledge is deliberately oracle privilege, not direct-weight learning.
"""
from itertools import permutations

OPS=("AND","OR","XOR","XNOR")

def op(kind,a,b):
    if kind=="AND":return int(a==1 and b==1)
    if kind=="OR":return int(a==1 or b==1)
    if kind=="XOR":return (a+b)%2
    if kind=="XNOR":return int(a==b)
    raise ValueError("INVALID_SCALAR_OP")

def independent_bank():
    truths=set()
    for perm in permutations((0,1,2,3,4,5)):
        for left_op in OPS:
            for right_op in OPS:
                g1=[]
                g2=[]
                bit4=[]
                bit5=[]
                for x in range(64):
                    b=tuple((x>>i)%2 for i in range(6))
                    g1.append(op(left_op,b[perm[0]],b[perm[1]]))
                    g2.append(op(right_op,b[perm[2]],b[perm[3]]))
                    bit4.append(b[perm[4]])
                    bit5.append(b[perm[5]])
                for outer_op in OPS:
                    for even in (False,True):
                        word=0
                        for x in range(64):
                            z=op(outer_op,g1[x],g2[x])
                            z^=(bit4[x]&bit5[x]) if even else bit4[x]
                            word|=z<<x
                        truths.add(word)
                word=0
                for x in range(64):
                    a,b,c=g1[x],g2[x],bit4[x]
                    maj=int((a+b+c)>=2)
                    word|=(maj^bit5[x])<<x
                truths.add(word)
    return tuple(sorted(truths))
