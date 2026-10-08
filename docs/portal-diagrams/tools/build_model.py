#!/usr/bin/env python3
"""Build model/portal-model.json from retrieved Amplify Customer Portal metadata.

Usage:
    python3 -I build_model.py --src <sfdx-project>/force-app/main/default \
                              --lwc <customerPortal>/force-app/main/default/lwc \
                              --out <docs/portal-diagrams>

--src must contain digitalExperiences/, flows/, navigationMenus/, networks/ (see README for the
sf project retrieve command). Nothing here talks to an org.
"""
import argparse
import itertools
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
import curated  # noqa: E402
import flowgraph  # noqa: E402

SITE = 'Amplify_Customer_Portal1'
NS = {'m': 'http://soap.sforce.com/2006/04/metadata'}
FAULT = flowgraph.FAULT_SUBFLOW
OBJECT_TYPES = ('read', 'create', 'update', 'delete')


def jload(path):
    with open(path) as f:
        return json.load(f)


def walk(node, fn, ctx=None):
    """Depth-first walk over every dict that has a component definition."""
    if isinstance(node, dict):
        if 'definition' in node and isinstance(node['definition'], str):
            fn(node)
        for v in node.values():
            walk(v, fn)
    elif isinstance(node, list):
        for v in node:
            walk(v, fn)


# --------------------------------------------------------------------------- site


def parse_flow_ref(attr):
    """dxp_flow:flow stores flowName as a JSON string; flowArguments as a JSON list string."""
    try:
        name = json.loads(attr.get('flowName', '{}')).get('flowName')
    except ValueError:
        name = None
    try:
        args = {a['name']: a.get('value') for a in json.loads(attr.get('flowArguments', '[]'))}
    except ValueError:
        args = {}
    return name, args


def page_components(content):
    """Return ordered list of top-level interesting components under a view, grouped by tab."""
    body = content['contentBody']['component']
    tabs, loose = [], []

    def collect(n, bucket):
        found = []

        def f(c):
            d = c['definition']
            if d == 'dxp_flow:flow':
                name, args = parse_flow_ref(c.get('attributes', {}))
                found.append({'kind': 'flow', 'flow': name, 'args': args})
            elif d.startswith('c:'):
                found.append({'kind': 'lwc', 'lwc': d[2:], 'attrs': {}})
            elif d in ('community_builder:richTextEditor', 'dxp_base:textBlock'):
                found.append({'kind': 'text'})
            elif d in ('community_login:loginForm', 'community_login:forgotPassword',
                       'community_login:selfRegister', 'community_login:checkEmail',
                       'dxp_search:searchInput', 'dxp_search:searchResults'):
                found.append({'kind': 'standard', 'component': d})
        walk(n, f)
        return found

    tab_comp = []

    def find_tabs(c):
        if c['definition'] == 'dxp_layout:tabs':
            tab_comp.append(c)
    walk(body, find_tabs)
    tab_children_ids = set()
    if tab_comp:
        t = tab_comp[0]
        cfg = json.loads(t['attributes'].get('tabsetConfig', '{}'))
        names = [x['tabName'] for x in cfg.get('tabs', [])]
        kids = [c for c in t.get('children', [])]
        # Child order matches the order of the tabsetConfig list in every view inspected.
        ordered_names = names
        for i, kid in enumerate(kids):
            label = ordered_names[i] if i < len(ordered_names) else 'Tab %d' % (i + 1)
            tabs.append({'name': label, 'items': collect(kid, None)})
            walk(kid, lambda c: tab_children_ids.add(id(c)))
    # non-tab content
    non_tab = []
    for item in collect(body, None):
        non_tab.append(item)
    if tabs:
        tabbed = {(i.get('flow') or i.get('lwc') or i.get('component'), i['kind']) for t in tabs for i in t['items']}
        non_tab = [i for i in non_tab if (i.get('flow') or i.get('lwc') or i.get('component'), i['kind']) not in tabbed]
    return tabs, non_tab


