"""Human-written descriptions layered on top of the extracted metadata.

Everything structural (pages, tabs, which flow sits where, objects touched, subflow calls)
is extracted from metadata by build_model.py. Only the *explanations* live here, so when a
flow or page changes you edit one line and re-run the build.
"""

# Flow purposes. Keyed by flow API name.
FLOW_PURPOSE = {
    # ---- sign-in helpers
    'Customer_Portal_Request_Username':
        'Modal on the Login / Forgot Password pages. Visitor enters their email and is sent their username.',
    'Customer_Portal_Find_Username':
        'Subflow. Looks up the active portal User by email and emails the username; sends a verification '
        'reminder if the email is unverified, or a "no user found" notice.',
    # ---- guest self service
    'Community_PO_Submission_Flow':
        'Customer submits a purchase order against one or more CPQ quotes, optionally with a tax-exemption '
        'certificate. Works for guests: matches contact/account by email or domain, creates a Contact if '
        'needed, logs everything in Community Portal Log, creates a Task for the tax form.',
    'Customer_Portal_Web_Form_to_Case':
        'Support web form. Anti-bot "submitted too fast" trap, then hands off to the case-creation subflow. '
        'Works for guests and logged-in users.',
    'Customer_Portal_Create_Case_from_Webform':
        'Subflow. Reads the Customer Portal Cases custom metadata, matches the requester Contact, routes to a '
        'support queue (Pedagogical, Physical Materials, Digital Materials, Strategic), creates or updates the '
        'Case, attaches files, emails the requester and publishes a Case Web Form Comment event.',
    'Community_Material_Status_v2':
        'Shipment status page. A token from the emailed link identifies the order (PQ). Logs the request, '
        'finds the Opportunity and its Integration Data Sync record, and shows shipment status. Errors email '
        'the support team.',
    'Knowledge_Article_Feedback_Customer_Portal':
        'Thumbs up/down voting on a Knowledge article, with an optional reason. Writes an Article Feedback '
        'record. Hides voting for collections and unpublished articles.',
    'Tutor_School_Request_Screen':
        'Token-linked page for school staff. Shows the school/district record and lets the school complete '
        'its scheduling information or approve the proposed tutoring schedule.',
    # ---- onboarding / contacts
    'Customer_Portal_Onboarding_Checklist':
        'Runs when Contact Management loads. Finds or creates the account\'s Onboarding Checklist record and '
        'refreshes its verified contact-type counts.',
    'Customer_Portal_Count_Contact_Types':
        'Subflow. Counts the account\'s portal contacts by contact type for the onboarding checklist.',
    'CALM_Portal_Contacts_Display_Contacts':
        'Contact roster for the account and its child accounts: list, add (New Contact subflow), edit, change '
        'contact types, invite, or remove access (publishes a Deactivate Portal User platform event). The '
        'Input_pageName value (cmp / omp / dop / pd) selects which contact role the page manages. Also run '
        'by Amplify staff (internal trigger).',
    'CALM_Portal_New_Contact':
        'Subflow. Adds a contact: duplicate check, email-domain-matches-account check, creates the Contact '
        'and an Affiliation record, or revives a former affiliation.',
    'Digital_Onboarding_Page_Key_Dates_and_Rostering_Information':
        'Technical contact reviews and updates the account\'s Technical Onboarding Case (key dates and '
        'rostering information). Selects a case, reviews details, writes the update back to the Case.',
    # ---- shipping + orders
    'CALM_Portal_View_Shipping_Addresses':
        'Lists the account\'s shipping addresses. Routes to Add New (if none exist) or Edit subflows.',
    'CALM_Portal_Add_New_Shipping_Addresses':
        'Subflow. Creates a Shipping Address for the account (or for the BSO when launched by staff).',
    'CALM_Portal_Edit_Shipping_Addresses':
        'Subflow. Edits a Shipping Address. If the address is already used on any Order Allocation it is '
        'cloned instead, and the allocations are repointed to the new address.',
    'CALM_Portal_Blanket_Sales_Order_Show_BSO_Details':
        'Orders tab. Lists the account\'s Blanket Sales Orders (BSOs). Choosing one starts the allocation '
        'journey (Create Order Allocation Request).',
    'CALM_Create_Order_Allocation':
        'Subflow. Shows existing Order Allocation Requests (OARs) for the BSO or starts a new one (creates '
        'the OAR and its first Order Allocation). Counts views. Hands off to Edit Order Allocations.',
    'CALM_Edit_Order_Allocations':
        'The main allocation editor. Per-site quantities of BSO products, save-and-stay, concurrent-edit '
        'conflict check, over-allocation check, cancel, and confirm. Launches the logistics modal per site '
        'and the final submit. Only a Materials Contact (or Amplify staff) may submit.',
    'CALM_Portal_Order_Allocation_Modal':
        'Subflow. Per-site delivery logistics: verify shipping address (editing it if required fields are '
        'missing), ship-to contact phone and delivery instructions, then marks the allocation confirmed.',
    'CALM_Portal_Submit_an_Allocation_Request':
        'Subflow. Verify-and-submit review, extra-details loop for unconfirmed sites, final confirmation, '
        'marks the allocations, the OAR and the BSO as submitted (and unlocks the allocations if the user backs out).',
    'CALM_Create_New_Order_Allocation':
        'Legacy. Adds a new site (Order Allocation) to an existing OAR. Launched from the createOAModal LWC '
        'used by the older allocationsTable_v2 component.',
    # ---- professional development
    'PD_Request_New_Customer_Portal_Input':
        'Request PD tab. Finds Work Orders and Service Appointments (SAs) available to schedule, lets the '
        'customer pick SAs and fill in details, then creates a PD Request with SA and session-topic '
        'connectors. Also supports a generic PD request. Updates the Onboarding Checklist PD stage.',
    'PD_Request_Customer_Portal_Change_Request':
        'Scheduled Sessions tab. Select already requested or scheduled SAs, edit them, and submit a change '
        'request (PD Request with SA and session-topic connectors).',
    'PD_Requests_Show_Completed_Service_Appointments':
        'Completed Sessions tab. Read-only table of the account\'s completed Service Appointments.',
    'PD_Completion_by_Customer_Screen_Flow':
        'Register for CTLE certificate. Attendee enters a session code and personal details; details are '
        'hashed (SHA-256 action plus bcrypt in the browser) and a PD Completion record is created.',
    'PD_Completion_Retrieval_Screen_Flow':
        'Retrieve CTLE certificate. Attendee re-enters details; hashes are compared in the browser against '
        'PD Completion records; matching certificates are listed and downloaded as PDF.',
    # ---- shared
    'CALM_Portal_Get_User_Details':
        'Shared identity resolver called by most flows. Works out the running user\'s Contact and Account, child '
        'accounts and secondary Affiliations, and returns the Account and Contact ID sets every other flow '
        'uses to scope its data. Has an internal-staff path that resolves from a BSO primary contact.',
    'Customer_Portal_Fault_Path_Screen':
        'Shared error handler. Every flow routes its fault connectors here: logs through the Portal Analytics '
        'error action and shows a "Something went wrong" screen with a Try Again button.',
}

