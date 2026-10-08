import { LightningElement, wire, api, track } from 'lwc';
// import { getPicklistValues } from 'lightning/uiObjectInfoApi';

// import STATUS_FIELD from '@salesforce/schema/Order_Fulfillment__c.Status__c';

import userId from '@salesforce/user/Id';
import createEvent from '@salesforce/apex/PortalTrackingController.createEvent';
import { parseDeviceType, parseBrowser, parseOS, parseScreenSize, parseViewport, parseLanguage, parseTimezone } from 'c/portalTrackerUtils';

// Lightning Message Service and a message channel
import { publish, subscribe, MessageContext } from 'lightning/messageService';
import ORDERS_FILTERED_MESSAGE from '@salesforce/messageChannel/OrdersFiltered__c';
//import ORDERSPQ_FILTERED_MESSAGE from '@salesforce/messageChannel/OrdersPQFiltered__c';
import ORDERSSHIPTO_FILTERED_MESSAGE from '@salesforce/messageChannel/OrdersShipToFiltered__c';
import SHIPMENTCOUNTS_MESSAGE from '@salesforce/messageChannel/OrdersShipmentCounts__c';

// Debounce for the live results filter (publish) — kept short so search still feels responsive.
const FILTER_DELAY = 250;
// Debounce for the SSP - Search Orders tracking event — longer than FILTER_DELAY so a mid-typing
// pause between keystrokes doesn't create a tracking record for every character.
const TRACK_DELAY = 500;

const SESSION_KEY     = 'portal_session_id';
const IS_INTERNAL_KEY = 'portal_is_internal';

export default class OrderStatusFilter extends LightningElement {

    searchKey;
    isbn;
    //    PQ;
    status;
    shipments;
    // True once the current search streak has already produced a tracking record.
    searchTracked = false;
    pclass = "slds-progress__marker neutral_marker" ;
    sclass = "slds-progress__marker neutral_marker" ;
    dclass = "slds-progress__marker neutral_marker" ;

    /**getting flow variables from orderStatusFilterOrder component */
    //  @api orderPQ;


    /** JSON.stringified version of filters to pass to apex */
    filters = {};
    /* this passes value to apex - initial value ''  */
    filters = {
        searchKey: '',
        isbn: '',
        PQ: '',
        shipToName: '',
        tracking: '',
        status: ''
    };

    shipments = {};
    shipments = {
        total: 0,
        processing: 0,
        shipped: 0,
        delivered: 0
    };


    /** JSON.stringified version of filters to pass to apex */
    //filters = {};

    @track isLoading = false;

    @wire(MessageContext)
    messageContext;



    // @wire(getPicklistValues, {
    //     recordTypeId: '012000000000000AAA',
    //      fieldApiName: STATUS_FIELD
    //  })
    //   status;


    /**Set status options for dropdown combobox */

    statusOptions = [
        {
            value: '',
            label: 'All',
            description: '',
        },
        {
            value: 'Preparing Your Order',
            label: 'Preparing Your Order',
            description: "Your material order is being processed and we'll notify you via email once it has shipped."
        },
        {
            value: 'Shipped',
            label: 'Shipped',
            description: 'Items from your materials order have left the warehouse, and are headed to one of our delivery partners.',
        },
        {
            value: 'Delivered',
            label: 'Delivered',
            description: 'Items from your materials order have been delivered!',
        },
    ];

    /** Subscription for ProductsFiltered Lightning message */
    //productFilterSubscription;
    //orderFilterSubscription;

    /**  Search value - validate add on to filters */
    handleSearchKeyChange(event) {
        const previousValue = this.filters.searchKey;
        const newValue      = event.target.value;
        this.filters.searchKey = newValue;

        console.log('OrderStatusFilter_FilterF-SEND-->' + JSON.stringify(this.filters));

        if (newValue === '') {
            // Field cleared: nothing to track, cancel any pending tracking timer, and
            // let the next non-empty value start a fresh search-tracking streak.
            window.clearTimeout(this.trackDelayTimeout);
            this.searchTracked = false;
        } else if (!this.isSearchContinuation(previousValue, newValue)) {
            // Value changed in a way that isn't a simple append/backspace of the prior
            // value (e.g., select-all and typed over) — treat as a new search.
            this.searchTracked = false;
        }

        // Debounced: onchange fires on every keystroke for lightning-input type="search".
        // Filter results and tracking use independent debounce timers/delays (see below).
        this.delayedFireFilterChangeEvent();
        if (newValue !== '') {
            this.delayedTrackSearchEvent();
        }
    }

    /**
     * True when newValue looks like a simple continuation (append or backspace) of
     * previousValue, rather than a wholesale replacement (e.g., select-all and typed over).
     */
    isSearchContinuation(previousValue, newValue) {
        if (!previousValue) {
            return false;
        }
        return newValue.startsWith(previousValue) || previousValue.startsWith(newValue);
    }

