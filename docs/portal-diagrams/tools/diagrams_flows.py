"""One flowchart per flow, generated from the extracted flow graph."""
from dotkit import esc, hlabel, header, node, nid, attrs, STYLE, wrap

KIND_BY_NODE = {'screen': 'screen', 'decision': 'decision', 'loop': 'loop', 'subflow': 'subflow',
                'read': 'read', 'create': 'write', 'update': 'write', 'delete': 'write', 'action': 'action',
                'wait': 'action', 'error': 'action', 'other': 'action'}
VERB = {'read': 'Get', 'create': 'Create', 'update': 'Update', 'delete': 'Delete'}


def short_comp(c):
    return c.split(':')[-1]


def flow_dot(model, api):
    f = model['flows'][api]
    g = f['graph']
    labels = model['objectLabels']
    out = [header(None, 'TB')]
    out.append('  start [label="Start", shape=circle, style=filled, fillcolor="#37474F", fontcolor="white", color="#37474F", '
               'width=0.5, fixedsize=true, id="%s"];' % nid(api, 'start'))
    has_out = {e['from'] for e in g['edges']}
    has_in = {e['to'] for e in g['edges']} | {g['start']}
    for key, n in list(g['nodes'].items()):
        if n['type'] == 'subflow' and n.get('flow') == 'Customer_Portal_Fault_Path_Screen' and key not in has_in:
            continue  # fault connectors are not drawn; an unconnected fault box is just noise
        k = KIND_BY_NODE.get(n['type'], 'action')
        i = nid(api, key)
        terminal = key not in has_out
        extra = dict(id=i, penwidth=2.6 if terminal else 1.2)
        t = n['type']
        if t == 'screen':
            small = [', '.join(short_comp(c) for c in n.get('components', []) if not c.startswith('flowruntime'))] \
                if n.get('components') else []
            small = [s for s in small if s]
            out.append(node(i, 'screen', hlabel(n['label'], small=small, header='SCREEN', width=28), **extra))
        elif t == 'decision':
            out.append(node(i, 'decision', hlabel(n['label'], width=18), shape='diamond', style='filled', **extra))
        elif t == 'loop':
            out.append(node(i, 'loop', hlabel(n['label'], header='LOOP', width=26), style='rounded,filled,dashed', **extra))
        elif t == 'subflow':
            tgt = model['flows'].get(n['flow'])
            lab = tgt['label'] if tgt else n['flow']
            out.append(node(i, 'subflow', hlabel(lab, header='SUBFLOW', width=26), peripheries=2, **extra))
        elif t in VERB:
            obj = labels.get(n.get('object'), n.get('object') or '(from component)')
            inf = ' *' if n.get('objectInferred') else ''
            kind = 'read' if t == 'read' else ('event' if (n.get('object') or '').endswith('__e') else 'write')
            out.append(node(i, kind, hlabel(n['label'], small=['%s %s%s' % (VERB[t].lower(), obj, inf)], width=26),
                            shape='cylinder', style='filled', **extra))
        elif t == 'action':
            is_mail = n.get('actionType') == 'emailSimple' or 'mail' in (n.get('action') or '').lower()
            out.append(node(i, 'email' if is_mail else 'action',
                            hlabel(n['label'], small=[n.get('action') or ''], header='EMAIL' if is_mail else 'ACTION', width=26),
                            shape='box', style='filled', **extra))
        else:
            out.append(node(i, 'action', hlabel(n['label'], width=26), **extra))
    if g['start'] and g['start'] in g['nodes']:
        out.append('  start -> %s;' % nid(api, g['start']))
    for e in g['edges']:
        if e['from'] not in g['nodes'] or e['to'] not in g['nodes']:
            continue
        if nid(api, e['from']) not in ''.join(out) or nid(api, e['to']) not in ''.join(out):
            continue
        a = dict(label=e['label'] if e['label'] not in ('default',) else 'otherwise')
        if not e['label']:
            a.pop('label')
        if e['label'] == 'each':
            a.update(style='dashed', label='each')
        if e['label'] == 'done':
            a.update(label='done')
        out.append('  %s -> %s [%s];' % (nid(api, e['from']), nid(api, e['to']), attrs(**a)))
    out.append('}')
    return '\n'.join(out)
