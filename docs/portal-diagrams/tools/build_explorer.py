#!/usr/bin/env python3
"""Assemble interactive/portal-explorer.html: one self-contained file (no network, no dependencies).
Usage: python3 -I build_explorer.py <docs/portal-diagrams>   (run render.mjs on static/ first)
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from findings import build_findings  # noqa: E402


def svg_text(path):
    s = open(path, encoding='utf-8').read()
    s = re.sub(r'<\?xml[^>]*\?>', '', s)
    s = re.sub(r'<!DOCTYPE[^>]*>', '', s)
    return s.strip()


def safe_json(o):
    return json.dumps(o, separators=(',', ':')).replace('</', '<\\/')


def main():
    root = sys.argv[1]
    m = json.load(open(os.path.join(root, 'model', 'portal-model.json')))
    steps = json.load(open(os.path.join(root, 'model', 'journey-steps.json')))
    st = os.path.join(root, 'static')
    for f in m['flows'].values():  # explorer needs nodes for click details, not edges
        f['graph'] = {'nodes': f['graph']['nodes']}
    m.pop('backgroundDetail', None)
    findings = build_findings(json.load(open(os.path.join(root, 'model', 'portal-model.json'))))
    svgs = {
        'architecture': svg_text(os.path.join(st, '01-architecture.svg')),
        'site': svg_text(os.path.join(st, '02-site-map.svg')),
        'callmap': svg_text(os.path.join(st, '09-flow-dependency-map.svg')),
        'cross': svg_text(os.path.join(st, '11-cross-cutting.svg')),
        'journeys': {os.path.basename(p)[:-4]: svg_text(p) for p in sorted(
            os.path.join(st, x) for x in os.listdir(st) if '-journey-' in x and x.endswith('.svg'))},
        'flows': {x[:-4]: svg_text(os.path.join(st, 'flows', x)) for x in sorted(os.listdir(os.path.join(st, 'flows'))) if x.endswith('.svg')},
    }
    tpl = open(os.path.join(os.path.dirname(__file__), 'explorer_template.html'), encoding='utf-8').read()
    html = tpl.replace('/*__DATA__*/null', safe_json({'model': m, 'steps': steps, 'findings': findings}))
    html = html.replace('/*__SVG__*/null', safe_json(svgs))
    os.makedirs(os.path.join(root, 'interactive'), exist_ok=True)
    out = os.path.join(root, 'interactive', 'portal-explorer.html')
    open(out, 'w', encoding='utf-8').write(html)
    json.dump(findings, open(os.path.join(root, 'model', 'findings.json'), 'w'), indent=1)
    print('wrote', out, '%.1f MB' % (len(html) / 1e6), '| findings', len(findings))


if __name__ == '__main__':
    main()
