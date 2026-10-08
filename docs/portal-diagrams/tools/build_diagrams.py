#!/usr/bin/env python3
"""Generate every DOT diagram + journey step data from model/portal-model.json.
Usage: python3 -I build_diagrams.py <docs/portal-diagrams>
"""
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from dotkit import esc, hlabel, header, node, nid, attrs, STYLE, wrap  # noqa: E402
import diagrams_flows  # noqa: E402

FAULT = 'Customer_Portal_Fault_Path_Screen'


def E(a, b, label=None, **kw):
    kw = dict(kw)
    if label:
        kw['label'] = label
    return '  %s -> %s%s;' % (a, b, (' [%s]' % attrs(**kw)) if kw else '')


def flow_label(m, api):
    f = m['flows'].get(api)
    return f['label'].replace('CALM Portal | ', '').replace('Customer Portal | ', '') if f else api


def page_kind(p):
    if p['themeLayout'] in ('snaThemeLayout',) or p['id'] in ('error',):
        return 'page_system'
    return 'page_login' if p['requiresLogin'] else 'page_public'


# ---------------------------------------------------------------- site map
def site_map(m):
    P = m['pages']
    out = [header('Site map: pages, access and where the flows live', 'LR', 'ranksep=0.9;')]

    def page_node(pid, extra_lines=None):
        p = P[pid]
        rows = ['<TR><TD ALIGN="LEFT"><B>%s</B></TD></TR>' % esc(p['title'] if p['title'] != pid else pid.replace('_', ' ')),
                '<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="8" COLOR="#555555">%s</FONT></TD></TR>' % esc(p['path'])]
        for t in p['tabs']:
            fl = [i['flow'] for i in t['items'] if i['kind'] == 'flow']
            rows.append('<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="9">Tab <B>%s</B>: %s</FONT></TD></TR>' %
                        (esc(t['name']), esc(', '.join(flow_label(m, x) for x in fl) or 'static content')))
        for i in p['items']:
            if i['kind'] == 'flow':
                rows.append('<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="9">Flow: %s</FONT></TD></TR>' % esc(flow_label(m, i['flow'])))
            elif i['kind'] == 'lwc':
                rows.append('<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="9" COLOR="#0277BD">LWC: %s</FONT></TD></TR>' % esc(i['lwc']))
        for x in (extra_lines or []):
            rows.append('<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="8" COLOR="#555555">%s</FONT></TD></TR>' % esc(x))
        lab = '<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="1">%s</TABLE>>' % ''.join(rows)
        k = page_kind(p)
        return node('pg_' + pid, k, lab, shape='box', style='rounded,filled', id='pg_' + pid)

    groups = [
        ('Sign-in', ['login', 'forgotPassword', 'checkPasswordResetEmail', 'register']),
        ('Landing', ['home']),
        ('Open to guests: transactions', ['Submit_a_PO', 'Make_a_Payment', 'Support', 'Shipment_Status', 'School_Scheduling', 'PD_Certificate_of_Completion']),
        ('Open to guests: Help Center', ['Help', 'Knowledge_Detail', 'Search']),
        ('Login required', ['Order_Management', 'Digital_Onboarding', 'Contact_Management', 'Professional_Development']),
        ('In development / test', ['OMP', 'Test']),
        ('System', ['error', 'serviceNotAvailable', 'tooManyRequests']),
    ]
    for gi, (title, ids) in enumerate(groups):
        out.append('  subgraph cluster_%d { label="%s"; style="rounded,dashed"; color="#90A4AE"; fontsize=11;' % (gi, title))
        for pid in ids:
            extra = None
            if pid == 'OMP':
                extra = ['Order Allocation Manager (mock data), no nav link']
            if pid == 'Test':
                extra = ['flow does not exist in org']
            if pid == 'register':
                extra = ['self-registration disabled']
            if pid in ('Shipment_Status', 'School_Scheduling'):
                extra = ['opened from emailed tokenised link']
            out.append('  ' + page_node(pid, extra))
        out.append('  }')
    out.append('  nav [label=<<B>Top navigation</B><BR/><FONT POINT-SIZE="8">personalised: 10 menu variations<BR/>by contact type and account tier</FONT>>, '
               'shape=box, style="filled", fillcolor="#FFFDE7", color="#F57F17", id="nav"];')
    for pid in ('Submit_a_PO', 'Make_a_Payment', 'Order_Management', 'Digital_Onboarding', 'Contact_Management', 'Professional_Development', 'Help'):
        out.append(E('nav', 'pg_' + pid, color='#F57F17', penwidth=1.2))
    out.append(E('login', 'pg_home', 'success'))
    out.append(E('pg_home', 'nav', style='dashed', arrowhead='none'))
    out.append(E('pg_login', 'pg_forgotPassword', 'forgot password', style='dashed'))
    out.append(E('pg_forgotPassword', 'pg_checkPasswordResetEmail', style='dashed'))
    out.append(E('pg_Help', 'pg_Knowledge_Detail', style='dashed'))
    out.append(E('pg_Help', 'pg_Search', style='dashed'))
    out.append('}')
    s = '\n'.join(out).replace('E(', '').replace('login -> pg_home', 'pg_login -> pg_home')
    return s