def build_pages(site_dir):
    routes = {}
    for f in os.listdir(os.path.join(site_dir, 'sfdc_cms__route')):
        c = jload(os.path.join(site_dir, 'sfdc_cms__route', f, 'content.json'))['contentBody']
        routes[c['activeViewId']] = {
            'routeApi': f, 'routeType': c.get('routeType'), 'urlPrefix': c.get('urlPrefix', ''),
            'pageAccess': c.get('pageAccess'),
        }
    theme = jload(os.path.join(site_dir, 'sfdc_cms__theme', os.listdir(os.path.join(site_dir, 'sfdc_cms__theme'))[0], 'content.json'))['contentBody']
    layout_by_type = {l['layoutType']: l['layoutId'] for l in theme['layouts']}
    pages = {}
    for view in sorted(os.listdir(os.path.join(site_dir, 'sfdc_cms__view'))):
        c = jload(os.path.join(site_dir, 'sfdc_cms__view', view, 'content.json'))
        r = routes.get(view, {})
        tabs, loose = page_components(c)
        access = r.get('pageAccess')
        pages[view] = {
            'id': view,
            'title': c.get('title') or view,
            'route': r.get('routeApi'),
            'path': '/' + (r.get('urlPrefix') or ''),
            'requiresLogin': access == 'RequiresLogin',
            'themeLayout': layout_by_type.get(c['contentBody'].get('themeLayoutType'), c['contentBody'].get('themeLayoutType')),
            'tabs': tabs,
            'items': loose,
            'purpose': curated.PAGE_PURPOSE.get(view, ''),
        }
    return pages


# ------------------------------------------------------------------------ navigation


def build_nav(nav_dir, pages):
    by_prefix = {p['path'].strip('/').lower(): pid for pid, p in pages.items()}
    by_prefix.update(curated.NAV_URL_OVERRIDES)
    menus = {}
    for f in sorted(os.listdir(nav_dir)):
        if not f.endswith('.xml'):
            continue
        name = f.split('.')[0]
        root = ET.parse(os.path.join(nav_dir, f)).getroot()
        items = []
        for it in root.findall('.//m:navigationMenuItem', NS):
            def t(tag):
                x = it.find('m:' + tag, NS)
                return x.text if x is not None else None
            typ, target = t('type'), t('target')
            page = None
            if typ == 'InternalLink' and target:
                page = by_prefix.get(target.strip('/').lower())
            items.append({'label': t('label'), 'type': typ, 'target': target, 'page': page, 'position': int(t('position') or 0)})
        menus[name] = items
    return menus


# ----------------------------------------------------------------- personalization


def collect_ops(site_dir):
    """Return {(file, targetDefinition): [variation dict]} with resolved rules, in rule order."""
    out = []
    for kind, folder in (('view', 'sfdc_cms__view'), ('themeLayout', 'sfdc_cms__themeLayout')):
        for name in sorted(os.listdir(os.path.join(site_dir, folder))):
            body = jload(os.path.join(site_dir, folder, name, 'content.json'))['contentBody']
            ops = body.get('contentOperations', {}).get('operations', [])
            if not ops:
                continue
            idx = {}

            def index(n):
                if isinstance(n, dict):
                    if 'id' in n and 'definition' in n:
                        idx[n['id']] = n
                    for v in n.values():
                        index(v)
                elif isinstance(n, list):
                    for v in n:
                        index(v)
            index(body.get('component', {}))
            for op in ops:
                tgt = idx.get(op['targetId'], {})
                variations = []
                for r in op.get('ruleToVariationList', []):
                    v = idx.get(r['variationId'], {})
                    menu = None
                    tiles = []

                    def scan(c):
                        nonlocal menu
                        a = c.get('attributes', {})
                        if a.get('navigationMenuEditor') and not menu:
                            menu = a['navigationMenuEditor']
                        if c['definition'] == 'dxp_base:button' and a.get('text'):
                            try:
                                page = json.loads(a.get('url', '{}'))['linkInfo']['pageReference']['attributes']['name']
                            except (ValueError, KeyError, TypeError):
                                page = None
                            tiles.append({'label': a['text'], 'route': page})
                    walk(v, scan)
                    variations.append({
                        'title': v.get('title'), 'menu': menu, 'tiles': tiles,
                        'formula': r['rule'].get('customFormula') or r['rule'].get('criteriaType'),
                        'criteria': {str(c['criterionNumber']): c for c in r['rule'].get('expressionCriteria', [])},
                    })
                out.append({'source': name, 'kind': kind, 'target': tgt.get('definition', '?'), 'variations': variations})
    return out