    //   handleStatusSelect change in the status value.

    handleStatusSelect(event) {
        this.filters.status = event.detail.value;

        console.log('OrderStatusFilter_StatusFilter-SEND-->' + JSON.stringify(this.filters));

        const selectedOption = this.statusOptions.find(option => option.value === this.filters.status);
        const filterLabel = selectedOption ? selectedOption.label : this.filters.status;
        this.trackFilterEvent(`SSP - Filter Changed to ${filterLabel}`);

        // Published ordersFiltered message for status change
        publish(this.messageContext, ORDERS_FILTERED_MESSAGE, {
            filters: this.filters
        });

    }





    connectedCallback() {
        // Subscribe to OrdersFiltered message to filter the orders Order_Fulfillments__c
        this.orderFilterSubscription = subscribe(
            this.messageContext,
            ORDERSSHIPTO_FILTERED_MESSAGE,
            (message) => this.handleFilterChange(message)
        );
        this.orderFilterSubscription = subscribe(
            this.messageContext,
            ORDERS_FILTERED_MESSAGE,
            (message) => this.handleFilterChange(message)
        );

        this.ShipmentsCountSubscription = subscribe(
            this.messageContext,
            SHIPMENTCOUNTS_MESSAGE,
            (message) => this.handleShipmentsChange(message)
        );

    }

    handleFilterChange(message) {
        this.filters = { ...message.filters };
        console.log('C_OrderStatusFilter_Filter-->' + JSON.stringify(this.filters));
    }

    handleShipmentsChange(message) {
        this.shipments = { ...message.shipments };
        console.log('A_OrderStatusFilter_Shipments-->' + JSON.stringify(this.shipments));

        if (this.shipments.processing > 0 ) {
            this.pclass = "slds-progress__marker green_marker"
        } else {
            this.pclass = "slds-progress__marker neutral_marker" 
        }

        if (this.shipments.shipped > 0 ) {
            this.sclass = "slds-progress__marker green_marker"
        } else {
            this.sclass = "slds-progress__marker neutral_marker" 
        }

        if (this.shipments.delivered > 0 ) {
            this.dclass = "slds-progress__marker green_marker"
        } else {
            this.dclass = "slds-progress__marker neutral_marker" 
        }



    }

    delayedFireFilterChangeEvent() {
        // Debouncing this method: do not actually fire the event as long as this function is
        // being called within FILTER_DELAY. This is to avoid a very large number of Apex
        // method calls in components listening to this event.
        window.clearTimeout(this.filterDelayTimeout);
        // eslint-disable-next-line @lwc/lwc/no-async-operation
        this.filterDelayTimeout = setTimeout(() => {
            // Published ProductsFiltered message
            publish(this.messageContext, ORDERS_FILTERED_MESSAGE, {
                filters: this.filters
            });
        }, FILTER_DELAY);
    }

    /**
     * Debounces the SSP - Search Orders tracking event on its own longer timer, independent
     * of the live results filter above, so a normal pause between keystrokes while typing
     * doesn't create a tracking record for every character. Only fires once per search
     * streak (see handleSearchKeyChange) — since we don't capture the search term itself,
     * a second event within the same streak wouldn't add any new information.
     */
    delayedTrackSearchEvent() {
        window.clearTimeout(this.trackDelayTimeout);
        // eslint-disable-next-line @lwc/lwc/no-async-operation
        this.trackDelayTimeout = setTimeout(() => {
            if (this.searchTracked) {
                return;
            }
            this.searchTracked = true;
            this.trackFilterEvent('SSP - Search Orders');
        }, TRACK_DELAY);
    }

    /**
     * Fires a Portal_Analytics__c event for an in-place filter interaction (no
     * navigation occurs, so pageUrl is the current page and there's no referrer).
     */
    trackFilterEvent(eventType) {
        try {
            const sessionId  = sessionStorage.getItem(SESSION_KEY);
            const isInternal = sessionStorage.getItem(IS_INTERNAL_KEY) === 'true';

            createEvent({
                sessionId,
                pageName    : document.title || null,
                pageUrl     : window.location.href,
                referrerUrl : null,
                eventType,
                searchTerm  : null,
                recordId    : null,
                urlName     : null,
                deviceType  : parseDeviceType(),
                screen      : parseScreenSize(),
                browser     : parseBrowser(),
                os          : parseOS(),
                viewport    : parseViewport(),
                language    : parseLanguage(),
                timeZone    : parseTimezone(),
                userId      : userId || null,
                isInternal
            }).catch(error => console.error('[OrderStatusFilter] tracking failed:', error));
        } catch (e) {
            console.error('[OrderStatusFilter] tracking failed:', e);
        }
    }

}