# ---------------------------------------------------------------- architecture by domain
DOMAINS = [
    ('Sign-in and account access', ['login', 'forgotPassword'], ['Customer_Portal_Request_Username'], ['User', 'Network', 'EmailTemplate']),
    ('Purchase orders', ['Submit_a_PO'], ['Community_PO_Submission_Flow'], None),
    ('Support and Help Center', ['Support', 'Knowledge_Detail'], ['Customer_Portal_Web_Form_to_Case', 'Knowledge_Article_Feedback_Customer_Portal'], None),
    ('Contacts and onboarding checklist', ['Contact_Management'], ['Customer_Portal_Onboarding_Checklist', 'CALM_Portal_Contacts_Display_Contacts'], None),
    ('Digital onboarding', ['Digital_Onboarding'], ['Digital_Onboarding_Page_Key_Dates_and_Rostering_Information'], None),
    ('Orders, shipping addresses, allocations', ['Order_Management'], ['CALM_Portal_View_Shipping_Addresses', 'CALM_Portal_Blanket_Sales_Order_Show_BSO_Details'], None),
    ('Shipment status', ['Shipment_Status'], ['Community_Material_Status_v2'], None),
    ('Professional development', ['Professional_Development', 'PD_Certificate_of_Completion'],
     ['PD_Request_New_Customer_Portal_Input', 'PD_Request_Customer_Portal_Change_Request', 'PD_Requests_Show_Completed_Service_Appointments',
      'PD_Completion_by_Customer_Screen_Flow', 'PD_Completion_Retrieval_Screen_Flow'], None),
    ('Tutor school scheduling', ['School_Scheduling'], ['Tutor_School_Request_Screen'], None),
]


def closure(m, roots):
    seen, st = set(), list(roots)
    while st:
        a = st.pop()
        if a in seen or a not in m['flows']:
            continue
        seen.add(a)
        st.extend(m['flows'][a]['calls'])
    return seen


def domain_data(m, roots):
    fl = closure(m, roots)
    writes, reads = set(), set()
    for a in fl:
        o = m['flows'][a]['objects']
        for k in ('create', 'update', 'delete'):
            writes.update(o[k])
        reads.update(o['read'])
    return fl, sorted(writes), sorted(reads - writes)


def background_by_object(m):
    d = defaultdict(list)
    for key, lst in m['background'].items():
        for b in lst:
            if key == 'Tutor':
                d['Tutor_School_Details__c'].append(b)
            elif b['object']:
                d[b['object']].append(b)
    return d


def architecture(m):
    L = m['objectLabels']
    bg = background_by_object(m)
    out = [header('How it fits together: page → screen flows → data → back-office automation', 'LR', 'ranksep=0.7; nodesep=0.25;')]
    out.append('  people [label=<<B>Visitors and portal users</B><BR/><FONT POINT-SIZE="8">guests, contacts by type and tier,<BR/>Amplify staff (internal trigger)</FONT>>, shape=box, style="rounded,filled", fillcolor="#FFFDE7", color="#F57F17", id="people"];')
    for di, (title, pages, roots, forced) in enumerate(DOMAINS):
        fl, writes, reads = domain_data(m, roots)
        out.append('  subgraph cluster_d%d { label="%s"; style="rounded"; color="#B0BEC5"; fontsize=12; labeljust=l;' % (di, title))
        for pid in pages:
            p = m['pages'][pid]
            out.append('  ' + node('a%d_pg_%s' % (di, pid), page_kind(p), hlabel(p['title'] if p['title'] != pid else pid.replace('_', ' '), small=[p['path']], width=20), id='a%d_pg_%s' % (di, pid)))
        for r in roots:
            out.append('  ' + node('a%d_fl_%s' % (di, r), 'flow', hlabel(flow_label(m, r), header='SCREEN FLOW', width=24), id='a%d_fl_%s' % (di, r)))
        subs = sorted(fl - set(roots) - {FAULT, 'CALM_Portal_Get_User_Details'})
        if subs:
            out.append('  ' + node('a%d_sub' % di, 'subflow', hlabel('%d subflows' % len(subs), small=[flow_label(m, s) for s in subs[:6]] + (['+%d more' % (len(subs) - 6)] if len(subs) > 6 else []), width=26), peripheries=2, id='a%d_sub' % di))
        shown = [o for o in writes if o not in ('PermissionSetAssignment',)]
        if shown:
            out.append('  ' + node('a%d_data' % di, 'write', hlabel('Data written', small=[L.get(o, o) for o in shown], width=26), shape='cylinder', style='filled', id='a%d_data' % di))
        bgs = []
        for o in shown:
            bgs.extend(bg.get(o, []))
        seen, uniq = set(), []
        for b in bgs:
            if b['api'] not in seen:
                seen.add(b['api']); uniq.append(b)
        if uniq:
            tutor = [b for b in uniq if b['api'].lower().startswith('tutor')]
            rest = [b for b in uniq if b not in tutor]
            lines = [b['label'].replace('CALM Portal | ', '').replace('CALM | ', '') for b in rest[:7]]
            if len(rest) > 7:
                lines.append('+%d more' % (len(rest) - 7))
            if tutor:
                lines.append('Tutor program: %d record-triggered flows' % len(tutor))
            out.append('  ' + node('a%d_bg' % di, 'auto', hlabel('Back-office automation', small=lines, width=30), style='rounded,filled,dashed', id='a%d_bg' % di))
        out.append('  }')
        for pid in pages:
            out.append(E('people', 'a%d_pg_%s' % (di, pid)))
        pg0 = 'a%d_pg_%s' % (di, pages[0])
        for pid in pages:
            for r in roots:
                placed = {x['page'] for x in m['flows'][r]['placedOn']}
                if pid in placed:
                    out.append(E('a%d_pg_%s' % (di, pid), 'a%d_fl_%s' % (di, r)))
        if subs:
            for r in roots:
                if set(m['flows'][r]['calls']) & set(subs) or any(set(m['flows'][c]['calls']) & set(subs) for c in closure(m, [r]) if c in m['flows']):
                    out.append(E('a%d_fl_%s' % (di, r), 'a%d_sub' % di))
        last = 'a%d_sub' % di if subs else None
        tgt = 'a%d_data' % di
        if shown:
            for r in roots:
                if m['flows'][r]['objects']['create'] or m['flows'][r]['objects']['update'] or last is None:
                    out.append(E('a%d_fl_%s' % (di, r), tgt))
            if last:
                out.append(E(last, tgt))
        if uniq and shown:
            out.append(E(tgt, 'a%d_bg' % di, 'triggers', style='dashed'))
    out.append('}')
    return '\n'.join(out)