# Page purposes. Keyed by view developer name (digitalExperiences sfdc_cms__view folder).
PAGE_PURPOSE = {
    'home': 'Landing page. Tiles and quick links are personalised by contact type and account tier.',
    'login': 'Login form, "forgot username" modal, employee login link. Self-registration is switched off.',
    'forgotPassword': 'Standard password reset, plus the "forgot username" modal.',
    'checkPasswordResetEmail': 'Confirmation that the reset email was sent.',
    'register': 'Self-registration page exists but self-registration is disabled on the site.',
    'Submit_a_PO': 'Purchase order submission for quotes. Open to guests.',
    'Make_a_Payment': 'Static remittance instructions (wire, ACH, mail). No flow.',
    'Support': 'Web form to Case (Webform theme layout). Open to guests.',
    'Help': 'Help Center landing: search, program list, topic tiles.',
    'Knowledge_Detail': 'Knowledge article viewer with translation links, related articles and article feedback.',
    'Search': 'Global search results.',
    'Order_Management': 'Materials contacts manage shipping addresses, the contacts who coordinate delivery, and orders (BSOs and allocations).',
    'Digital_Onboarding': 'Technical contacts provide key dates and rostering information; manage digital contacts.',
    'Professional_Development': 'Request PD sessions, manage PD contacts, change scheduled sessions, see completed sessions.',
    'PD_Certificate_of_Completion': 'CTLE certificate registration and retrieval for session attendees.',
    'Contact_Management': 'Primary contacts maintain the portal contact roster. Loads the onboarding checklist flow.',
    'Shipment_Status': 'Order shipment status, opened from an emailed tokenised link.',
    'School_Scheduling': 'Tutor program school information and approval, opened from an emailed tokenised link.',
    'OMP': 'Order Allocation Manager LWC (new). Uses mock data today; not linked from any navigation menu.',
    'Test': 'Test page. References flow Portal_Tracker_Test, which does not exist in the org.',
    'error': 'System error page.',
    'serviceNotAvailable': 'System page: service not available.',
    'tooManyRequests': 'System page: rate limit reached; auto-refresh.',
    'Knowledge_List': 'Standard Knowledge list route (no custom content).',
    'Knowledge_Related_List': 'Standard Knowledge related-list route (no custom content).',
    'Network_Data_Category_Detail': 'Standard topic/category route (no custom content).',
    'newsDetail': 'Standard news detail route (no custom content).',
}

