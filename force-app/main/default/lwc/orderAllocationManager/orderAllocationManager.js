import { LightningElement, track } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

// ============================================================
// Mock Data — replaced by Apex in Phase 2
// ============================================================

const MOCK_BSOS = [
    { id: 'bso001', pqNumber: 'PQ-2024-0142', customerQuote: 'CQ-55821', poNumber: 'PO-44103', program: 'Amplify ELA',     allocationStatus: 'Open',      orderEndDate: '2025-08-15' },
    { id: 'bso002', pqNumber: 'PQ-2024-0287', customerQuote: 'CQ-55834', poNumber: 'PO-44109', program: 'Amplify ELA',     allocationStatus: 'Submitted', orderEndDate: '2025-06-30' },
    { id: 'bso003', pqNumber: 'PQ-2024-0391', customerQuote: 'CQ-56011', poNumber: 'PO-44201', program: 'Amplify Science', allocationStatus: 'Open',      orderEndDate: '2025-09-01' },
    { id: 'bso004', pqNumber: 'PQ-2023-0892', customerQuote: 'CQ-53441', poNumber: 'PO-43801', program: 'Amplify Science', allocationStatus: 'Confirmed', orderEndDate: '2024-12-15' },
    { id: 'bso005', pqNumber: 'PQ-2024-0455', customerQuote: 'CQ-56221', poNumber: 'PO-44315', program: 'CKLA',            allocationStatus: 'Open',      orderEndDate: '2025-07-31' },
    { id: 'bso006', pqNumber: 'PQ-2024-0512', customerQuote: 'CQ-56480', poNumber: 'PO-44402', program: 'CKLA',            allocationStatus: 'Draft',     orderEndDate: '2025-10-31' },
];