# ---------------------------------------------------------------- flow call map
def call_map(m):
    out = [header('Flow dependency map: which flows call which', 'LR', 'ranksep=0.8;')]
    pages_with = defaultdict(list)
    for a, f in m['flows'].items():
        for p in f['placedOn']:
            pages_with[p['page']].append(a)
    for pid in sorted(pages_with):
        p = m['pages'][pid]
        out.append('  ' + node('pg_' + pid, page_kind(p), hlabel(p['title'] if p['title'] != pid else pid.replace('_', ' '), small=[p['path']], width=20), id='pg_' + pid))
    for a, f in m['flows'].items():
        if a == FAULT:
            continue
        kind = 'flow' if f['role'] == 'page' else 'subflow'
        out.append('  ' + node('fl_' + a, kind, hlabel(f['label'].replace('CALM Portal | ', '').replace('Customer Portal | ', ''), header={'page': 'SCREEN FLOW', 'subflow': 'SUBFLOW', 'legacy': 'LEGACY'}[f['role']], width=26),
                              peripheries=2 if kind == 'subflow' else 1, style='rounded,filled,dashed' if f['role'] == 'legacy' else 'rounded,filled', id='fl_' + a))
    for a, f in m['flows'].items():
        for p in f['placedOn']:
            out.append(E('pg_' + p['page'], 'fl_' + a))
        for c in f['calls']:
            out.append(E('fl_' + a, 'fl_' + c))
    n = len(m['flows'][FAULT]['calledBy'])
    out.append('  note [label="All other flows also route their fault paths\\nto Customer Portal | Fault Path Screen\\n(%d flows). Not drawn." , shape=note, style=filled, fillcolor="#FFFFFF", color="#BDBDBD"];' % n)
    out.append('}')
    return '\n'.join(out)


# ---------------------------------------------------------------- cross-cutting
def cross_cutting(m):
    out = [header('Cross-cutting mechanisms behind every page', 'LR', 'ranksep=0.8;')]
    def box(i, kind, title, lines, **kw):
        out.append('  ' + node(i, kind, hlabel(title, small=lines, width=34, bold_first=True), id=i, **kw))
    box('user', 'person', 'Request arrives', ['guest or authenticated portal user', 'optionally with an emailed token in the URL'])
    box('site', 'page_public', 'LWR site: Amplify Customer Portal', ['route → view → theme layout', 'page access: public, or RequiresLogin', 'Experience Builder audience rules'])
    box('pers', 'person', 'Personalisation', ['rules on Contact.Contact_Type__c and Account.Tier__c', 'choose nav menu (bar + mobile) and home tiles', '10 variations, first matching rule wins'])
    box('track', 'lwc', 'Usage tracking', ['portalTracker LWC in theme layouts', 'flowPortalTracker on flow screens', 'PortalTrackingFlowStart / End actions', 'PortalTrackingController → Portal_Analytics__c'])
    box('flows', 'flow', 'Screen flows (dxp_flow:flow)', ['embedded on pages, some with parameters', 'e.g. Input_pageName, token, recordId'])
    box('ident', 'subflow', 'CALM Portal | Get User Details', ['resolves Contact, Account, child accounts', 'and secondary Affiliations → ID lists', 'every data query is scoped by these IDs'], peripheries=2)
    box('fault', 'subflow', 'Fault Path Screen', ['%d flows route faults here' % len(m['flows'][FAULT]['calledBy']), 'logs via Portal Analytics error action', '"Something went wrong" + Try Again'], peripheries=2)
    box('cmdt', 'read', 'Custom metadata defaults', ['CALM Automation Defaults', 'Customer Portal Automation Default', 'Customer Portal Cases, PD Completion Default'], shape='cylinder', style='filled')
    box('int', 'person', 'Amplify staff (internal trigger)', ['same flows run with an internal-user flag', 'resolve context from the BSO primary contact', 'e.g. invite contact, edit allocation on behalf'])
    box('bg', 'auto', 'Back-office automation', ['record-triggered flows, platform events, scheduled flows', 'user provisioning, emails, cases, status sync'], style='rounded,filled,dashed')
    for a, b in [('user', 'site'), ('site', 'pers'), ('site', 'track'), ('site', 'flows'), ('flows', 'ident'), ('flows', 'fault'), ('flows', 'cmdt'), ('flows', 'bg'), ('int', 'flows'), ('ident', 'cmdt')]:
        out.append(E(a, b))
    out.append(E('pers', 'flows', 'tile / menu links', style='dashed'))
    out.append('}')
    return '\n'.join(out)