def eval_rule(formula, criteria, ctx):
    """ctx: {'types': set, 'tier': str, 'guest': bool}."""
    results = {}
    for num, c in criteria.items():
        res, op, val = c['resource'], c['operator'], c['value']
        if res.endswith('Contact_Type__c'):
            actual = ctx['types']
            ok = (val in actual) if op == 'Contains' else (val not in actual) if op == 'NotContains' else None
        elif res.endswith('Tier__c'):
            ok = (ctx['tier'] == val) if op == 'Equal' else (ctx['tier'] != val) if op == 'NotEqual' else None
        elif res.endswith('isGuest'):
            ok = ctx['guest'] if (op == 'Equal' and str(val).lower() == 'true') else None
        else:
            ok = None
        if ok is None:
            raise ValueError('unsupported criterion %r' % c)
        results[num] = ok
    if formula == 'AllCriteriaMatch':
        return all(results.values())
    if formula == 'AnyCriteriaMatch':
        return any(results.values())
    if not re.fullmatch(r'[0-9 ()ANDOR]+', formula):
        raise ValueError('unsupported formula %r' % formula)
    expr = re.sub(r'\d+', lambda m: str(results[m.group(0)]), formula).replace('AND', ' and ').replace('OR', ' or ')
    return bool(eval(expr, {'__builtins__': {}}, {}))  # formula is digits/AND/OR/parens only


def first_match(variations, ctx):
    for v in variations:
        if eval_rule(v['formula'], v['criteria'], ctx):
            return v
    return None


def build_personas(ops, menus_known):
    def pick(source, target_suffix):
        for o in ops:
            if o['source'] == source and o['target'].endswith(target_suffix):
                return o['variations']
        return []
    slots = {
        'innerBar': pick('scopedHeaderAndFooter', 'customizableNavigationBarContainer'),
        'innerHamburger': pick('scopedHeaderAndFooter', 'customizableNavigationHamburgerMenuContainer'),
        'homeBar': pick('Home_Page', 'customizableNavigationBarContainer'),
        'homeHamburger': pick('Home_Page', 'customizableNavigationHamburgerMenuContainer'),
    }
    home_tiles = []
    for o in ops:
        if o['source'] == 'home' and o['target'].endswith('columns'):
            home_tiles.append(o['variations'])

    codes = [c for c, _ in curated.CONTACT_TYPES]
    full = dict(curated.CONTACT_TYPES)
    tiers = ['3', '3T', '3+', 'Other']
    rows = []
    for tier in tiers + ['GUEST']:
        for n in range(0, len(codes) + 1):
            for combo in itertools.combinations(codes, n):
                if tier == 'GUEST' and combo:
                    continue
                ctx = {'types': {full[c] for c in combo}, 'tier': 'x' if tier in ('Other', 'GUEST') else tier, 'guest': tier == 'GUEST'}
                row = {'types': list(combo), 'tier': tier}
                for k, vs in slots.items():
                    m = first_match(vs, ctx)
                    row[k] = {'title': m['title'], 'menu': m['menu']} if m else None
                tiles = {}
                for vs in home_tiles:
                    m = first_match(vs, ctx)
                    if m:
                        for t in m['tiles']:
                            tiles[(t['label'], t['route'])] = 1
                row['homeTiles'] = [{'label': l, 'route': r} for (l, r) in tiles]
                rows.append(row)
    return rows


