"""Parse Salesforce Flow metadata XML into a simplified node/edge graph.

Plumbing elements (assignments, transforms, collection processors, tracking and
commit actions) are collapsed so the graph shows only what a person would
recognise: screens, decisions, loops, data operations, subflows and actions.
Fault connectors are not drawn; they are summarised per flow instead.
"""
import glob
import os
import xml.etree.ElementTree as ET

NS = {'m': 'http://soap.sforce.com/2006/04/metadata'}
FAULT_SUBFLOW = 'Customer_Portal_Fault_Path_Screen'
TRACKING_ACTIONS = {'PortalTrackingFlowStart', 'PortalTrackingFlowEnd', 'CommitTransactionAction', 'CommitTransaction'}
COLLAPSED_TYPES = {'assignments', 'transforms', 'collectionProcessors'}
NODE_TYPES = {
    'screens': 'screen', 'decisions': 'decision', 'loops': 'loop', 'subflows': 'subflow',
    'actionCalls': 'action', 'recordLookups': 'read', 'recordCreates': 'create',
    'recordUpdates': 'update', 'recordDeletes': 'delete', 'assignments': 'assign',
    'transforms': 'assign', 'collectionProcessors': 'assign', 'waits': 'wait',
    'customErrors': 'error', 'apexPluginCalls': 'action', 'steps': 'other',
}


def _t(el, tag):
    x = el.find('m:' + tag, NS)
    return x.text if x is not None else None


def _target(el, tag):
    c = el.find('m:' + tag, NS)
    return _t(c, 'targetReference') if c is not None else None


def parse_flow(path):
    root = ET.parse(path).getroot()
    api = os.path.basename(path).replace('.flow-meta.xml', '')
    nodes, edges, faults = {}, [], {'count': 0, 'to_fault_subflow': 0}
    subflow_names = {_t(s, 'name'): _t(s, 'flowName') for s in root.findall('m:subflows', NS)}
    var_types = {_t(v, 'name'): _t(v, 'objectType') for v in root.findall('m:variables', NS) if _t(v, 'objectType')}

    for tag, kind in NODE_TYPES.items():
        for el in root.findall('m:' + tag, NS):
            name = _t(el, 'name')
            n = {'id': name, 'type': kind, 'label': _t(el, 'label') or name, 'tag': tag}
            if kind == 'screen':
                fields = el.findall('m:fields', NS)
                n['components'] = sorted({_t(f, 'extensionName') for f in fields if _t(f, 'extensionName')})
                n['text'] = [_strip_html(_t(f, 'fieldText')) for f in fields
                             if _t(f, 'fieldType') == 'DisplayText' and _t(f, 'fieldText')][:3]
            if kind == 'subflow':
                n['flow'] = _t(el, 'flowName')
            if kind == 'action':
                n['action'] = _t(el, 'actionName')
                n['actionType'] = _t(el, 'actionType')
                if n['action'] in TRACKING_ACTIONS:
                    n['collapse'] = 'tracking'
            if kind in ('read', 'create', 'update', 'delete'):
                n['object'] = _t(el, 'object')
                if not n['object']:
                    # created/updated from a record variable: take its declared sObject type
                    ref = (_t(el, 'inputReference') or '').split('.')[0]
                    n['object'] = var_types.get(ref)
            if tag in COLLAPSED_TYPES:
                n['collapse'] = 'plumbing'
            nodes[name] = n

            # connectors
            for ctag, lbl in (('connector', None), ('defaultConnector', 'default'),
                              ('nextValueConnector', 'each'), ('noMoreValuesConnector', 'done')):
                tgt = _target(el, ctag)
                if tgt:
                    edges.append({'from': name, 'to': tgt, 'label': lbl or ''})
            for rule in el.findall('m:rules', NS):
                tgt = _target(rule, 'connector')
                if tgt:
                    edges.append({'from': name, 'to': tgt, 'label': _t(rule, 'label') or _t(rule, 'name')})
            tgt = _target(el, 'faultConnector')
            if tgt:
                faults['count'] += 1
                dest = nodes.get(tgt)
                if (tgt in subflow_names and subflow_names[tgt] == FAULT_SUBFLOW):
                    faults['to_fault_subflow'] += 1

    start = root.find('m:start', NS)
    start_target = None
    if start is not None:
        start_target = _target(start, 'connector')
        if not start_target:
            sp = start.find('m:scheduledPaths', NS)
            if sp is not None:
                start_target = _target(sp, 'connector')
    meta = {
        'api': api, 'label': _t(root, 'label'), 'processType': _t(root, 'processType'),
        'status': _t(root, 'status'), 'apiVersion': _t(root, 'apiVersion'),
        'description': _t(root, 'description'), 'start': start_target,
        'variables': {
            'input': [_t(v, 'name') for v in root.findall('m:variables', NS) if _t(v, 'isInput') == 'true'],
            'output': [_t(v, 'name') for v in root.findall('m:variables', NS) if _t(v, 'isOutput') == 'true'],
        },
    }
    return meta, nodes, edges, faults


def _strip_html(s):
    import re
    if not s:
        return ''
    s = re.sub(r'<[^>]+>', ' ', s)
    s = s.replace('&nbsp;', ' ').replace('&amp;', '&')
    return re.sub(r'\s+', ' ', s).strip()


def simplify(nodes, edges, start):
    """Contract collapsed nodes; return (kept_nodes, new_edges, new_start)."""
    out_edges = {}
    for e in edges:
        out_edges.setdefault(e['from'], []).append(e)

    def resolve(t, seen=None):
        seen = seen or set()
        results = []
        n = nodes.get(t)
        if n is None:
            return results
        if not n.get('collapse'):
            return [t]
        if t in seen:
            return []
        seen.add(t)
        for e in out_edges.get(t, []):
            results.extend(resolve(e['to'], seen))
        return results

    kept = {k: v for k, v in nodes.items() if not v.get('collapse')}
    new_edges, seen_pairs = [], set()
    for e in edges:
        if e['from'] not in kept:
            continue
        for t in resolve(e['to']):
            key = (e['from'], t, e['label'])
            if key not in seen_pairs:
                seen_pairs.add(key)
                new_edges.append({'from': e['from'], 'to': t, 'label': e['label']})
    starts = resolve(start) if start else []
    return kept, new_edges, (starts[0] if starts else None)


def load_all(flow_dir):
    flows = {}
    for p in sorted(glob.glob(os.path.join(flow_dir, '*.flow-meta.xml'))):
        meta, nodes, edges, faults = parse_flow(p)
        kept, sedges, start = simplify(nodes, edges, meta['start'])
        tracked = any(n.get('collapse') == 'tracking' for n in nodes.values())
        flows[meta['api']] = {'meta': meta, 'nodes': kept, 'edges': sedges, 'start': start,
                              'faults': faults, 'tracked': tracked,
                              'raw_counts': {'nodes': len(nodes), 'collapsed': len(nodes) - len(kept)}}
    return flows
