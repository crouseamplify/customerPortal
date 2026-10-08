"""Shared Graphviz (DOT) styling so every diagram uses one visual language."""
import html
import re
import textwrap

FONT = 'Helvetica'

# One palette, one meaning per colour. Shape also varies with meaning so the diagrams survive greyscale.
STYLE = {
    'page_public': dict(fill='#E8F5E9', line='#2E7D32'),
    'page_login':  dict(fill='#FFF3E0', line='#E65100'),
    'page_system': dict(fill='#F2F2F2', line='#757575'),
    'flow':        dict(fill='#D1C4E9', line='#4527A0'),
    'subflow':     dict(fill='#EDE7F6', line='#5E35B1'),
    'screen':      dict(fill='#E3F2FD', line='#1565C0'),
    'decision':    dict(fill='#FFF8E1', line='#F9A825'),
    'loop':        dict(fill='#E8EAF6', line='#3949AB'),
    'read':        dict(fill='#E0F2F1', line='#00796B'),
    'write':       dict(fill='#C8E6C9', line='#1B5E20'),
    'action':      dict(fill='#ECEFF1', line='#546E7A'),
    'email':       dict(fill='#FCE4EC', line='#AD1457'),
    'event':       dict(fill='#F8BBD0', line='#880E4F'),
    'lwc':         dict(fill='#E1F5FE', line='#0277BD'),
    'auto':        dict(fill='#FAFAFA', line='#9E9E9E'),
    'person':      dict(fill='#FFFDE7', line='#F57F17'),
    'note':        dict(fill='#FFFFFF', line='#BDBDBD'),
}


def esc(s):
    return html.escape(str(s).replace('\u2192', '->'), quote=False)


def wrap(s, width=26):
    return textwrap.wrap(str(s), width=width, break_long_words=False) or ['']


def hlabel(lines, small=None, header=None, width=26, bold_first=False):
    """HTML-like label: optional tiny header, wrapped body, optional small grey footer lines."""
    parts = []
    if header:
        parts.append('<FONT POINT-SIZE="8" COLOR="#555555">%s</FONT>' % esc(header))
    body = lines if isinstance(lines, list) else wrap(lines, width)
    for i, l in enumerate(body):
        txt = esc(l)
        parts.append('<B>%s</B>' % txt if (bold_first and i == 0) else txt)
    for s in (small or []):
        for l in wrap(s, int(width * 1.15)):
            parts.append('<FONT POINT-SIZE="8" COLOR="#555555">%s</FONT>' % esc(l))
    return '<' + '<BR/>'.join(parts) + '>'


def attrs(**kw):
    out = []
    for k, v in kw.items():
        k = k.rstrip('_')
        if v is None:
            continue
        if isinstance(v, str) and v.startswith('<') and v.endswith('>'):
            out.append('%s=%s' % (k, v))
        else:
            out.append('%s="%s"' % (k, str(v).replace('\\', '\\\\').replace('"', '\\"')))
    return ', '.join(out)


def node(nid, kind, label, shape='box', style='rounded,filled', **extra):
    st = STYLE[kind]
    return '  %s [%s];' % (nid, attrs(label=label, shape=shape, style=style, fillcolor=st['fill'], color=st['line'],
                                       class_='n-' + kind, **extra))


def header(title=None, rankdir='TB', extra=''):
    out = ['digraph G {',
           '  graph [fontname="%s", rankdir=%s, bgcolor="white", pad=0.3, nodesep=0.35, ranksep=0.5, newrank=true, compound=true];' % (FONT, rankdir)]
    if title:
        out.append('  label=%s; labelloc=t; labeljust=l; fontsize=15; fontname="%s";' % (hlabel([title], bold_first=True, width=110), FONT))
    out.append('  node [fontname="%s", fontsize=10, margin="0.12,0.07"];' % FONT)
    out.append('  edge [fontname="%s", fontsize=9, color="#607D8B", arrowsize=0.8];' % FONT)
    if extra:
        out.append(extra)
    return '\n'.join(out) + '\n'


def nid(*parts):
    return re.sub(r'[^A-Za-z0-9_]', '_', '_'.join(str(p) for p in parts))