const MOCK_PRODUCTS = [
    { id: 'p001', name: 'Amplify ELA Grade K Student Edition',      isbn: '978-1-68333-001-2', program: 'Amplify ELA',          available: 450  },
    { id: 'p002', name: 'Amplify ELA Grade K Teacher Edition',      isbn: '978-1-68333-002-9', program: 'Amplify ELA',          available: 45   },
    { id: 'p003', name: 'Amplify ELA Grade 1 Student Edition',      isbn: '978-1-68333-003-6', program: 'Amplify ELA',          available: 520  },
    { id: 'p004', name: 'Amplify ELA Grade 1 Teacher Edition',      isbn: '978-1-68333-004-3', program: 'Amplify ELA',          available: 52   },
    { id: 'p005', name: 'Amplify ELA Grade 2 Student Edition',      isbn: '978-1-68333-005-0', program: 'Amplify ELA',          available: 495  },
    { id: 'p006', name: 'Amplify ELA Grade 2 Teacher Edition',      isbn: '978-1-68333-006-7', program: 'Amplify ELA',          available: 50   },
    { id: 'p007', name: 'Amplify ELA Grade 3 Student Edition',      isbn: '978-1-68333-007-4', program: 'Amplify ELA',          available: 480  },
    { id: 'p008', name: 'Amplify ELA Grade 3 Teacher Edition',      isbn: '978-1-68333-008-1', program: 'Amplify ELA',          available: 48   },
    { id: 'p009', name: 'Amplify ELA Grade 4 Student Edition',      isbn: '978-1-68333-009-8', program: 'Amplify ELA',          available: 510  },
    { id: 'p010', name: 'Amplify ELA Grade 4 Teacher Edition',      isbn: '978-1-68333-010-4', program: 'Amplify ELA',          available: 51   },
    { id: 'p011', name: 'Amplify ELA Grade 5 Student Edition',      isbn: '978-1-68333-011-1', program: 'Amplify ELA',          available: 530  },
    { id: 'p012', name: 'Amplify ELA Grade 5 Teacher Edition',      isbn: '978-1-68333-012-8', program: 'Amplify ELA',          available: 53   },
    { id: 'p013', name: 'Amplify ELA Grade 6 Student Edition',      isbn: '978-1-68333-013-5', program: 'Amplify ELA',          available: 465  },
    { id: 'p014', name: 'Amplify ELA Grade 6 Teacher Edition',      isbn: '978-1-68333-014-2', program: 'Amplify ELA',          available: 47   },
    { id: 'p015', name: 'Amplify ELA Classroom Kit Grade K',        isbn: '978-1-68333-015-9', program: 'Amplify ELA',          available: 90   },
    { id: 'p016', name: 'Amplify ELA Classroom Kit Grade 1',        isbn: '978-1-68333-016-6', program: 'Amplify ELA',          available: 104  },
    { id: 'p017', name: 'Amplify ELA Classroom Kit Grade 2',        isbn: '978-1-68333-017-3', program: 'Amplify ELA',          available: 99   },
    { id: 'p018', name: 'Amplify ELA Classroom Kit Grade 3',        isbn: '978-1-68333-018-0', program: 'Amplify ELA',          available: 96   },
    { id: 'p019', name: 'Amplify ELA Classroom Kit Grade 4',        isbn: '978-1-68333-019-7', program: 'Amplify ELA',          available: 102  },
    { id: 'p020', name: 'Amplify ELA Classroom Kit Grade 5',        isbn: '978-1-68333-020-3', program: 'Amplify ELA',          available: 106  },
    { id: 'p021', name: 'Amplify ELA Supplemental Workbook K',      isbn: '978-1-68333-021-0', program: 'Amplify ELA',          available: 450  },
    { id: 'p022', name: 'Amplify ELA Supplemental Workbook 1',      isbn: '978-1-68333-022-7', program: 'Amplify ELA',          available: 520  },
    { id: 'p023', name: 'Amplify ELA Assessment Guide K',           isbn: '978-1-68333-023-4', program: 'Amplify ELA',          available: 45   },
    { id: 'p024', name: 'Amplify ELA Assessment Guide 1',           isbn: '978-1-68333-024-1', program: 'Amplify ELA',          available: 52   },
    { id: 'p025', name: 'Amplify ELA Assessment Guide 2',           isbn: '978-1-68333-025-8', program: 'Amplify ELA',          available: 50   },
    { id: 'p026', name: 'Amplify ELA Family Letter Set K',          isbn: '978-1-68333-026-5', program: 'Amplify ELA',          available: 900  },
    { id: 'p027', name: 'Amplify ELA Family Letter Set 1',          isbn: '978-1-68333-027-2', program: 'Amplify ELA',          available: 1040 },
    { id: 'p028', name: 'Amplify ELA Family Letter Set 2',          isbn: '978-1-68333-028-9', program: 'Amplify ELA',          available: 990  },
    { id: 'p029', name: 'Professional Learning Guide',              isbn: '978-1-68333-029-6', program: 'Amplify ELA',          available: 150  },
    { id: 'p030', name: 'Shipping & Handling — Standard',           isbn: null,                program: 'Shipping and Handling', available: 1    },
];

const MOCK_CONTACTS = [
    { value: 'con001', label: 'Sarah Johnson' },
    { value: 'con002', label: 'Michael Torres' },
    { value: 'con003', label: 'Emily Chen' },
    { value: 'con004', label: 'David Williams' },
];

const MOCK_SITES = [
    {
        id: 'oa001', displayName: 'Lincoln Elementary', status: 'New', editable: true, configured: true,
        addressId: 'addr001', addressLabel: 'Lincoln Elementary — 123 Main St, Springfield, IL 62701',
        contactId: 'con001', contactPhone: '217-555-0101',
        doNotDeliverBefore: '', blackoutStart: '', blackoutEnd: '',
        fiscalYearEnd: '', roomOfChoice: '', floorNumber: null,
    },
    {
        id: 'oa002', displayName: 'Roosevelt Middle School', status: 'Confirmed', editable: false, configured: true,
        addressId: 'addr002', addressLabel: 'Roosevelt Middle School — 456 Oak Ave, Springfield, IL 62702',
        contactId: 'con002', contactPhone: '217-555-0202',
        doNotDeliverBefore: '', blackoutStart: '', blackoutEnd: '',
        fiscalYearEnd: '', roomOfChoice: '', floorNumber: null,
    },
    {
        id: 'oa003', displayName: 'Site 3', status: 'New', editable: true, configured: false,
        addressId: null, addressLabel: null,
        contactId: null, contactPhone: '',
        doNotDeliverBefore: '', blackoutStart: '', blackoutEnd: '',
        fiscalYearEnd: '', roomOfChoice: '', floorNumber: null,
    },
];

