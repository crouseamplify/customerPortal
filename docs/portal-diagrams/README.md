# Amplify Customer Portal: process and workflow diagrams

How a user moves through the Amplify Customer Portal (LWR Experience Cloud site) and how pages, screen flows, data and back-office automation fit together.

Source: metadata retrieved from **AmplifyDev1** on 2026-10-08 (site bundle `Amplify_Customer_Portal1`, 29 portal flows, 10 navigation menus) plus the LWCs and Apex in this repo.

## Start here

| If you want to... | Open |
|---|---|
| Explore it interactively (click, filter, walk through) | [interactive/portal-explorer.html](interactive/portal-explorer.html). One self-contained file, works offline, no install. Open it in any browser. |
| See the big picture on one page | [static/01-architecture.png](static/01-architecture.png) |
| Read a diagram legend | [static/00-legend.png](static/00-legend.png) |

## Static diagrams (`static/`, each as `.svg` for zoom and `.png` for slides)

| # | Diagram | What it answers |
|---|---|---|
| 01 | `01-architecture` | For each business area: which page, which screen flows and subflows, which data is written, which back-office automation fires |
| 02 | `02-site-map` | Every page, its URL, whether it needs login, and which tab holds which flow |
| 03 | `03-persona-navigation-matrix` | Who sees which menu, by contact type and account tier |
| 04 | `04-journey-sign-in` | Login, password and username recovery, and where accounts come from |
| 05 | `05-journey-guest-self-service` | What anyone can do without logging in |
| 06 | `06-journey-onboarding` | New customer path across Contact Management, Digital Onboarding, Order Management, PD |
| 07 | `07-journey-order-allocation` | BSO to allocation request to site logistics to submission |
| 08 | `08-journey-professional-development` | PD requests, session changes, certificates |
| 09 | `09-flow-dependency-map` | Which flows call which subflows |
| 10 | `10-data-matrix` | Which flows read or write which objects |
| 11 | `11-cross-cutting` | Personalisation, usage tracking, identity resolution, fault handling, internal-staff path |
| `flows/` | one flowchart per flow (28) | Screens, decisions, loops, subflow calls, data operations, in order |

## Interactive explorer

Eight tabs: **Overview** (architecture), **Site map**, **Journeys** (step-by-step walkthrough that highlights each step), **Flows** (all 28 flowcharts, click a subflow node to drill down), **Who sees what** (pick contact types and tier, see that user's menus and home tiles), **Data** (object by flow matrix), **Flow dependencies**, **Findings**.

Controls: drag to pan, scroll to move, Ctrl/Cmd or Shift + scroll to zoom.

## How the portal works, in brief

- **Pages.** 27 views. Four require login (Order Management, Digital Onboarding, Contact Management, Professional Development). The rest use the site default, which allows guests.
- **Screen flows do the work.** Pages are mostly thin shells. A flow embedded with `dxp_flow:flow` (sometimes with a parameter such as `Input_pageName`) performs the transaction. One flow, *Display Contacts*, is reused on four pages and its parameter selects which contact role it manages.
- **Identity scoping.** Nearly every flow calls the shared subflow *CALM Portal | Get User Details*, which resolves the running user's Contact, Account, child accounts and secondary Affiliations. All queries are scoped by those IDs.
- **Personalisation.** Experience Builder audience rules on `Contact.Contact_Type__c` and `Account.Tier__c` choose the menu (desktop and mobile) and the home tiles. 10 variations, first match wins.
- **No self-registration.** Users are created by record-triggered flows (Contact saved, BSO saved) and removed through a platform event. See Journey 4.
- **Back-office layer.** Writing certain records fires record-triggered flows: allocation emails and status sync, Portal Log to Cases, Tutor scheduling (about 37 flows), PD request date logic.
- **Cross-cutting.** Usage tracking (`portalTracker`, `flowPortalTracker`, tracking actions) and a shared fault screen that nearly every flow routes to.

## Findings worth a look

Full list with evidence is in the **Findings** tab and `model/findings.json`. Highlights:

1. **Fix.** The `Test` page embeds flow `Portal_Tracker_Test`, which does not exist in the org.
2. **Fix.** Menu `Primary_Onboarding_Contact_3T` has an item labelled "Make a payment" that links to `/CheckPasswordResetEmail`.
3. **Fix.** Inner-page mobile menu: the "Guest/Generic" rule has criterion 4 as *Contains* PD contact where the desktop rule has *NotContains*. Logged-in contacts with no contact type get no mobile menu.
4. **Review.** Technical + PD contacts (tier 3 family) get a different mobile home menu than desktop (mobile adds Orders and shipping).
5. **Review.** Tier 3+ with Technical + Materials + PD types loses the Professional Development link on inner pages (rule lists tier 3T twice, omits 3+).
6. **Review.** One rule contains the typo "Technical Conact".
7. **Info.** `orderAllocationManager` at `/omp` uses mock data and is in no menu. The `orderStatus*` LWCs are not used by any flow on this site.
8. **Review.** Guest access depends on the guest user profile and sharing, which this review did not examine.

## Limits of this review

- Read from one sandbox (AmplifyDev1). Production may differ.
- Flow diagrams omit fault connectors, assignments, transforms and tracking actions to stay readable. Open the flow in Flow Builder for full detail.
- Descriptions are written from reading the flows. Record-triggered flows were summarised by trigger object, and only nine were read in detail.
- Persona results come from evaluating the audience rules as written. They were not tested with live users.
- Objects marked `*` in flow diagrams are inferred from element labels because the flow takes records from a screen component.
- Not examined: Apex behind actions, permission sets and guest profile, email templates, the Tutor automation internals.

## Rebuild

```bash
# 1. Retrieve site + flows into a scratch SFDX project (must be inside a project dir)
mkdir -p /tmp/portal_proj/force-app && cd /tmp/portal_proj
echo '{"packageDirectories":[{"path":"force-app","default":true}],"sourceApiVersion":"66.0"}' > sfdx-project.json
sf project retrieve start -o AmplifyDev1 \
  -m "DigitalExperienceBundle:site/Amplify_Customer_Portal1" -m "Network:Amplify Customer Portal" \
  -m CustomSite -m NavigationMenu -m "Flow:<each flow API name listed in model/portal-model.json>"

# 2. Rebuild everything
docs/portal-diagrams/tools/build.sh /tmp/portal_proj/force-app/main/default
```

`model/active_flows_snapshot.json` is a saved query result (active portal-related flows with trigger objects). Refresh it with a `FlowDefinitionView` query if back-office automation changes.

Descriptions of pages and flows live in `tools/curated.py`; edit there and rebuild. Everything else is extracted from metadata.
