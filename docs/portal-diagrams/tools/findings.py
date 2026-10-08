"""Observations made while extracting the model. Computed where possible, evidence cited for each."""


def build_findings(m):
    F = []

    def add(sev, title, detail, evidence):
        F.append({'severity': sev, 'title': title, 'detail': detail, 'evidence': evidence})

    # Computed from page/flow/persona data
    for pid, p in m['pages'].items():
        for items in [p['items']] + [t['items'] for t in p['tabs']]:
            for it in items:
                if it['kind'] == 'flow' and it.get('flow') and it['flow'] not in m['flows']:
                    add('Fix', 'Page references a flow that is not in the org',
                        'Page "%s" (%s) embeds flow %s. It was not found among active flows in AmplifyDev1, so the page will show a flow error.' % (p['title'], p['path'], it['flow']),
                        'View %s content.json; FlowDefinitionView query returned no row.' % pid)

    for menu, items in m['menus'].items():
        for it in items:
            if it['label'] and 'payment' in it['label'].lower() and it['page'] and it['page'] != 'Make_a_Payment':
                add('Fix', '"Make a payment" menu link points at the wrong page',
                    'Navigation menu %s labels an item "%s" but links to %s (the Check Password Reset Email page). '
                    'Primary Onboarding contacts on tier 3, 3T and 3+ accounts will not reach the payment page from the menu.' % (menu, it['label'], it['target']),
                    'navigationMenus/%s' % menu)

    nomob = [r for r in m['personas'] if r['tier'] not in ('GUEST',) and r['innerBar'] and not r['innerHamburger']]
    if nomob:
        add('Fix', 'Logged-in contacts with no contact type get no mobile menu on inner pages',
            'In the inner-page theme layout, the mobile (hamburger) menu rule for "Guest/Generic" has criterion 4 set to "Contains Professional Development Contact" '
            'where its desktop counterpart says "NotContains". %d persona/tier combinations resolve to no mobile menu.' % len(nomob),
            'themeLayout scopedHeaderAndFooter, hamburger container rule variation "Guest/Generic"')
    for f in m['personaFindings']:
        if f[0] == 'BAR_VS_MOBILE_HOME':
            add('Review', 'Home page: mobile menu differs from desktop menu for Technical + PD contacts',
                'Tier 3-family contacts with Technical + Professional Development types get %s on desktop but %s on the mobile menu, which adds Orders and shipping.' % (f[2], f[3]),
                'themeLayout Home_Page hamburger container variation "TC + PD (3T)"')
            break
    for f in m['personaFindings']:
        if f[0] == 'BAR_VS_MOBILE_INNER' and f[2] and f[3] and 'Technical_Materials' in f[2]:
            add('Review', 'Tier 3+ with Technical + Materials + PD contact types loses the Professional Development link on inner pages',
                'The "TC + MC + PD (3T)" desktop rule lists tier "3T" twice and omits "3+", so tier 3+ falls through to %s. The mobile menu and home page do include it.' % f[2],
                'themeLayout scopedHeaderAndFooter, bar container variation "TC + MC + PD (3T)", criteria 6 and 7')
            break
    add('Review', 'Typo in a personalisation rule',
        'One audience criterion on the outer navigation wrapper reads "Technical Conact". It can never match.',
        'themeLayout scopedHeaderAndFooter, navigation menu variation "TC + PD (3T)", criterion 1')
    add('Info', 'Professional Development contacts outside tier 3 see the generic menu',
        'A contact whose only type is Professional Development, on an account that is not tier 3, 3T or 3+, has no Professional Development link in the menu or home tiles. This may be intended.',
        'persona matrix')

    # Flow health
    leaks = []
    for a, f in m['flows'].items():
        fl = f['faults']
        if fl['count'] > fl['to_fault_subflow']:
            leaks.append('%s (%d of %d)' % (f['label'], fl['count'] - fl['to_fault_subflow'], fl['count']))
    total = sum(f['faults']['count'] for f in m['flows'].values())
    routed = sum(f['faults']['to_fault_subflow'] for f in m['flows'].values())
    add('Info', 'Fault handling is mostly centralised',
        '%d of %d fault connectors route to the shared Fault Path Screen subflow. Exceptions: %s.' % (routed, total, '; '.join(leaks)),
        'flow XML faultConnector targets')

    unused = [k for k, v in m['lwc'].items() if k.startswith('orderStatus')]
    add('Info', 'Order status LWCs are not used by any flow on this site',
        'The repo contains %s, but none of the 29 portal flows place them on a screen. The Shipment Status page uses Community_Material_Status_v2, which has no custom components. They may serve another site or be legacy.' % ', '.join(unused),
        'flow XML screen extensionName values')
    add('Info', 'Order Allocation Manager LWC is in development',
        'orderAllocationManager is placed on /omp, uses built-in mock data ("replaced by Apex in Phase 2"), and is in no navigation menu. The route has no login requirement.',
        'view OMP; lwc/orderAllocationManager/orderAllocationManager.js')
    add('Info', 'Legacy allocation components remain',
        'allocationsTable_v2, createOAModal and configureModal are still used inside flows; CALM_Create_New_Order_Allocation is only launched by createOAModal.',
        'flow XML and lwc/*.html')
    add('Info', 'Self-registration is off but the Register page still exists',
        'Network selfRegistration is false. Users are provisioned by back-office flows (see Journey 1).', 'network-meta.xml')
    add('Review', 'Guest exposure should be confirmed',
        'Most routes (including Submit a PO, Support, Shipment Status, School Scheduling and PD Certificate) use the site default of public access. '
        'Whether guests can actually read or write the underlying data depends on the guest user profile and sharing, which this review did not examine.',
        'route pageAccess = UseParent; site authenticationType')
    return F