const MOCK_SHIPPING_ADDRESSES = [
    { value: 'addr001', label: 'Lincoln Elementary — 123 Main St, Springfield, IL 62701' },
    { value: 'addr002', label: 'Roosevelt Middle School — 456 Oak Ave, Springfield, IL 62702' },
    { value: 'addr003', label: 'South High School — 789 Elm Dr, Springfield, IL 62703' },
    { value: 'addr004', label: 'District Office — 321 Center Blvd, Springfield, IL 62704' },
    { value: 'addr005', label: 'Washington Elementary — 555 Park Rd, Springfield, IL 62705' },
];

// Pre-filled quantities for sites 1 and 2
const INITIAL_QUANTITIES = {
    'p001-oa001': 150,  'p001-oa002': 200,
    'p002-oa001': 15,   'p002-oa002': 20,
    'p003-oa001': 180,  'p003-oa002': 220,
    'p004-oa001': 18,   'p004-oa002': 22,
    'p005-oa001': 160,  'p005-oa002': 180,
    'p006-oa001': 16,   'p006-oa002': 18,
    'p007-oa001': 155,  'p007-oa002': 175,
    'p008-oa001': 16,   'p008-oa002': 17,
    'p015-oa001': 30,   'p015-oa002': 35,
    'p016-oa001': 34,   'p016-oa002': 40,
    'p026-oa001': 300,  'p026-oa002': 350,
    'p027-oa001': 340,  'p027-oa002': 400,
    'p029-oa001': 50,   'p029-oa002': 60,
    'p030-oa001': 1,    'p030-oa002': 1,
};

const STATUS_BADGE_CLASSES = {
    'Open':        'status-badge status-open',
    'Draft':       'status-badge status-draft',
    'Submitted':   'status-badge status-submitted',
    'Confirmed':   'status-badge status-confirmed',
    'Cancelled':   'status-badge status-cancelled',
    'In Progress': 'status-badge status-in-progress',
    'New':         'status-badge status-new',
};

// ============================================================
// Component
// ============================================================

export default class OrderAllocationManager extends LightningElement {

    // --- Navigation ---
    currentView = 'list';
    @track selectedBso = null;

    // --- BSO List ---
    @track bsoGroups = [];

    // --- Table ---
    @track sites = [];
    @track quantities = {};
    products = [];
    @track filteredProducts = [];
    searchTerm = '';
    programFilter = '';
    siteCounter = 4;
    currentPage = 1;
    pageSize = 25;

    // --- Drawer ---
    @track drawerOpen = false;
    @track activeSite = null;

    // --- Submit Modal ---
    @track showSubmitModal = false;

    shippingAddressOptions = MOCK_SHIPPING_ADDRESSES;
    shippingContactOptions = MOCK_CONTACTS;


    // ============================================================
    // Lifecycle
    // ============================================================

    connectedCallback() {
        this.initializeBsoGroups();
    }

    renderedCallback() {
        if (this.isTableView) {
            this.syncInputsFromQuantities();
        }
    }


    // ============================================================
    // Initialization
    // ============================================================

    initializeBsoGroups() {
        const grouped = MOCK_BSOS.reduce((acc, bso) => {
            if (!acc[bso.program]) acc[bso.program] = [];
            acc[bso.program].push(bso);
            return acc;
        }, {});

        this.bsoGroups = Object.entries(grouped).map(([program, orders]) => ({
            program,
            expanded: true,
            orderCount: orders.length,
            orders: orders.map(o => ({ ...o, statusBadgeClass: this.getStatusBadgeClass(o.allocationStatus) })),
        }));
    }

