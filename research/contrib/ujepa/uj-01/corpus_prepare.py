"""DEV conversion of explicitly supplied, digest-pinned source partitions."""
import hashlib
import json
import unicodedata


def convert(raw, sha256, source, split):
    if type(raw) is not bytes or not 0 < len(raw) <= 64 * 1024**2:
        raise ValueError('source size')
    if hashlib.sha256(raw).hexdigest() != sha256:
        raise ValueError('source digest')
    if source not in ('aqua', 'openbookqa') or split not in ('train', 'validation', 'test'):
        raise ValueError('source or partition')
    rows, seen = [], set()
    excluded = 0
    for i, line in enumerate(raw.splitlines()):
        item = json.loads(line)
        if source == 'aqua':
            context = item['question']
            options = item['options']
            labels = list('ABCDE')
            if len(options) != 5 or any(not o.startswith(k + ')') for k, o in zip(labels, options)):
                raise ValueError('AQuA choice format')
            options = [o[2:].strip() for o in options]
            answer = item['correct']
            ident = sha256 + ':' + str(i)
            domain = 'math'
        else:
            context = item['question']['stem']
            choices = item['question']['choices']
            labels = [c['label'] for c in choices]
            if sorted(labels) != list('ABCD'):
                raise ValueError('OpenBookQA choice format')
            options = [c['text'] for c in choices]
            answer = item['answerKey']
            ident = item['id']
            domain = 'language'
        if type(ident) is not str or not ident or ident in seen or answer not in labels:
            raise ValueError('identity or answer')
        seen.add(ident)
        if any(type(s) is not str or not s.strip() for s in [context] + options):
            raise ValueError('empty or invalid signal')
        if len(set(options)) != len(options):
            raise ValueError('duplicate choices')
        if any(len(s.encode('utf-8')) > 256 for s in [context] + options):
            excluded += 1
            continue
        normalized = ' '.join(unicodedata.normalize('NFKC', context).casefold().split())
        group = hashlib.sha256(normalized.encode()).hexdigest()
        rows.append(dict(id=source + ':' + ident, group=group, domain=domain,
                         split=split, context=context, options=options, answer=labels.index(answer)))
    return rows, dict(input=len(seen), eligible=len(rows), excluded_length=excluded)