# Contact type short codes used in persona labels (from Contact.Contact_Type__c values).
CONTACT_TYPES = [
    ('POC', 'Primary Onboarding Contact'),
    ('TC', 'Technical Contact'),
    ('MC', 'Materials Contact'),
    ('PDC', 'Professional Development Contact'),
]

# Which contact role each Contact Management tab/flow parameter manages.
PAGE_NAME_TO_ROLE = {
    'cmp': 'Contact Management page (Primary contact)',
    'omp': 'Order Management page (Materials contact)',
    'dop': 'Digital Onboarding page (Technical contact)',
    'pd': 'Professional Development page (PD contact)',
}

# Object API name -> friendly name for diagrams.
OBJECT_LABEL = {
    'Blanket_Sales_Orders__c': 'Blanket Sales Order (BSO)',
    'Blanket_Sales_Order_Product__c': 'BSO Product',
    'Order_Allocation_Request__c': 'Order Allocation Request (OAR)',
    'Order_Allocation__c': 'Order Allocation (site)',
    'Order_Allocation_Product__c': 'Order Allocation Product',
    'Shipping_Address__c': 'Shipping Address',
    'Contact': 'Contact',
    'Account': 'Account',
    'User': 'User',
    'Affiliations__c': 'Affiliation',
    'Onboarding_Checklist__c': 'Onboarding Checklist',
    'Case': 'Case',
    'EmailMessage': 'Email Message',
    'Community_Portal_Log__c': 'Community Portal Log',
    'Integration_Data_Sync__c': 'Integration Data Sync',
    'Opportunity': 'Opportunity',
    'SBQQ__Quote__c': 'CPQ Quote',
    'Task': 'Task',
    'ContentDocumentLink': 'File link',
    'ServiceAppointment': 'Service Appointment',
    'WorkOrder': 'Work Order',
    'WorkOrderLineItem': 'Work Order Line Item',
    'PD_Session_Topic__c': 'PD Session Topic',
    'PD_Completion__c': 'PD Completion',
    'RecordType': 'Record Type',
    'Tutor_School_Details__c': 'Tutor School Details',
    'Tutor_District_Details__c': 'Tutor District Details',
    'Knowledge__kav': 'Knowledge Article',
    'afl__afl_Article_Feedback__c': 'Article Feedback',
    'Network': 'Network (site)',
    'EmailTemplate': 'Email Template',
    'Deactivate_Customer_Portal_Users__e': 'Event: Deactivate Portal User',
    'Case_Web_Form_Comment__e': 'Event: Case Web Form Comment',
    'CALM_Automation_Defaults__mdt': 'CMDT: CALM Automation Defaults',
    'Automation_Defaults__mdt': 'CMDT: Automation Defaults',
    'Customer_Portal_Automation_Default__mdt': 'CMDT: Portal Automation Default',
    'Customer_Portal_Cases__mdt': 'CMDT: Portal Cases',
    'PD_Completion_Default__mdt': 'CMDT: PD Completion Default',
}