    initializeTableData() {
        this.products = JSON.parse(JSON.stringify(MOCK_PRODUCTS));
        this.sites    = JSON.parse(JSON.stringify(MOCK_SITES));
        this.quantities = { ...INITIAL_QUANTITIES };
        this.filteredProducts = [...this.products];
        this.searchTerm = '';
        this.programFilter = '';
        this.siteCounter = 4;
    }

    // Sync uncontrolled input values from the quantities map after render.
    // Only touches DOM nodes whose displayed value differs from state.
    syncInputsFromQuantities() {
        const inputs = this.template.querySelectorAll('input[data-product-id]');
        inputs.forEach(input => {
            const key = `${input.dataset.productId}-${input.dataset.siteId}`;
            const expected = this.quantities[key] || 0;
            if (parseFloat(input.value) !== expected) {
                input.value = expected;
            }
        });
    }


    // ============================================================
    // Getters — Navigation
    // ============================================================

    get isListView()  { return this.currentView === 'list'; }
    get isTableView() { return this.currentView === 'table'; }


    // ============================================================
    // Getters — BSO List
    // ============================================================

    get bsoGroupsView() {
        return this.bsoGroups.map(g => ({
            ...g,
            chevronIcon: g.expanded ? 'utility:chevrondown' : 'utility:chevronright',
        }));
    }


    // ============================================================
    // Getters — Table
    // ============================================================

    get sitesForHeader() {
        return this.sites.map(site => ({
            ...site,
            notConfigured: !site.configured,
            statusBadgeClass: this.getStatusBadgeClass(site.status),
            thClass: `site-th${this.activeSite && this.activeSite.id === site.id ? ' site-th-active' : ''}`,
        }));
    }

    get productsWithCalcs() {
        return this.filteredProducts.map(product => {
            const siteData = this.sites.map(site => {
                const quantity = this.quantities[`${product.id}-${site.id}`] || 0;
                return {
                    ...site,
                    quantity,
                    notEditable: !site.editable,
                    inputClass: 'qty-input', // updated below after distributed is known
                };
            });

            const distributed   = siteData.reduce((sum, s) => sum + s.quantity, 0);
            const remaining     = product.available - distributed;
            const overAllocated = remaining < 0;

            const siteDataFinal = siteData.map(s => ({
                ...s,
                inputClass: `qty-input${overAllocated ? ' qty-error' : ''}`,
            }));

            return {
                ...product,
                siteData: siteDataFinal,
                distributed,
                remaining,
                remainingClass: this.getRemainingClass(remaining),
                overAllocated: overAllocated,
                overAllocatedMessage: overAllocated ? `Over-allocated by ${Math.abs(remaining)} unit(s)` : '',
            };
        });
    }

    get managerBodyClass() {
        return `manager-body${this.drawerOpen ? ' drawer-is-open' : ''}`;
    }

    get drawerClass() {
        return `site-drawer${this.drawerOpen ? ' drawer-open' : ''}`;
    }

    get pagedProducts() {
        const start = (this.currentPage - 1) * this.pageSize;
        return this.productsWithCalcs.slice(start, start + this.pageSize);
    }

    get totalPages() {
        return Math.max(1, Math.ceil(this.filteredProducts.length / this.pageSize));
    }

    get pageStart() { return (this.currentPage - 1) * this.pageSize + 1; }
    get pageEnd()   { return Math.min(this.currentPage * this.pageSize, this.filteredProducts.length); }

    get isFirstPage()    { return this.currentPage === 1; }
    get isLastPage()     { return this.currentPage >= this.totalPages; }

    get isPageSize1()    { return this.pageSize === 1; }
    get isPageSize5()    { return this.pageSize === 5; }
    get isPageSize10()   { return this.pageSize === 10; }
    get isPageSize25()   { return this.pageSize === 25; }
    get isPageSize50()   { return this.pageSize === 50; }
    get isPageSize75()   { return this.pageSize === 75; }
    get isPageSize100()  { return this.pageSize === 100; }

