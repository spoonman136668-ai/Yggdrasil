"""Independent full numeric scalar-afferent interventions, evaluator only."""
import random
from routed import influence_proxy,traced_forward,LENGTHS,context
from two_row import pack_rows
from structural import forward,threshold

def intervened(rows,x,row):
    values=list(x)
    for g in range(6):
        a=sum(w*v for w,v in zip(rows[2*g],values));b=sum(w*v for w,v in zip(rows[2*g+1],values))
        if row==2*g:a=1-a
        if row==2*g+1:b=1-b
        values.append(threshold(1-a-b))
    value=sum(w*v for w,v in zip(rows[-1],values))
    return 1-value if row==12 else value

def audit():
    rng=random.Random(27001);counts={'circuits':256,'forward_checks':0,'influence_checks':0,'agreement':0,'false_positive':0,'false_negative':0}
    for _ in range(256):
        rows=[]
        for i,n in enumerate(LENGTHS):
            address=rng.randrange(n if i==12 else n+1);rows.append([int(j==address) for j in range(n)])
        masks=pack_rows(rows)
        for x in map(context,range(8)):
            p,values=traced_forward(masks,x,1)
            if p!=forward(rows,x):raise AssertionError('WSP27_TRACE_DIFFERENTIAL')
            counts['forward_checks']+=1;proxy=influence_proxy(masks,values,1)
            for row in range(13):
                actual=int(intervened(rows,x,row)!=p);estimate=proxy[row]
                counts['influence_checks']+=1;counts['agreement']+=actual==estimate
                counts['false_positive']+=estimate==1 and actual==0
                counts['false_negative']+=estimate==0 and actual==1
    return counts