# Record-triggered / event-triggered flow trigger label -> object API name used by the portal flows.
BG_TRIGGER_TO_OBJECT = {
    'Order Allocation': 'Order_Allocation__c',
    'Order Allocation Request': 'Order_Allocation_Request__c',
    'Blanket Sales Orders': 'Blanket_Sales_Orders__c',
    'Blanket Sales Order Product': 'Blanket_Sales_Order_Product__c',
    'Contact': 'Contact',
    'Community Portal Log': 'Community_Portal_Log__c',
    'Case': 'Case',
    'Case Web Form Comment': 'Case_Web_Form_Comment__e',
    'Deactivate Customer Portal User': 'Deactivate_Customer_Portal_Users__e',
    'Tutor School Details': 'Tutor_School_Details__c',
    'PD Request': 'PD_Request__c',
    'Knowledge': 'Knowledge__kav',
    'User': 'User',
}

# Nav URL (lower-case, no leading slash) -> view developer name, for links that do not match urlPrefix.
NAV_URL_OVERRIDES = {
    'po-submission': 'Submit_a_PO',
    'customer-portal/make-a-payment': 'Make_a_Payment',
    'order-management-page': 'Order_Management',
    'digital-onboarding-page': 'Digital_Onboarding',
}

# Record operations whose sObject type cannot be read from the flow XML because they take their records from
# a screen component's output. Inferred from the element label / output name; flagged as inferred in the model.
OBJECT_OVERRIDES = {
    ('CALM_Edit_Order_Allocations', 'Update Order Allocation Products'): 'Order_Allocation_Product__c',
    ('CALM_Edit_Order_Allocations', 'Set Order Allocations to Cancelled'): 'Order_Allocation__c',
    ('CALM_Edit_Order_Allocations', 'Copy 1 of Set Order Allocations to Cancelled'): 'Order_Allocation__c',
    ('CALM_Portal_Edit_Shipping_Addresses', 'Create Shipping Address Clone'): 'Shipping_Address__c',
    ('CALM_Portal_Edit_Shipping_Addresses', 'Update Order Allocation Status and Shipping Address'): 'Order_Allocation__c',
    ('PD_Request_Customer_Portal_Change_Request', 'Update Reactive SAs Collection'): 'ServiceAppointment',
}

# Flows that are not placed on a page and not called by one, but are launched from an LWC in this repo.
LWC_LAUNCHED_FLOWS = {'CALM_Create_New_Order_Allocation': 'createOAModal', 'CALM_Portal_Order_Allocation_Modal': 'configureModal'}

# Short purpose for the back-office flows that were read in detail.
BACKGROUND_PURPOSE = {
    'CALM_Portal_Create_Portal_User_From_Contact':
        'When a Contact is saved: find or create the portal User, reactivate if inactive, and assign the '
        'Customer Portal Access permission set.',
    'CALM_Portal_Invite_Contact_to_Portal_Using_BSO_Status':
        'When a BSO is saved: find the Materials Coordinator (Opportunity contact role), stamp it as the BSO '
        'primary contact and invite it to the portal.',
    'Customer_Portal_Invite_Updated_BSO_Primary_Contact':
        'When the BSO primary contact changes: make sure the new contact carries the Materials contact type '
        'and is invited.',
    'Customer_Portal_Portal_User_Deactivation':
        'Platform-event subscriber (Deactivate Customer Portal User): deactivates the portal User.',
    'Customer_Portal_Deactivate_Portal_User': 'Autolaunched helper that deactivates a portal User.',
    'Community_Portal_Log_to_Cases':
        'When a Community Portal Log is saved (PO submission): create Cases per quote and link the uploaded '
        'documents to them.',
    'CALM_Portal_Send_Email_on_Order_Allocation_Submissions':
        'When an Order Allocation Request is submitted: send the confirmation email if the contact allows it.',
    'CALM_Create_Internal_Support_Case':
        'When an Order Allocation changes: create an internal support Case.',
    'CALM_Portal_Synchronize_Order_Allocation_and_Order_Allocation_Product_Status':
        'Keeps Order Allocation and Order Allocation Product status in step.',
}