    get pageLabel()   { return `Page ${this.currentPage} of ${this.totalPages}`; }

    get filteredProductCount() { return this.filteredProducts.length; }
    get totalProductCount()    { return this.products.length; }

    get programFilterOptions() {
        const programs = [...new Set(this.products.map(p => p.program))];
        return [
            { label: 'All Programs', value: '' },
            ...programs.map(p => ({ label: p, value: p })),
        ];
    }


    // ============================================================
    // Getters — Submit Modal
    // ============================================================

    get submitChecks() {
        const checks = [];

        // 1. All active sites must have a shipping address
        const unconfigured = this.sites.filter(s => s.status !== 'Cancelled' && !s.configured);
        checks.push({
            id: 'check-configured',
            pass: unconfigured.length === 0,
            label: unconfigured.length === 0
                ? 'All sites have a shipping address configured'
                : `${unconfigured.length} site(s) missing a shipping address: ${unconfigured.map(s => s.displayName).join(', ')}`,
            icon:        unconfigured.length === 0 ? 'utility:success' : 'utility:error',
            itemClass:  `preflight-item ${unconfigured.length === 0 ? 'check-pass' : 'check-fail'}`,
        });

        // 2. No product may be over-allocated
        const overAllocated = this.products.filter(p => {
            const dist = this.sites.reduce((sum, s) => sum + (this.quantities[`${p.id}-${s.id}`] || 0), 0);
            return dist > p.available;
        });
        checks.push({
            id: 'check-overallocated',
            pass: overAllocated.length === 0,
            label: overAllocated.length === 0
                ? 'No products are over-allocated'
                : `${overAllocated.length} product(s) exceed available quantity`,
            icon:       overAllocated.length === 0 ? 'utility:success' : 'utility:error',
            itemClass: `preflight-item ${overAllocated.length === 0 ? 'check-pass' : 'check-fail'}`,
        });

        // 3. At least some quantities assigned (warning, not a blocker)
        const totalQty = Object.values(this.quantities).reduce((sum, q) => sum + q, 0);
        checks.push({
            id: 'check-quantities',
            pass: true, // warning only
            label: totalQty > 0
                ? `Quantities assigned across ${this.sites.filter(s => s.status !== 'Cancelled').length} site(s)`
                : 'No quantities have been assigned yet — you may still submit',
            icon:       totalQty > 0 ? 'utility:success' : 'utility:warning',
            itemClass: `preflight-item ${totalQty > 0 ? 'check-pass' : 'check-warn'}`,
        });

        return checks;
    }

    get hasSubmitErrors() {
        return this.submitChecks.some(c => !c.pass);
    }


    // ============================================================
    // Handlers — Navigation
    // ============================================================

    handleSelectBso(event) {
        const bsoId = event.currentTarget.dataset.id;
        const bso   = MOCK_BSOS.find(b => b.id === bsoId);
        this.selectedBso = { ...bso, statusBadgeClass: this.getStatusBadgeClass(bso.allocationStatus) };
        this.initializeTableData();
        this.currentView = 'table';
    }

    handleBack() {
        this.currentView    = 'list';
        this.selectedBso    = null;
        this.drawerOpen     = false;
        this.activeSite     = null;
        this.showSubmitModal = false;
    }

    handleToggleGroup(event) {
        const program = event.currentTarget.dataset.program;
        this.bsoGroups = this.bsoGroups.map(g =>
            g.program === program ? { ...g, expanded: !g.expanded } : g
        );
    }


    // ============================================================
    // Handlers — Toolbar
    // ============================================================

    handleSearch(event) {
        this.searchTerm = event.target.value;
        this.applyFilters();
    }

    handleProgramFilter(event) {
        this.programFilter = event.detail.value;
        this.applyFilters();
    }

    applyFilters() {
        const term    = this.searchTerm.trim().toLowerCase();
        const program = this.programFilter;
        this.filteredProducts = this.products.filter(p => {
            const matchesSearch  = !term    || p.name.toLowerCase().includes(term) || (p.isbn && p.isbn.toLowerCase().includes(term));
            const matchesProgram = !program || p.program === program;
            return matchesSearch && matchesProgram;
        });
        this.currentPage = 1;
    }