def persona_findings(rows):
    f = []
    for r in rows:
        who = ('Guest' if r['tier'] == 'GUEST' else '+'.join(r['types']) or 'No contact type') + \
              ('' if r['tier'] == 'GUEST' else ' / tier ' + r['tier'])
        if r['tier'] != 'GUEST' and r['innerBar'] is None:
            f.append(('NO_MENU', who))
        if r['innerBar'] and r['innerHamburger'] and r['innerBar']['menu'] != r['innerHamburger']['menu']:
            f.append(('BAR_VS_MOBILE_INNER', who, r['innerBar']['menu'], r['innerHamburger']['menu']))
        if r['homeBar'] and r['homeHamburger'] and r['homeBar']['menu'] != r['homeHamburger']['menu']:
            f.append(('BAR_VS_MOBILE_HOME', who, r['homeBar']['menu'], r['homeHamburger']['menu']))
        if r['innerBar'] and r['homeBar'] and r['innerBar']['menu'] != r['homeBar']['menu']:
            f.append(('INNER_VS_HOME', who, r['innerBar']['menu'], r['homeBar']['menu']))
    return f


# --------------------------------------------------------------------------- flows


def build_flows(flow_dir, pages, lwc_inv):
    flows = flowgraph.load_all(flow_dir)
    for api, f in flows.items():
        for n in f['nodes'].values():
            ov = curated.OBJECT_OVERRIDES.get((api, n['label']))
            if ov and not n.get('object'):
                n['object'], n['objectInferred'] = ov, True
    info = {}
    for api, f in flows.items():
        objs = {k: set() for k in OBJECT_TYPES}
        apex, lwc, subflows, screens, emails = set(), set(), [], [], 0
        for n in f['nodes'].values():
            if n['type'] in OBJECT_TYPES and n.get('object'):
                objs[n['type']].add(n['object'])
            if n['type'] == 'action':
                if n.get('actionType') == 'emailSimple':
                    emails += 1
                elif n.get('action'):
                    apex.add(n['action'])
            if n['type'] == 'subflow' and n.get('flow') and n['flow'] != FAULT:
                subflows.append(n['flow'])
            if n['type'] == 'screen':
                lwc.update(c for c in n.get('components', []))
                screens.append(n['label'])
        info[api] = {
            'api': api, 'label': f['meta']['label'], 'processType': f['meta']['processType'],
            'status': f['meta']['status'], 'apiVersion': f['meta']['apiVersion'],
            'purpose': curated.FLOW_PURPOSE.get(api) or curated.BACKGROUND_PURPOSE.get(api, ''),
            'objects': {k: sorted(v) for k, v in objs.items()},
            'apex': sorted(apex), 'components': sorted(lwc), 'emailActions': emails,
            'calls': sorted(set(subflows)),
            'usesFaultPath': any(n.get('flow') == FAULT for n in f['nodes'].values() if n['type'] == 'subflow'),
            'tracked': f['tracked'], 'faults': f['faults'], 'screens': screens,
            'inputs': f['meta']['variables']['input'], 'outputs': f['meta']['variables']['output'],
            'graph': {'nodes': f['nodes'], 'edges': f['edges'], 'start': f['start']},
            'placedOn': [], 'calledBy': [], 'launchedByLwc': curated.LWC_LAUNCHED_FLOWS.get(api),
        }
    for pid, p in pages.items():
        for loc, items in [('page', p['items'])] + [(t['name'], t['items']) for t in p['tabs']]:
            for it in items:
                if it['kind'] == 'flow' and it.get('flow') in info:
                    info[it['flow']]['placedOn'].append({'page': pid, 'location': loc, 'args': it.get('args', {})})
    # reachability from pages / LWCs, following subflow calls and the implicit fault subflow
    roots = [a for a, f in info.items() if f['placedOn'] or f['launchedByLwc']]
    reach, stack = set(), list(roots)
    while stack:
        a = stack.pop()
        if a in reach or a not in info:
            continue
        reach.add(a)
        stack.extend(info[a]['calls'])
        if info[a]['usesFaultPath']:
            stack.append(FAULT)
    portal, background = {}, {}
    for a, f in info.items():
        if a in reach:
            f['role'] = 'page' if f['placedOn'] else ('legacy' if f['launchedByLwc'] and not any(a in info[x]['calls'] for x in reach if x != a) else 'subflow')
            portal[a] = f
        else:
            f['role'] = 'background'
            background[a] = f
    for a, f in portal.items():
        for c in f['calls']:
            if c in portal:
                portal[c]['calledBy'].append(a)
        if f['usesFaultPath'] and FAULT in portal and a != FAULT:
            portal[FAULT]['calledBy'].append(a)
    return portal, background


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--lwc', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    site_dir = os.path.join(a.src, 'digitalExperiences', 'site', SITE)
    pages = build_pages(site_dir)
    menus = build_nav(os.path.join(a.src, 'navigationMenus'), pages)
    flows, background_detail = build_flows(os.path.join(a.src, 'flows'), pages, {})
    ops = collect_ops(site_dir)
    personas = build_personas(ops, menus)
    pfind = persona_findings(personas)

    # menus actually used by the portal theme layouts
    used_menus = sorted({r[k]['menu'] for r in personas for k in ('innerBar', 'innerHamburger', 'homeBar', 'homeHamburger') if r[k] and r[k]['menu']})

    # which pages appear in which menus
    page_menus = defaultdict(set)
    for m in used_menus:
        for it in menus.get(m, []):
            if it['page']:
                page_menus[it['page']].add(m)
    for pid, p in pages.items():
        p['inMenus'] = sorted(page_menus.get(pid, []))

    # data-driven LWC inventory from the repo
    lwc_inv = {}
    for d in sorted(os.listdir(a.lwc)):
        p = os.path.join(a.lwc, d)
        if not os.path.isdir(p):
            continue
        js = open(os.path.join(p, d + '.js')).read() if os.path.exists(os.path.join(p, d + '.js')) else ''
        meta = open(os.path.join(p, d + '.js-meta.xml')).read() if os.path.exists(os.path.join(p, d + '.js-meta.xml')) else ''
        lwc_inv[d] = {
            'targets': re.findall(r'<target>([^<]+)</target>', meta),
            'apex': sorted(set(re.findall(r"@salesforce/apex/(\w+\.\w+)", js))),
            'flows': sorted(set(re.findall(r"flow-api-name=['\"](\w+)['\"]", open(os.path.join(p, d + '.html')).read() if os.path.exists(os.path.join(p, d + '.html')) else ''))),
            'mockData': 'Mock Data' in js,
        }

    bg = jload(os.path.join(a.out, 'model', 'active_flows_snapshot.json'))['flows']
    portal_flow_names = set(flows)
    background = defaultdict(list)
    for r in bg:
        if r['TriggerType'] and r['ApiName'] not in portal_flow_names:
            obj = curated.BG_TRIGGER_TO_OBJECT.get(r['TriggerObjectOrEventLabel'])
            group = r['TriggerObjectOrEventLabel']
            tutor = r['ApiName'].lower().startswith('tutor')
            background['Tutor program (%d flows)' % 0 if False else ('Tutor' if tutor else group)].append(
                {'api': r['ApiName'], 'label': r['Label'], 'trigger': r['TriggerType'], 'object': obj or None, 'triggerLabel': group})

    model = {
        'site': {
            'name': 'Amplify Customer Portal', 'bundle': SITE, 'type': 'LWR (Experience Cloud)',
            'urlPathPrefix': 'customerportallwr', 'authentication': 'AUTHENTICATED_WITH_PUBLIC_ACCESS_ENABLED',
            'selfRegistration': False, 'sourceOrg': 'AmplifyDev1', 'generated': '2026-10-08',
        },
        'pages': pages, 'flows': flows, 'backgroundDetail': background_detail, 'menus': {m: menus[m] for m in used_menus}, 'usedMenus': used_menus,
        'personas': personas, 'personaFindings': pfind,
        'lwc': lwc_inv, 'background': background,
        'objectLabels': curated.OBJECT_LABEL,
        'contactTypes': curated.CONTACT_TYPES, 'pageNameToRole': curated.PAGE_NAME_TO_ROLE,
    }
    os.makedirs(os.path.join(a.out, 'model'), exist_ok=True)
    with open(os.path.join(a.out, 'model', 'portal-model.json'), 'w') as f:
        json.dump(model, f, indent=1, default=lambda o: sorted(o) if isinstance(o, set) else str(o))
    print('pages', len(pages), 'flows', len(flows), 'menus', len(used_menus), 'persona rows', len(personas), 'findings', len(pfind))


if __name__ == '__main__':
    main()
