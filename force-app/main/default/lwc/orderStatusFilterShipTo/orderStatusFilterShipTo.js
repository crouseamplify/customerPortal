import { LightningElement, wire, track, api } from 'lwc';

// Lightning Message Service and message channels
import { publish, subscribe, MessageContext } from 'lightning/messageService';
import ORDERSSHIPTO_FILTERED_MESSAGE from '@salesforce/messageChannel/OrdersShipToFiltered__c';

import getOrderShipto from '@salesforce/apex/OrderStatusController.getOrderShipto';
import { FlowAttributeChangeEvent } from 'lightning/flowSupport';

import userId from '@salesforce/user/Id';
import createEvent from '@salesforce/apex/PortalTrackingController.createEvent';
import { parseDeviceType, parseBrowser, parseOS, parseScreenSize, parseViewport, parseLanguage, parseTimezone } from 'c/portalTrackerUtils';

const SESSION_KEY     = 'portal_session_id';
const IS_INTERNAL_KEY = 'portal_is_internal';

export default class OrderStatusFilterShipTo extends LightningElement {
    @api orderVariable;
    @api orderPQ;

    orderShipto;
    orderShipto1;
    orderShipto_prior;

    @track ShipToOptions;
    @track value = '-none-';
    //   @track districtName;
    @track singleorderShipto = {};
    //   @track parent;
    //   @track ultimateParent;
    //   @track customerPO;

    /** Load context for Lightning Messaging Service */
    @wire(MessageContext) messageContext;

    selectedKey = '';

    /** JSON.stringified version of filters to pass to apex */
    filters = {};
    /* this passes value to apex - initial value ''  */
    filters = {
        //searchKey: '',
        isbn: '',
        PQ: '',
        shipToName: '',
        tracking: '',
        status: ''
    };

    handleshipToNameChange(event) {
        this.selectedKey = event.detail.value;
        this.singleorderShipto = this.orderShipto[this.selectedKey];
//        this.filters.shipToName = this.orderShipto[this.selectedKey].Name;
        this.value = this.orderShipto[this.selectedKey].Name;
        this.filters.shipToName = this.value.replace(/\'/,"\\'");
        this.trackDeliveryLocationSelected();
        this.sendFilterMessage();
    }

    /**
     * Fires a Portal_Analytics__c event when the user picks a delivery location.
     * Only called from the user-driven change handler above, not from the
     * automatic default-selection in level1dataD when data first loads.
     */
    trackDeliveryLocationSelected() {
        try {
            const sessionId  = sessionStorage.getItem(SESSION_KEY);
            const isInternal = sessionStorage.getItem(IS_INTERNAL_KEY) === 'true';

            createEvent({
                sessionId,
                pageName    : document.title || null,
                pageUrl     : window.location.href,
                referrerUrl : null,
                eventType   : 'SSP - Delivery Location Selected',
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
            }).catch(error => console.error('[OrderStatusFilterShipTo] tracking failed:', error));
        } catch (e) {
            console.error('[OrderStatusFilterShipTo] tracking failed:', e);
        }
    }

    /**
     * Fires a Portal_Analytics__c event when the user clicks the customer care link
     * in the 60-day inventory notice below the shipping details card.
     */
    handleCustomerCareClick() {
        try {
            const sessionId  = sessionStorage.getItem(SESSION_KEY);
            const isInternal = sessionStorage.getItem(IS_INTERNAL_KEY) === 'true';

            createEvent({
                sessionId,
                pageName    : document.title || null,
                pageUrl     : 'https://service.amplify.com/support',
                referrerUrl : window.location.href,
                eventType   : 'SSP - Customer Care Link Clicked',
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
            }).catch(error => console.error('[OrderStatusFilterShipTo] tracking failed:', error));
        } catch (e) {
            console.error('[OrderStatusFilterShipTo] tracking failed:', e);
        }
    }

    sendFilterMessage() {
        console.log('OrderShipto_Filter-SEND-->' + JSON.stringify(this.filters));
        publish(this.messageContext, ORDERSSHIPTO_FILTERED_MESSAGE, {
            filters: this.filters
        });
    }

    @wire(getOrderShipto, { filters: '$filters', pageNumber: '1' })
    level1dataD(data, error) {
        if (error) {
            console.log('OrderShipto_error -->' + error);
        } else if (data && JSON.stringify(data).length != 2 && JSON.stringify(data.data).length != 2 && JSON.stringify(data.data).length != 18) {
            this.orderShipto1 = data.data;
            //console.log('OrderShipto1_valuesDataData-->' + JSON.stringify(this.orderShipto1));
            for (var key in this.orderShipto1) {
                if (this.orderShipto1[key].Name) {
                    if (this.orderShipto_prior != this.orderShipto1[key].Name) {
                        if (this.orderShipto) {
                            this.orderShipto = [...this.orderShipto, this.orderShipto1[key]];
                        } else {
                            this.orderShipto = [this.orderShipto1[key]];
                        }
                    }
                    this.orderShipto_prior = this.orderShipto1[key].Name;
                }
            }

            // ***Debug all ship to names***
            console.log('OrderShiptoA_valuesDataDataNamesA-->' + JSON.stringify(this.orderShipto, ["Name"]));
            //Populate ShipTo Combobox options with all shipto names
            let optionsA = [];
            for (var key in this.orderShipto) {
                optionsA.push({ label: this.orderShipto[key].Name, value: key });
            }
            this.ShipToOptions = optionsA;
            //Initialze selection to first value in combobox and publish message for detail components
            this.singleorderShipto = this.orderShipto[0];
//           this.filters.shipToName = this.orderShipto[0].Name;
            this.value = this.orderShipto[0].Name;
            this.filters.shipToName = this.value.replace(/\'/,"\\'");
            //            this.districtName = this.orderShipto[0].DistrictName;
            //            this.parent = this.orderShipto[0].Parent;
            //            this.ultimateParent = this.orderShipto[0].UltimateParent;
            //            this.customerPO = this.orderShipto[0].CustomerPO;
            this.sendFilterMessage();
            //console.log('OrderShiptoA_valuesDataData0-->' + JSON.stringify(this.orderShipto[0]));
        } else if (error) {
            console.log('OrderShipto_error -->' + error);
        } else {
            console.log('OrderShipto_nodata -->');
            // Reset select if no data
            this.value = this.filters.shipToName;
            this.singleorderShipto = {};
        }
    }

    connectedCallback() {
        this.filters.PQ = this.orderPQ;
        console.log('B_OrderStatusFilterShipto_Filter-->' + JSON.stringify(this.filters));
    }

    handleFilterChange(message) {
        this.filters = { ...message.filters };
        console.log('B_OrderStatusFilterShipto_Filter-->' + JSON.stringify(this.filters));
        refreshApex();
    }

}