    handlePrevPage() {
        if (!this.isFirstPage) this.currentPage -= 1;
    }

    handleNextPage() {
        if (!this.isLastPage) this.currentPage += 1;
    }

    handlePageSizeChange(event) {
        this.pageSize = parseInt(event.target.value, 10);
        this.currentPage = 1;
    }

    handleAddSite() {
        const newSite = {
            id:           `oa_new_${this.siteCounter}`,
            displayName:  `Site ${this.siteCounter}`,
            status:       'New',
            editable:     true,
            configured:   false,
            addressId:    null,
            addressLabel: null,
        };
        this.siteCounter++;
        this.sites = [...this.sites, newSite];
    }


    // ============================================================
    // Handlers — Site Column
    // ============================================================

    handleSiteClick(event) {
        event.stopPropagation();
        const siteId = event.currentTarget.dataset.id;
        const site   = this.sites.find(s => s.id === siteId);
        if (site) {
            this.activeSite = { ...site };
            this.drawerOpen = true;
        }
    }

    handleClearSite(event) {
        event.stopPropagation();
        const siteId = event.currentTarget.dataset.id;
        const updated = { ...this.quantities };
        this.products.forEach(p => delete updated[`${p.id}-${siteId}`]);
        this.quantities = updated;
    }

    handleRemoveSite(event) {
        event.stopPropagation();
        const siteId = event.currentTarget.dataset.id;
        this.sites = this.sites.filter(s => s.id !== siteId);
        if (this.activeSite && this.activeSite.id === siteId) {
            this.drawerOpen = false;
            this.activeSite = null;
        }
        const updated = { ...this.quantities };
        this.products.forEach(p => delete updated[`${p.id}-${siteId}`]);
        this.quantities = updated;
    }


    // ============================================================
    // Handlers — Cell Input
    // ============================================================

    handleInputFocus(event) {
        event.target.select();
    }

    handleInput(event) {
        const { productId, siteId } = event.target.dataset;
        const value = Math.max(0, parseFloat(event.target.value) || 0);
        this.quantities = { ...this.quantities, [`${productId}-${siteId}`]: value };
    }

    handleInputBlur(event) {
        const { productId, siteId } = event.target.dataset;
        const value      = Math.max(0, parseFloat(event.target.value) || 0);
        const maxAllowed = this.getMaxForSite(productId, siteId);

        if (value > maxAllowed) {
            const overage = value - maxAllowed;
            this.dispatchEvent(new ShowToastEvent({
                title:   'Product Over-Allocated',
                message: `This site exceeds available quantity by ${overage} unit(s). Reduce quantities on this or another site before submitting.`,
                variant: 'warning',
                mode:    'dismissable',
            }));
        }
    }

    handleIncrement(event) {
        const { productId, siteId } = event.currentTarget.dataset;
        const key        = `${productId}-${siteId}`;
        const current    = this.quantities[key] || 0;
        const maxAllowed = this.getMaxForSite(productId, siteId);

        if (current >= maxAllowed) return; // silently stop at the cap

        this.quantities = { ...this.quantities, [key]: current + 1 };
        this.setInputDomValue(productId, siteId, current + 1);
    }

    handleDecrement(event) {
        const { productId, siteId } = event.currentTarget.dataset;
        const key     = `${productId}-${siteId}`;
        const current = this.quantities[key] || 0;
        if (current > 0) {
            this.quantities = { ...this.quantities, [key]: current - 1 };
            this.setInputDomValue(productId, siteId, current - 1);
        }
    }

    // Directly set a specific input's DOM value (used by +/- buttons to avoid
    // waiting for renderedCallback to sync)
    setInputDomValue(productId, siteId, value) {
        const input = this.template.querySelector(
            `input[data-product-id="${productId}"][data-site-id="${siteId}"]`
        );
        if (input) input.value = value;
    }