# ---------------------------------------------------------------- journeys
def J(title, nodes, edges, clusters=None, rankdir='TB'):
    out = [header(title, rankdir, 'ranksep=0.55;')]
    for cl in (clusters or []):
        out.append('  subgraph cluster_%s { label="%s"; style="rounded"; color="#B0BEC5"; fontsize=11; labeljust=l;' % (cl[0], cl[1]))
        for n in cl[2]:
            out.append('  ' + nodes[n])
        out.append('  }')
    inside = {n for cl in (clusters or []) for n in cl[2]}
    for k, v in nodes.items():
        if k not in inside:
            out.append('  ' + v)
    out.extend(edges)
    out.append('}')
    return '\n'.join(out)


def N(i, kind, title, lines=None, header_=None, **kw):
    shape = kw.pop('shape', 'box')
    style = kw.pop('style', 'rounded,filled')
    return node(i, kind, hlabel(title, small=lines or [], header=header_, width=30), shape=shape, style=style, id=i, **kw)


def journeys(m):
    js = {}
    # 1 -------------------------------------------------------------- sign in
    n = {
        's1': N('s1', 'person', 'Visitor opens the portal', ['no session yet']),
        's2': N('s2', 'page_public', 'Home page (guest variation)', ['Guest tiles: PO, payment, order management', '"Log In" button shown to guests only'], 'PAGE'),
        's3': N('s3', 'page_public', 'Login page', ['login form, employee login link', 'No-Navigation theme layout'], 'PAGE'),
        's4': N('s4', 'page_public', 'Home page (personalised)', ['tiles + nav menu chosen by contact type and tier'], 'PAGE'),
        's5': N('s5', 'page_public', 'Forgot Password page', ['standard reset form'], 'PAGE'),
        's6': N('s6', 'page_public', 'Check your email page', ['reset link arrives by email'], 'PAGE'),
        's7': N('s7', 'flow', 'Request Username (modal)', ['screen: enter email'], 'SCREEN FLOW'),
        's8': N('s8', 'subflow', 'Find Requested Username', ['looks up active User by email', 'is email verified?'], 'SUBFLOW', peripheries=2),
        's9': N('s9', 'email', 'Email to the visitor', ['username', '+ verification reminder if unverified', 'or "no user found" notice'], 'EMAIL', shape='box', style='filled'),
        'b1': N('b1', 'person', 'Sale recorded: BSO saved', ['Blanket Sales Order'], None),
        'b2': N('b2', 'auto', 'Invite Contact to Portal Using BSO Status', ['finds Materials Coordinator from', 'Opportunity contact roles; sets BSO primary contact'], 'BACK-OFFICE', style='rounded,filled,dashed'),
        'b3': N('b3', 'flow', 'Contacts flow: New Contact', ['primary contact adds a person in Contact Management'], 'SCREEN FLOW'),
        'b4': N('b4', 'write', 'Contact saved', ['Contact + Affiliation'], None, shape='cylinder', style='filled'),
        'b5': N('b5', 'auto', 'Create Portal User From Contact', ['creates or reactivates User', 'assigns Customer Portal Access permission set'], 'BACK-OFFICE', style='rounded,filled,dashed'),
        'b6': N('b6', 'person', 'Portal User exists: can log in', [], None),
    }
    e = [E('s1', 's2'), E('s2', 's3', 'Log In'), E('s3', 's4', 'login succeeds'), E('s3', 's5', 'forgot password', style='dashed'),
         E('s5', 's6'), E('s6', 's3', 'reset, then log in', style='dashed'), E('s3', 's7', 'forgot username', style='dashed'),
         E('s7', 's8'), E('s8', 's9'), E('s9', 's3', 'visitor now knows username', style='dashed'),
         E('b1', 'b2'), E('b2', 'b4', 'invites contact'), E('b3', 'b4'), E('b4', 'b5'), E('b5', 'b6'), E('b6', 's3', style='dashed')]
    cl = [('c1', 'Visitor path', ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9']),
          ('c2', 'Where accounts come from (self-registration is switched off)', ['b1', 'b2', 'b3', 'b4', 'b5', 'b6'])]
    steps = [
        ('s1', 'Arrive', 'A visitor opens the portal URL. Nothing requires them to log in to see the home page.'),
        ('s2', 'Guest home page', 'Experience Builder audience rules show the "Guest/Generic" variation: tiles for PO, payment and order management, plus a Log In button that only guests see.'),
        ('s3', 'Login', 'The login page uses the No-Navigation layout. It has the login form and an employee login link. Self-registration is disabled on this site.'),
        ('s4', 'Personalised home', 'After login the same home page re-renders: nav menu and tiles depend on Contact Type(s) and Account Tier.'),
        ('s5', 'Forgot password', 'Standard Experience Cloud reset page.'),
        ('s6', 'Check email', 'Confirmation page; the reset link is sent by email.'),
        ('s7', 'Forgot username', 'A modal on both Login and Forgot Password hosts the Request Username screen flow. The visitor enters their email.'),
        ('s8', 'Find username', 'Subflow reads the User by email. If found and the email is verified it sends the username; if not verified it also sends a verification reminder; if not found it sends a "no user found" email.'),
        ('s9', 'Email', 'The visitor receives the username by email, then logs in.'),
        ('b1', 'Account origin: BSO', 'Users are not self-registered. When a Blanket Sales Order is saved, a record-triggered flow looks for the Materials Coordinator on the Opportunity and invites them.'),
        ('b2', 'Invite', 'Stamps the primary contact on the BSO and invites the contact to the portal.'),
        ('b3', 'Account origin: contacts', 'A primary contact can add colleagues in Contact Management (New Contact subflow: duplicate check, email-domain check, Affiliation record).'),
        ('b4', 'Contact saved', 'The Contact (and Affiliation) now exist.'),
        ('b5', 'User provisioning', 'Record-triggered flow Create Portal User From Contact creates or reactivates the User and assigns the Customer Portal Access permission set.'),
        ('b6', 'Ready', 'The contact can log in. Removing access publishes a Deactivate Customer Portal User platform event, handled by a subscriber flow.'),
    ]
    js['04-journey-sign-in'] = (J('Journey 1: Getting in: sign-in, recovery and where accounts come from', n, e, cl), steps)

    # 2 -------------------------------------------------------------- guest
    n = {
        'g0': N('g0', 'person', 'Guest or any user', ['no login needed for these pages']),
        'p1': N('p1', 'page_public', 'Submit a PO', ['/submit-a-po'], 'PAGE'),
        'f1': N('f1', 'flow', 'PO Submission', ['email, PO number, quote numbers,', 'optional tax-exemption file'], 'SCREEN FLOW'),
        'd1': N('d1', 'write', 'Community Portal Log', ['+ Contact, Task, file links'], None, shape='cylinder', style='filled'),
        'b1': N('b1', 'auto', 'Portal Log → Cases + confirmation', ['creates Cases per quote, links documents'], 'BACK-OFFICE', style='rounded,filled,dashed'),
        'p2': N('p2', 'page_public', 'Make a Payment', ['/make-a-payment', 'static remittance instructions'], 'PAGE'),
        'p3': N('p3', 'page_public', 'Support', ['/support (Webform layout)'], 'PAGE'),
        'f3': N('f3', 'flow', 'Web Form to Case', ['too-fast submit = bot trap'], 'SCREEN FLOW'),
        'f3b': N('f3b', 'subflow', 'Create Case from Webform', ['queue routing, email, attachments'], 'SUBFLOW', peripheries=2),
        'd3': N('d3', 'write', 'Case', ['+ Case Web Form Comment event'], None, shape='cylinder', style='filled'),
        'p4': N('p4', 'page_public', 'Help Center → Knowledge article', ['/help, /article'], 'PAGE'),
        'f4': N('f4', 'flow', 'Article Feedback', ['thumbs up/down + reason'], 'SCREEN FLOW'),
        'd4': N('d4', 'write', 'Article Feedback', [], None, shape='cylinder', style='filled'),
        'p5': N('p5', 'page_public', 'Shipment Status', ['/shipment-status?token=…', 'link sent by email'], 'PAGE'),
        'f5': N('f5', 'flow', 'Material Status v2', ['token → PQ → Opportunity', '+ Integration Data Sync'], 'SCREEN FLOW'),
        'd5': N('d5', 'write', 'Community Portal Log', ['request log'], None, shape='cylinder', style='filled'),
        'p6': N('p6', 'page_public', 'School Scheduling', ['/school-scheduling?token=…'], 'PAGE'),
        'f6': N('f6', 'flow', 'Tutor School Request', ['school info or approval'], 'SCREEN FLOW'),
        'd6': N('d6', 'write', 'Tutor School Details', ['→ Tutor automation (record-triggered)'], None, shape='cylinder', style='filled'),
    }
    e = [E('g0', 'p1'), E('p1', 'f1'), E('f1', 'd1'), E('d1', 'b1', style='dashed'), E('g0', 'p2'), E('g0', 'p3'), E('p3', 'f3'), E('f3', 'f3b'), E('f3b', 'd3'),
         E('g0', 'p4'), E('p4', 'f4'), E('f4', 'd4'), E('g0', 'p5'), E('p5', 'f5'), E('f5', 'd5'), E('g0', 'p6'), E('p6', 'f6'), E('f6', 'd6')]
    steps = [
        ('g0', 'No login', 'These routes do not require login (site is "authenticated with public access enabled"). Guest permissions on the flows and objects were not reviewed here.'),
        ('p1', 'Submit a PO', 'Intro text plus the PO Submission screen flow.'),
        ('f1', 'PO flow', 'Matches the contact by email, or the account by email domain; creates a Contact if needed; user picks quotes by number; optional tax-exemption upload; everything is logged in Community Portal Log.'),
        ('d1', 'Records', 'Community Portal Log, Contact, Task (for the tax form) and file links are written.'),
        ('b1', 'Back-office', 'Record-triggered flows on Community Portal Log create Cases per quote and send a confirmation.'),
        ('p2', 'Make a Payment', 'Static rich-text instructions for wire, ACH and mailed payments. No flow.'),
        ('p3', 'Support form', 'The Support page uses the Webform theme layout.'),
        ('f3', 'Bot trap', 'If the form is submitted implausibly fast the user lands on a Spam Trap screen; otherwise the case subflow runs.'),
        ('f3b', 'Case creation', 'Reads Customer Portal Cases metadata, matches the Contact, routes to Pedagogical, Physical Materials, Digital Materials or Strategic queue, creates or updates the Case, attaches files and emails the requester.'),
        ('d3', 'Case', 'Also publishes a Case Web Form Comment platform event; a subscriber flow adds the feed item to the Case.'),
        ('p4', 'Help Center', 'Help landing, search and Knowledge article viewer with translation links and related articles.'),
        ('f4', 'Feedback', 'Voting is hidden for collections and unpublished articles.'),
        ('d4', 'Feedback record', 'Writes an Article Feedback record.'),
        ('p5', 'Shipment status', 'Opened from an emailed link carrying a token.'),
        ('f5', 'Status lookup', 'Logs the request, finds the Opportunity for the PQ and its Integration Data Sync record, and shows status. Invalid orders and errors get their own screens; errors email support.'),
        ('d5', 'Log', 'Writes and updates a Community Portal Log row for each request.'),
        ('p6', 'School scheduling', 'Opened by school staff from an emailed link carrying a token.'),
        ('f6', 'School form', 'Shows school and district; the school completes information or approves the schedule.'),
        ('d6', 'Tutor record', 'Updating Tutor School Details fires the record-triggered Tutor scheduling automation (about 37 flows).'),
    ]
    js['05-journey-guest-self-service'] = (J('Journey 2: Self-service without logging in', n, e, None, 'LR'), steps)

    # 3 -------------------------------------------------------------- onboarding
    n = {
        'o0': N('o0', 'person', 'Primary Onboarding Contact logs in', ['personalised home: contact management,', 'digital logistics, order management, PD']),
        'o1': N('o1', 'page_login', 'Contact Management', ['/contact-management'], 'PAGE · LOGIN REQUIRED'),
        'o1a': N('o1a', 'flow', 'Onboarding Checklist', ['finds or creates the checklist,', 'counts contact types'], 'SCREEN FLOW'),
        'o1b': N('o1b', 'flow', 'Display Contacts (cmp)', ['add / edit / invite / remove access'], 'SCREEN FLOW'),
        'o1c': N('o1c', 'write', 'Onboarding Checklist, Contact, Affiliation', [], None, shape='cylinder', style='filled'),
        'o2': N('o2', 'page_login', 'Digital Onboarding', ['/digital-onboarding'], 'PAGE · LOGIN REQUIRED'),
        'o2a': N('o2a', 'flow', 'Key Dates and Rostering', ['Technical contact updates the', 'Technical Onboarding Case'], 'SCREEN FLOW'),
        'o2b': N('o2b', 'flow', 'Display Contacts (dop)', ['technical contacts'], 'SCREEN FLOW'),
        'o3': N('o3', 'page_login', 'Order Management', ['/order-management'], 'PAGE · LOGIN REQUIRED'),
        'o3a': N('o3a', 'flow', 'Shipping addresses', ['view, add, edit'], 'SCREEN FLOW'),
        'o3b': N('o3b', 'flow', 'Display Contacts (omp)', ['materials contacts'], 'SCREEN FLOW'),
        'o3c': N('o3c', 'flow', 'Orders: BSO list', ['→ allocation journey'], 'SCREEN FLOW'),
        'o4': N('o4', 'page_login', 'Professional Development', ['/professional-development'], 'PAGE · LOGIN REQUIRED'),
        'o4a': N('o4a', 'flow', 'Request PD, Contacts (pd), Sessions', ['→ PD journey'], 'SCREEN FLOW'),
    }
    e = [E('o0', 'o1'), E('o1', 'o1a', 'on load'), E('o1', 'o1b', 'tab content'), E('o1b', 'o1c'), E('o1a', 'o1c'),
         E('o1', 'o2', 'then'), E('o2', 'o2a', 'Digital Logistics tab'), E('o2', 'o2b', 'Contacts tab'),
         E('o2', 'o3', 'then'), E('o3', 'o3a', 'Shipping addresses tab'), E('o3', 'o3b', 'Contacts tab'), E('o3', 'o3c', 'Orders tab'),
         E('o3', 'o4', 'then'), E('o4', 'o4a')]
    steps = [
        ('o0', 'Starting point', 'The Primary Onboarding Contact sees all four areas (Professional Development only on tier 3, 3T and 3+ accounts).'),
        ('o1', 'Contact Management', 'Login-required page for maintaining who can use the portal.'),
        ('o1a', 'Checklist on load', 'Finds or creates the account\'s Onboarding Checklist and refreshes its contact-type counts.'),
        ('o1b', 'Contacts', 'Display Contacts runs with Input_pageName = cmp. Primary contacts can add contacts (duplicate and email-domain checks, Affiliation), edit roles, invite or remove access.'),
        ('o1c', 'Records', 'Onboarding Checklist, Contact and Affiliation records; removing access publishes a deactivation event.'),
        ('o2', 'Digital Onboarding', 'Two tabs: Digital Logistics and Contacts.'),
        ('o2a', 'Key dates and rostering', 'The Technical contact selects their Technical Onboarding Case, reviews and submits key dates and rostering information; the Case is updated.'),
        ('o2b', 'Technical contacts', 'Same contacts flow with Input_pageName = dop.'),
        ('o3', 'Order Management', 'Three tabs: Shipping addresses, Contacts, Orders.'),
        ('o3a', 'Addresses', 'Lists addresses; adds one if none exist; editing clones an address that is already used by an allocation.'),
        ('o3b', 'Materials contacts', 'Contacts flow with Input_pageName = omp.'),
        ('o3c', 'Orders', 'Lists Blanket Sales Orders and starts the allocation journey (Journey 4).'),
        ('o4', 'Professional Development', 'Four tabs; see Journey 5.'),
        ('o4a', 'PD', 'Request PD, Contacts (pd), Scheduled Sessions, Completed Sessions.'),
    ]
    js['06-journey-onboarding'] = (J('Journey 3: Onboarding a new customer (Primary Onboarding Contact)', n, e, None, 'TB'), steps)

    # 4 -------------------------------------------------------------- allocation
    n = {
        'a0': N('a0', 'page_login', 'Order Management → Orders tab', ['materials contact'], 'PAGE · LOGIN REQUIRED'),
        'a1': N('a1', 'flow', 'Show BSO Details', ['table of Blanket Sales Orders', 'none found → "BSO not found"'], 'SCREEN FLOW'),
        'a2': N('a2', 'subflow', 'Create Order Allocation Request', ['existing requests, or start a new one', 'creates OAR + first allocation'], 'SUBFLOW', peripheries=2),
        'a3': N('a3', 'subflow', 'Edit Order Allocations', ['quantities per product and site', 'save and stay, conflict + over-allocation checks'], 'SUBFLOW', peripheries=2),
        'a4': N('a4', 'subflow', 'Order Allocation Modal', ['per-site delivery logistics'], 'SUBFLOW', peripheries=2),
        'a4a': N('a4a', 'subflow', 'Edit Shipping Address', ['required fields missing?', 'address in use → clone and repoint'], 'SUBFLOW', peripheries=2),
        'a5': N('a5', 'decision', 'Materials contact?', [], None, shape='diamond', style='filled'),
        'a5b': N('a5b', 'screen', 'Not Materials Contact', ['cannot submit'], 'SCREEN'),
        'a6': N('a6', 'subflow', 'Submit an Allocation Request', ['verify and submit → final confirmation', 'thank you (or thank internal support)'], 'SUBFLOW', peripheries=2),
        'a7': N('a7', 'write', 'Order Allocations, OAR, BSO', ['status set to submitted'], None, shape='cylinder', style='filled'),
        'a8': N('a8', 'auto', 'Back-office', ['confirmation email on OAR submission', 'internal support case', 'status sync, reminders'], 'AUTOMATION', style='rounded,filled,dashed'),
        'a9': N('a9', 'lwc', 'Order Allocation Manager (LWC)', ['new component on /omp', 'mock data today; not linked in nav'], 'IN DEVELOPMENT', style='rounded,filled,dashed'),
    }
    e = [E('a0', 'a1'), E('a1', 'a2', 'select a BSO'), E('a2', 'a3', 'edit'), E('a3', 'a4', 'configure site', style='dashed'), E('a4', 'a4a', style='dashed'),
         E('a3', 'a5', 'confirm'), E('a5', 'a5b', 'no'), E('a5', 'a6', 'yes'), E('a6', 'a7'), E('a7', 'a8', style='dashed'), E('a9', 'a1', 'intended replacement', style='dotted')]
    steps = [
        ('a0', 'Orders tab', 'Materials contacts open the Orders tab on Order Management.'),
        ('a1', 'Choose a BSO', 'Shows the account\'s Blanket Sales Orders, scoped by the IDs from Get User Details.'),
        ('a2', 'Allocation request', 'Lists existing Order Allocation Requests for the BSO or starts a new one, creating the OAR and its first Order Allocation. Counts how often it is viewed.'),
        ('a3', 'Edit allocations', 'The main editor: quantities of each BSO product per site. Checks for another user having edited (timestamp), for over-allocation, and lets the user cancel sites or the request.'),
        ('a4', 'Site logistics', 'Per site: verify delivery details, ship-to contact phone, delivery instructions; marks the allocation confirmed.'),
        ('a4a', 'Address fixes', 'If required address fields are missing, the address is edited; if it is already used elsewhere it is cloned and allocations are repointed.'),
        ('a5', 'Who may submit', 'Unconfirmed sites send the user back to the modal. Only a Materials Contact (or Amplify staff) can proceed to submit.'),
        ('a5b', 'Blocked', 'Other contacts see a "Not Materials Contact" screen.'),
        ('a6', 'Submit', 'Verify-and-submit review, then final confirmation. Backing out unlocks the allocations.'),
        ('a7', 'Statuses', 'Order Allocations, the OAR and the BSO are marked submitted.'),
        ('a8', 'Behind the scenes', 'Record-triggered flows email the contact (if they allow it), create an internal support case, keep statuses in sync and send reminders.'),
        ('a9', 'Coming next', 'orderAllocationManager is a rebuilt single-screen experience. It currently uses mock data and is only reachable at /omp.'),
    ]
    js['07-journey-order-allocation'] = (J('Journey 4: Order allocation lifecycle', n, e, None, 'TB'), steps)

    # 5 -------------------------------------------------------------- PD
    n = {
        'q0': N('q0', 'page_login', 'Professional Development', ['/professional-development'], 'PAGE · LOGIN REQUIRED'),
        'q1': N('q1', 'flow', 'Request PD tab', ['find Work Orders and Service Appointments', 'specific or generic request'], 'SCREEN FLOW'),
        'q1a': N('q1a', 'write', 'PD Request + SA / topic connectors', ['updates Onboarding Checklist PD stage'], None, shape='cylinder', style='filled'),
        'q1b': N('q1b', 'auto', 'PD Request automation', ['earliest preferred dates', 'workflow-rule replacement'], 'BACK-OFFICE', style='rounded,filled,dashed'),
        'q2': N('q2', 'flow', 'Scheduled Sessions tab', ['select requested/scheduled SAs,', 'edit, submit change request'], 'SCREEN FLOW'),
        'q3': N('q3', 'flow', 'Completed Sessions tab', ['read-only table'], 'SCREEN FLOW'),
        'q4': N('q4', 'page_public', 'PD Certificate of Completion', ['/pd-certificate (no login)'], 'PAGE'),
        'q4a': N('q4a', 'flow', 'Register for CTLE Certificate', ['session code + details, hashed'], 'SCREEN FLOW'),
        'q4b': N('q4b', 'write', 'PD Completion', [], None, shape='cylinder', style='filled'),
        'q4c': N('q4c', 'flow', 'Retrieve CTLE Certificate', ['re-enter details, hash compared', 'PDF download'], 'SCREEN FLOW'),
    }
    e = [E('q0', 'q1'), E('q1', 'q1a'), E('q1a', 'q1b', style='dashed'), E('q0', 'q2', 'later'), E('q2', 'q1a', 'change request'), E('q0', 'q3', 'after delivery'),
         E('q3', 'q4', 'attendees', style='dashed'), E('q4', 'q4a'), E('q4a', 'q4b'), E('q4', 'q4c'), E('q4c', 'q4b', 'matches', dir='back')]
    steps = [
        ('q0', 'PD page', 'Four tabs: Request PD, Contacts, Scheduled Sessions, Completed Sessions. The page appears in the menu for PD contacts on tier 3, 3T and 3+ accounts.'),
        ('q1', 'Request PD', 'Finds Work Orders and line items in the right status, then the Service Appointments (SAs) available to schedule. Customer picks SAs and fills in details, or files a generic request.'),
        ('q1a', 'Records', 'Creates the PD Request with SA and session-topic connector records, and updates the Onboarding Checklist PD stage.'),
        ('q1b', 'Automation', 'Record-triggered flows on PD Request set earliest preferred dates and replace legacy workflow rules.'),
        ('q2', 'Change a session', 'Select requested or scheduled SAs, edit them and submit; a new PD Request records the change.'),
        ('q3', 'Completed', 'Table of completed Service Appointments for the account.'),
        ('q4', 'Certificates', 'Public page with two tabs for CTLE certificate registration and retrieval.'),
        ('q4a', 'Register', 'Attendee enters a code and personal details. Details are hashed (SHA-256 action plus bcrypt in the browser) before a PD Completion record is created.'),
        ('q4b', 'PD Completion', 'The record used for later retrieval.'),
        ('q4c', 'Retrieve', 'Attendee re-enters details; the browser compares hashes against matching PD Completion records and offers a PDF download.'),
    ]
    js['08-journey-professional-development'] = (J('Journey 5: Professional development and certificates', n, e, None, 'TB'), steps)
    return js


def legend():
    out = [header('Legend', 'LR', 'nodesep=0.25;')]
    items = [('page_public', 'Page open to guests', {}), ('page_login', 'Page that requires login', {}), ('page_system', 'System page', {}),
             ('flow', 'Screen flow placed on a page', {}), ('subflow', 'Subflow (double border)', dict(peripheries=2)),
             ('screen', 'Flow screen', {}), ('decision', 'Decision', dict(shape='diamond', style='filled')),
             ('loop', 'Loop (dashed)', dict(style='rounded,filled,dashed')), ('read', 'Data read', dict(shape='cylinder', style='filled')),
             ('write', 'Data created / updated / deleted', dict(shape='cylinder', style='filled')), ('action', 'Apex or action', dict(style='filled')),
             ('email', 'Email', dict(style='filled')), ('auto', 'Back-office automation (dashed)', dict(style='rounded,filled,dashed')),
             ('person', 'Person / starting point', {}), ('lwc', 'Lightning web component', {})]
    for i, (k, t, kw) in enumerate(items):
        out.append('  ' + node('l%d' % i, k, hlabel(t, width=40), **kw))
    out.append('  note [shape=note, label=<<B>Reading flow diagrams</B><BR/>Bold border = the flow can end here.<BR/>Fault paths are not drawn: nearly every element routes<BR/>faults to the shared Fault Path Screen subflow.<BR/>* = object inferred from the element label.<BR/>Collapsed: assignments, transforms, usage-tracking and<BR/>commit actions.>, style=filled, fillcolor="#FFFFFF", color="#BDBDBD"];')
    out.append('  l0 -> l1 -> l2 -> l3 -> l4 -> l5 -> l6 -> l7 [style=invis];')
    out.append('  l8 -> l9 -> l10 -> l11 -> l12 -> l13 -> l14 -> note [style=invis];')
    out.append('}')
    return '\n'.join(out)


def main():
    root = sys.argv[1]
    m = json.load(open(os.path.join(root, 'model', 'portal-model.json')))
    sd = os.path.join(root, 'static')
    os.makedirs(os.path.join(sd, 'flows'), exist_ok=True)
    for a in m['flows']:
        if a == FAULT:
            continue
        open(os.path.join(sd, 'flows', a + '.dot'), 'w').write(diagrams_flows.flow_dot(m, a))
    open(os.path.join(sd, '02-site-map.dot'), 'w').write(site_map(m))
    open(os.path.join(sd, '01-architecture.dot'), 'w').write(architecture(m))
    open(os.path.join(sd, '09-flow-dependency-map.dot'), 'w').write(call_map(m))
    open(os.path.join(sd, '00-legend.dot'), 'w').write(legend())
    open(os.path.join(sd, '11-cross-cutting.dot'), 'w').write(cross_cutting(m))
    steps = {}
    for name, (dot, st) in journeys(m).items():
        open(os.path.join(sd, name + '.dot'), 'w').write(dot)
        steps[name] = [{'node': a, 'title': b, 'text': c} for a, b, c in st]
    json.dump(steps, open(os.path.join(root, 'model', 'journey-steps.json'), 'w'), indent=1)
    print('dot files written')


if __name__ == '__main__':
    main()
