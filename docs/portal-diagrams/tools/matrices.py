#!/usr/bin/env python3
"""Persona navigation matrix and flow/object data matrix as standalone SVGs.
Usage: python3 -I matrices.py <docs/portal-diagrams>
"""
import html
import json
import os
import sys
from collections import OrderedDict

F = 'Helvetica, Arial, sans-serif'
NAV_COLS = [('Submit_a_PO', 'Submit a PO'), ('Make_a_Payment', 'Make a payment'), ('Order_Management', 'Order mgmt'),
            ('Digital_Onboarding', 'Digital onboarding'), ('Contact_Management', 'Contact mgmt'),
            ('Professional_Development', 'Prof. dev.'), ('Help', 'Help Center')]


def e(s):
    return html.escape(str(s))


def persona_groups(m):
    """Collapse tier rows that behave identically; keep anomalies visible."""
    def sig(r):
        return json.dumps([r[k] and r[k]['menu'] for k in ('innerBar', 'innerHamburger', 'homeBar', 'homeHamburger')])
    groups = OrderedDict()
    for r in m['personas']:
        key = ('Guest' if r['tier'] == 'GUEST' else '+'.join(r['types']) or 'none', sig(r))
        groups.setdefault(key, []).append(r)
    return [{'who': k[0], 'tiers': [r['tier'] for r in rows], 'row': rows[0]} for k, rows in groups.items()]


def tier_label(g):
    t = set(g['tiers'])
    if g['who'] == 'Guest':
        return 'guest session'
    if t == {'3', '3T', '3+', 'Other'}:
        return 'any tier'
    if t == {'3', '3T', '3+'}:
        return 'tier 3-family'
    return 'tier ' + '/'.join(g['tiers'])


def persona_svg(m):
    groups = persona_groups(m)
    menus = m['menus']
    lw, cw, rh, top = 250, 78, 24, 150
    w = lw + cw * len(NAV_COLS) + 560
    h = top + rh * len(groups) + 90
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="%s" font-size="11">' % (w, h, F),
         '<rect width="100%" height="100%" fill="white"/>',
         '<text x="14" y="26" font-size="15" font-weight="bold">Who sees what: navigation by contact type and account tier</text>',
         '<text x="14" y="46" fill="#555">Contact types: POC Primary Onboarding, TC Technical, MC Materials, PDC Professional Development. '
         'A check means the page is in that persona\'s desktop menu.</text>']
    for i, (_, lab) in enumerate(NAV_COLS):
        x = lw + i * cw + cw / 2
        o.append('<text transform="translate(%d,%d) rotate(-40)" font-weight="bold">%s</text>' % (x, top - 8, e(lab)))
    o.append('<text x="%d" y="%d" font-weight="bold">Menu used (desktop / mobile)</text>' % (lw + cw * len(NAV_COLS) + 12, top - 8))
    y = top
    for gi, g in enumerate(groups):
        r = g['row']
        label = ('No contact type' if g['who'] == 'none' else g['who']) + '  ·  ' + tier_label(g)
        if gi % 2 == 0:
            o.append('<rect x="0" y="%d" width="%d" height="%d" fill="#F6F8FA"/>' % (y, w, rh))
        o.append('<text x="14" y="%d">%s</text>' % (y + 16, e(label)))
        menu = r['innerBar']['menu'] if r['innerBar'] else None
        items = {it['page'] for it in menus.get(menu, [])} if menu else set()
        for i, (pid, _) in enumerate(NAV_COLS):
            if pid in items:
                o.append('<text x="%d" y="%d" fill="#2E7D32" font-size="14" text-anchor="middle">✓</text>' % (lw + i * cw + cw / 2, y + 17))
        mob = r['innerHamburger']['menu'] if r['innerHamburger'] else None
        warn = mob != menu
        txt = (menu or '-') + ((' / ' + str(mob) + ' (differs)') if warn else '')
        o.append('<text x="%d" y="%d" fill="%s">%s</text>' % (lw + cw * len(NAV_COLS) + 12, y + 16, '#C62828' if warn else '#333', e(txt)))
        y += rh
    o.append('<text x="14" y="%d" fill="#555">Red = desktop and mobile menus differ for that persona. Rows come from evaluating the Experience Builder audience rules; tiers that behave identically are merged.</text>' % (y + 28))
    o.append('<text x="14" y="%d" fill="#555">Contacts with no matching contact type, or PD-only contacts outside tier 3, fall through to the Guest/Generic menu.</text>' % (y + 46))
    o.append('</svg>')
    return '\n'.join(o)


def data_svg(m):
    flows = [a for a in m['flows'] if a != 'Customer_Portal_Fault_Path_Screen']
    order = sorted(flows, key=lambda a: ({'page': 0, 'subflow': 1, 'legacy': 2}[m['flows'][a]['role']], a))
    objs = sorted({o for a in flows for k in ('read', 'create', 'update', 'delete') for o in m['flows'][a]['objects'][k]},
                  key=lambda o: (o.endswith('__mdt'), o.endswith('__e'), m['objectLabels'].get(o, o)))
    L = m['objectLabels']
    lw, cw, rh, top = 230, 22, 20, 250
    w = lw + cw * len(order) + 30
    h = top + rh * len(objs) + 70
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="%s" font-size="11">' % (w, h, F),
         '<rect width="100%" height="100%" fill="white"/>',
         '<text x="14" y="26" font-size="15" font-weight="bold">Data map: which flows read and write which objects</text>',
         '<text x="14" y="46" fill="#555">C create (green) · U update (orange) · D delete (red) · R read (teal). Columns: flows placed on pages first (bold), then shared subflows.</text>']
    colors = {'C': '#1B5E20', 'U': '#E65100', 'D': '#B71C1C', 'R': '#00796B'}
    for i, a in enumerate(order):
        x = lw + i * cw + cw / 2
        f = m['flows'][a]
        lab = f['label'].replace('CALM Portal | ', '').replace('Customer Portal | ', '')
        o.append('<text transform="translate(%d,%d) rotate(-60)" fill="%s" font-weight="%s">%s</text>' %
                 (x, top - 6, '#4527A0' if f['role'] == 'page' else '#7E57C2', 'bold' if f['role'] == 'page' else 'normal', e(lab[:46])))
    for ri, ob in enumerate(objs):
        y = top + ri * rh
        if ri % 2 == 0:
            o.append('<rect x="0" y="%d" width="%d" height="%d" fill="#F6F8FA"/>' % (y, w, rh))
        o.append('<text x="14" y="%d">%s</text>' % (y + 14, e(L.get(ob, ob))))
        for i, a in enumerate(order):
            ops = m['flows'][a]['objects']
            letters = [c for k, c in (('create', 'C'), ('update', 'U'), ('delete', 'D'), ('read', 'R')) if ob in ops[k]]
            if letters:
                o.append('<text x="%d" y="%d" fill="%s" font-weight="bold" text-anchor="middle">%s</text>' %
                         (lw + i * cw + cw / 2, y + 14, colors[letters[0]], letters[0]))
    o.append('<text x="14" y="%d" fill="#555">Each cell shows the strongest operation. The interactive explorer lists all operations per cell.</text>' % (top + rh * len(objs) + 30))
    o.append('</svg>')
    return '\n'.join(o)


if __name__ == '__main__':
    root = sys.argv[1]
    m = json.load(open(os.path.join(root, 'model', 'portal-model.json')))
    open(os.path.join(root, 'static', '03-persona-navigation-matrix.svg'), 'w').write(persona_svg(m))
    open(os.path.join(root, 'static', '10-data-matrix.svg'), 'w').write(data_svg(m))
    print('matrices written')