    // ============================================================
    // Handlers — Drawer
    // ============================================================

    handleCloseDrawer() {
        this.drawerOpen = false;
        this.activeSite = null;
    }

    handleDisplayNameChange(event) {
        this.activeSite = { ...this.activeSite, displayName: event.target.value };
    }

    handleAddressChange(event) {
        const addressId     = event.detail.value;
        const addressOption = MOCK_SHIPPING_ADDRESSES.find(a => a.value === addressId);
        this.activeSite = {
            ...this.activeSite,
            addressId,
            addressLabel: addressOption ? addressOption.label : null,
            configured:   !!(addressId && this.activeSite.contactId),
        };
    }

    handleContactChange(event) {
        const contactId = event.detail.value;
        this.activeSite = {
            ...this.activeSite,
            contactId,
            configured: !!(this.activeSite.addressId && contactId),
        };
    }

    handlePhoneChange(event) {
        this.activeSite = { ...this.activeSite, contactPhone: event.target.value };
    }

    handleDoNotDeliverBeforeChange(event) {
        this.activeSite = { ...this.activeSite, doNotDeliverBefore: event.target.value };
    }

    handleBlackoutStartChange(event) {
        this.activeSite = { ...this.activeSite, blackoutStart: event.target.value };
    }

    handleBlackoutEndChange(event) {
        this.activeSite = { ...this.activeSite, blackoutEnd: event.target.value };
    }

    handleFiscalYearEndChange(event) {
        this.activeSite = { ...this.activeSite, fiscalYearEnd: event.target.value };
    }

    handleRoomOfChoiceChange(event) {
        this.activeSite = { ...this.activeSite, roomOfChoice: event.target.value };
    }

    handleFloorNumberChange(event) {
        this.activeSite = { ...this.activeSite, floorNumber: parseInt(event.target.value, 10) || null };
    }

    handleSaveDrawer() {
        const siteId = this.activeSite.id;
        this.sites = this.sites.map(s => s.id === siteId ? { ...this.activeSite } : s);
        this.dispatchEvent(new ShowToastEvent({
            title:   'Site Updated',
            message: `"${this.activeSite.displayName}" details have been saved.`,
            variant: 'success',
        }));
        this.drawerOpen = false;
        this.activeSite = null;
    }


    // ============================================================
    // Handlers — Submit Modal
    // ============================================================

    handleSaveDraft() {
        this.dispatchEvent(new ShowToastEvent({
            title:   'Draft Saved',
            message: 'Your allocation quantities have been saved.',
            variant: 'success',
        }));
    }

    handleSubmitClick() {
        this.showSubmitModal = true;
    }

    handleCloseSubmitModal() {
        this.showSubmitModal = false;
    }

    // Close modal on backdrop click (but not on the modal itself)
    handleBackdropClick(event) {
        if (event.target === event.currentTarget) {
            this.showSubmitModal = false;
        }
    }

    handleConfirmSubmit() {
        this.showSubmitModal = false;
        this.dispatchEvent(new ShowToastEvent({
            title:   'Order Submitted',
            message: 'Your allocation request has been submitted successfully.',
            variant: 'success',
        }));
        this.currentView = 'list';
    }


    // ============================================================
    // Helpers
    // ============================================================

    // Returns the maximum quantity that can be assigned to a single site for a given product,
    // i.e. available minus whatever all other sites have already claimed.
    getMaxForSite(productId, siteId) {
        const product = this.products.find(p => p.id === productId);
        if (!product) return 0;
        const otherTotal = this.sites
            .filter(s => s.id !== siteId)
            .reduce((sum, s) => sum + (this.quantities[`${productId}-${s.id}`] || 0), 0);
        return Math.max(0, product.available - otherTotal);
    }

    getStatusBadgeClass(status) {
        return STATUS_BADGE_CLASSES[status] || 'status-badge status-default';
    }

    getRemainingClass(remaining) {
        const base = 'col-number td-freeze-4';
        if (remaining < 0) return `${base} remaining-error`;
        return base;
    }
}
