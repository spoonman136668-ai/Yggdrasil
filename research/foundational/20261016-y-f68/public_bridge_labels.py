"""Independent public-only 9+9 structural-junction labeler for offline FIT TRAIN.

No hidden tags, future query, future answer, or source labels. The entire
72-edge stream may be used ONLY for training labels, never online decisions.
"""
from collections import defaultdict
def full_public_bridge_edges(public):
 assert len(public)==72 and len(set(tuple(e) for e in public))==72
 graph=defaultdict(list)
 for index,(a,_r,b) in enumerate(public):
  graph[a].append((b,index));graph[b].append((a,index))
 found=[];already=set()
 for root in graph:
  if root in already:continue
  queue=[root];component={root};edges=set()
  while queue:
   u=queue.pop()
   for v,idx in graph[u]:
    edges.add(idx)
    if v not in component:component.add(v);queue.append(v)
  already.update(component)
  if (len(component),len(edges))!=(18,17):continue
  for idx in edges:
   a,_role,b=public[idx]
   reachable={a};pending=[a]
   while pending:
    n=pending.pop()
    for v,j in graph[n]:
     if j==idx:continue
     if v not in reachable:reachable.add(v);pending.append(v)
   if b not in reachable and len(reachable)==9 and len(component-reachable)==9:
    found.append(tuple(public[idx]))
 assert len(found)==2,("PUBLIC_STRUCTURE_9_X_9_BRIDGE_WITNESS_REQUIRED",len(found))
 return frozenset(found)
