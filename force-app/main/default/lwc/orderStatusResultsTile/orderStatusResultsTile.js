import { LightningElement, api, wire } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';
import userId from '@salesforce/user/Id';

import getOrderDetail from '@salesforce/apex/OrderStatusController.getOrderDetail';
import createEvent from '@salesforce/apex/PortalTrackingController.createEvent';
import { refreshApex } from '@salesforce/apex';

import { subscribe, MessageContext } from 'lightning/messageService';
import ORDERS_FILTERED_MESSAGE from '@salesforce/messageChannel/OrdersFiltered__c';
import ORDERSSHIPTO_FILTERED_MESSAGE from '@salesforce/messageChannel/OrdersShipToFiltered__c';
import ORDERSPQ_FILTERED_MESSAGE from '@salesforce/messageChannel/OrdersPQFiltered__c';
import { parseDeviceType, parseBrowser, parseOS, parseScreenSize, parseViewport, parseLanguage, parseTimezone } from 'c/portalTrackerUtils';

const SESSION_KEY     = 'portal_session_id';
const IS_INTERNAL_KEY = 'portal_is_internal';

export default class OrderStatusResultsTile extends NavigationMixin(LightningElement) {
    @api filters;
    @api listdata; //orderheader results fields
    @api headerid;
    @api groupitem;
    orderDetail; //orderdetail results fields

    /**getting flow variables from orderStatusFilterOrder component */
    @api orderPQ;

    /** JSON.stringified version of filters to pass to apex */
    filters = {};
    /* this passes value to apex - initial value '' */
    filters = {
        searchKey: '',
        isbn: '',
        PQ: '',
        shipToName: '',
        tracking: '',
        status: ''
    };

    /** Load context for Lightning Messaging Service */
    @wire(MessageContext) messageContext;

    // Use lower case filters: '$filters' ----
    @wire(getOrderDetail, { headerId: '$headerid', groupItem: '$groupitem', filters: '$filters', pageNumber: '1' })
    level1dataC(data, error) {
        if (data && JSON.stringify(data).length != 2 && JSON.stringify(data).length != 11) {
            this.orderDetail = data.data;
            console.log('Z7_OrderStatusResultsTile_QUERY_Filter-->' + 'HDR:' + this.headerId + '-' + JSON.stringify(this.filters));
            // ************************* use to monitor SOQL
            console.log('Z6_OrderDetail_SOQL1-->' + this.orderDetail[0].QueryString1);
            console.log('Z5_OrderDetail_SOQL2-->' + this.orderDetail[0].QueryString2);
            // *************************
        } else if (error) {
            console.log('OrderDetail_error -->' + error);
        } else {
            console.log('Y_OrderDetail_nodata -->');
            console.log('Y_OrderDetail_nodata_Filter-->' + JSON.stringify(this.filters));
            this.orderDetail = [];  // Reset orderDetail on change
            console.log('Y_OrderDetail_nodata_valuesData-->' + JSON.stringify(data));
        }
    }

    connectedCallback() {
        console.log('M1_OrderStatusResultsTile-->' + 'HDR:' + this.headerId + '-' + JSON.stringify(this.filters));
        // Subscribe to OrdersFiltered message to filter the orders Order_Fulfillments__c
        this.orderFilterSubscription = subscribe(
            this.messageContext,
            ORDERS_FILTERED_MESSAGE,
            (message) => this.handleFilterChange(message)
        );
        // Subscribe to OrdersFiltered message to filter the orders Order_Fulfillments__c
        this.orderFilterSubscription = subscribe(
            this.messageContext,
            ORDERSSHIPTO_FILTERED_MESSAGE,
            (message) => this.handleFilterChange(message)
        );
        // Subscribe to OrdersFiltered message to filter the orders Order_Fulfillments__c
        this.orderFilterSubscription = subscribe(
            this.messageContext,
            ORDERSPQ_FILTERED_MESSAGE,
            (message) => this.handleFilterChange(message)
        );
        console.log('M2_OrderStatusResultsTile-->' + 'HDR:' + this.headerId + '-' + JSON.stringify(this.filters));
    }

    handleFilterChange(message) {
        this.filters = { ...message.filters };
        console.log('Z_OrderStatusResultsTile_Filter-->' + JSON.stringify(this.filters));
        refreshApex();
    }

    /** View Tracking Handler to navigates to external Tracking_Number_Link__c */
  handleTrackingClick() {
       this.trackShipmentClick();
       this[NavigationMixin.Navigate]({
              type: 'standard__webPage',
              attributes: {
                 url: this.listdata.TrackingLinkPortal2
             }
          });
       }

    /**
     * Fires a Portal_Analytics__c event for the Track Shipment click. This button
     * navigates to an external carrier tracking page via NavigationMixin rather than
     * a plain <a> tag, so portalTracker's global external-link listener never sees it —
     * track it directly here instead, the same way portalTracker does for external links.
     */
    trackShipmentClick() {
        try {
            const sessionId  = sessionStorage.getItem(SESSION_KEY);
            const isInternal = sessionStorage.getItem(IS_INTERNAL_KEY) === 'true';

            createEvent({
                sessionId,
                pageName    : document.title || null,
                pageUrl     : this.listdata.TrackingLinkPortal2,
                referrerUrl : window.location.href,
                eventType   : 'SSP - Track Shipment Clicked',
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
            }).catch(error => console.error('[OrderStatusResultsTile] Track Shipment click tracking failed:', error));
        } catch (e) {
            console.error('[OrderStatusResultsTile] Track Shipment click tracking failed:', e);
        }
    }

}