"""Information-matched symbolic control. Not imported by the native learner.

The config prior and hypothesis language are supplied. Certification is conditional
on that language and complete actually acquired source facts, never universal truth.
"""
from broad_model import CONFIGS,context,PUBLIC,HIDDEN

def route_output(tables,cfg,i):
    first,outer,inject=cfg
    x=list(context(i));x[inject]=tables[first][i]
    return tables[outer][sum(v<<j for j,v in enumerate(x))]

def certify(model):
    if not model.canonical() or any(v!=1 for row in model.source_known for v in row):
        raise ValueError('WSP33_SOURCE_KNOWLEDGE_INCOMPLETE')
    tables=model.effective_tables()
    compatible=tuple(j for j,cfg in enumerate(CONFIGS) if all(route_output(tables,cfg,i)==model.target_labels[i] for i in PUBLIC))
    if not compatible:raise ValueError('WSP33_NO_COMPATIBLE_CONNECTION')
    outputs=tuple(tuple(route_output(tables,CONFIGS[j],i) for i in HIDDEN) for j in compatible)
    certified=tuple(bits[0] if len(set(bits))==1 else None for bits in zip(*outputs))
    # Configs, not distinct truth tables, have equal weight under the frozen prior.
    majority=tuple(int(sum(bits)*2>len(bits)) for bits in zip(*outputs))
    return {'compatible_configs':compatible,'possible_hidden_signatures':tuple(sorted(set(outputs))),
            'certified_predictions':certified,'majority_predictions':majority}
