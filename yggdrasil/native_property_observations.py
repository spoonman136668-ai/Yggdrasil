"""Export ONLY provenance-matching witnessed property/consequence contexts.

This bridges existing native checkpoint types, not sources or architectures.
Hashes validate the original observed event identity/context mapping; they do
not authenticate real-world truth. No source generator or learner is called.
"""
from yggdrasil.native_property_knowledge import NativePropertyKnowledge
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_context_basis import canonical,digest,require,SOURCE_MODE
from yggdrasil.native_prior_hypothesis import input_order
from yggdrasil.public_causal_cells import PublicCausalCells


def observed_property_view(raw,expected_sha256,address,event_keys,*,observations,
                           retained=False,source_mode=SOURCE_MODE):
    require(source_mode==SOURCE_MODE,'PROPERTY_VIEW_ORIGINAL_SOURCE_UNQUALIFIED')
    knowledge=NativePropertyKnowledge.restore(raw,expected_sha256)
    slot=PublicCausalCells._address(address,retained)
    profile=knowledge._relations._profiles[slot]
    require(type(event_keys) is list and 0<len(event_keys)<=4096
            and len(event_keys)==profile.source_records,'PROPERTY_VIEW_EVENT_COUNT')
    entities=[];contexts=[];witnesses={}
    for key in event_keys:
        require(type(key) is list and len(key)==2,'PROPERTY_VIEW_EVENT_KEY')
        entity,action=key;knowledge._entity(entity);PublicCausalCells._bit(action,'ACTION')
        require(knowledge._known[entity]==(1<<knowledge._bits)-1,'PROPERTY_VIEW_MISSING_PROPERTY')
        context=knowledge._values[entity]
        outcome=knowledge.predict_entity(address,entity,action,retained=retained)
        require(type(outcome) is int and outcome in (0,1),'PROPERTY_VIEW_UNIDENTIFIED_CONSEQUENCE')
        entities.append([entity,action,outcome]);contexts.append([context,action,outcome])
        mask=context|(action<<knowledge._bits)
        require(mask not in witnesses or witnesses[mask]==outcome,'PROPERTY_VIEW_CONFLICT')
        witnesses[mask]=outcome
    require(digest(canonical(entities))==knowledge._relation_sources[slot],
            'PROPERTY_VIEW_UNWITNESSED_ENTITY_IDENTITIES')
    require(digest(canonical(contexts))==profile.source_sha256,
            'PROPERTY_VIEW_CONTEXT_GROUNDING_MISMATCH')
    require(type(observations) is int and 8<=observations<=min(2048,len(witnesses))
            and observations%4==0,'PROPERTY_VIEW_EXPOSURE')
    masks=sorted(witnesses,key=input_order)[:observations]
    rows=[[x&((1<<knowledge._bits)-1),x>>knowledge._bits,witnesses[x]] for x in masks]
    view=NativeContextAccumulator(knowledge._bits).stage_update(0,rows,digest(canonical(rows)),max_degree=knowledge._bits+1)
    result=view.checkpoint()
    receipt={'schema':'yggdrasil.ckad.native-property-observed-view.v1',
        'knowledge_checkpoint_sha256':expected_sha256,'source_namespace':knowledge._namespace,
        'observed_entity_rows_sha256':digest(canonical(entities)),
        'observed_context_rows_sha256':digest(canonical(contexts)),
        'source_records':len(entities),'unique_witnessed_contexts':len(witnesses),
        'view_observations':observations,'view_rows_sha256':digest(canonical(rows)),
        'view_checkpoint_sha256':digest(result),'native_stored_properties':knowledge.property_count,
        'source_mode':SOURCE_MODE,'accepted_native':False,'scientific_pass':False}
    return result,receipt
