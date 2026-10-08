import { LightningElement, api, track, wire } from 'lwc';

// Lightning Message Service and message channels
import { publish, subscribe, MessageContext } from 'lightning/messageService';
import ORDERS_FILTERED_MESSAGE from '@salesforce/messageChannel/OrdersFiltered__c';
import ORDERSSHIPTO_FILTERED_MESSAGE from '@salesforce/messageChannel/OrdersShipToFiltered__c';
import ORDERSPQ_FILTERED_MESSAGE from '@salesforce/messageChannel/OrdersPQFiltered__c';
import SHIPMENTCOUNTS_MESSAGE from '@salesforce/messageChannel/OrdersShipmentCounts__c';



import getOrderHeader from '@salesforce/apex/OrderStatusController.getOrderHeader';
import { refreshApex } from '@salesforce/apex';

import userId from '@salesforce/user/Id';
import createEvent from '@salesforce/apex/PortalTrackingController.createEvent';
import { parseDeviceType, parseBrowser, parseOS, parseScreenSize, parseViewport, parseLanguage, parseTimezone } from 'c/portalTrackerUtils';

const SESSION_KEY     = 'portal_session_id';
const IS_INTERNAL_KEY = 'portal_is_internal';

export default class OrderStatusResults extends LightningElement {
    orderHeader;
    orderHeader1;
    orderHeader_prior;
    @track shipCount = 0;
    @track multiship = 0; // controls multi-shipment message in html.
    @track showdata = 0;  // if 1 shows data results. used in if
    @track nodata = 0;    // if 1 shows no data found in html. used in elseif

    // ******** confir if still needed !
    /**getting flow variables from orderStatusFilterOrder component */
    @api orderPQ;

    /** JSON.stringified version of filters to pass to apex */
    filters = {};
    /* this passes value to apex - initial value -none- to clear on load  */
    filters = {
        //searchKey: '',
        isbn: '',
        PQ: '-none-',
        shipToName: '-none-',
        tracking: '',
        //status: ''
    };

    shipments = {};
    shipments = {
        total: '',
        processing: '',
        shipped: '',
        delivered: ''
    };



    /** Load context for Lightning Messaging Service */
    @wire(MessageContext)
    messageContext;


    sendShipmentsMessage() {
        console.log('OrderStatusResults_SHIPMENTS-SENDtoFilter-->' + JSON.stringify(this.shipments));
        publish(this.messageContext, SHIPMENTCOUNTS_MESSAGE, {
            shipments: this.shipments
        });
        return true;
    }

    //    sendFilterMessage() {
    //        console.log('OrderStatusResults_Filter-SENDtoTile-->' + JSON.stringify(this.filters));
    //        publish(this.messageContext, ORDERSSHIPTO_FILTERED_MESSAGE, {
    //            filters: this.filters
    //        });
    //    }



    /* call Apex method in OrderStatusController */
    @wire(getOrderHeader, { filters: '$filters', pageNumber: '1' })
    level1dataA(data, error) {
        if (error) {
            // console.log('OrderHeaderz1_error -->' + error);
        } else if (data && JSON.stringify(data).length != 2 && JSON.stringify(data).length != 11) {
            this.shipCount = 0;
            this.multiship = 0;
            this.showdata = 0;
            this.nodata = 0;
            this.shipments.total = 0;
            this.shipments.processing = 0;
            this.shipments.shipped = 0;
            this.shipments.delivered = 0;
            this.orderHeader = [];  // Reset orderHeader on ShipTo change
            this.orderHeader_prior = [];  //Reset orderHeader prior value at start of loop
            this.orderHeader1 = data.data;
            //console.log('OrderStatusResults_DataDetail-->' + JSON.stringify(data));
            console.log('OrderStatusResults_DataObject-->' + data);
            console.log('OrderStatusResults_QueryFilter-->' + JSON.stringify(this.filters));
            //console.log('OrderStatusResults_orderHeader_QueryString1-->' + JSON.stringify(this.orderHeader1[0], ["QueryString1"]));
            //console.log('OrderStatusResults_orderHeader_QueryString2-->' + JSON.stringify(this.orderHeader1[0], ["QueryString2"]));

            for (var key in this.orderHeader1) {
                if (this.orderHeader1[key].Name) {
                    if (!this.orderHeader_prior.includes(this.orderHeader1[key].Name)) {
                        if (this.orderHeader) {
                            this.orderHeader = [...this.orderHeader, this.orderHeader1[key]];
                            this.shipCount++;
                            this.shipments.total++;
                        } else {
                            this.orderHeader = [this.orderHeader1[key]];
                            this.shipCount = 1;
                            this.shipments.total = 1;
                        }
                        if (this.orderHeader1[key].Status === "Preparing Your Order")
                            this.shipments.processing++;

                        if (this.orderHeader1[key].Status === "Shipped")
                            this.shipments.shipped++;

                        if (this.orderHeader1[key].Status === "Delivered")
                            this.shipments.delivered++;
                    }
                    if (this.shipments.total > 1)
                        this.multiship = 1;

                    if (this.shipments.total > 0) {
                        this.showdata = 1;
                    } else {
                        this.showdata = 0;
                        this.nodata = 1;
                    }
                }
                this.orderHeader_prior.push(this.orderHeader1[key].Name);

            }
            console.log('OrderHeaderA1_valuesDataDataNamesB2-->' + JSON.stringify(this.orderHeader, ["Name"]));
            console.log('OrderHeaderA1_valuesDataDataDetailFilter-->' + JSON.stringify(this.orderHeader, ["DetailFilter"]));
            console.log('OrderHeaderA1_valuesDataDataGroupItem-->' + JSON.stringify(this.orderHeader, ["GroupItem"]));
            this.filters.shipCount = this.shipCount;

            //           console.log('OrderStatusResults_SHIPMENTS-SENDtoFilterA-->' + JSON.stringify(this.shipments));
            publish(this.messageContext, SHIPMENTCOUNTS_MESSAGE, {
                shipments: this.shipments
            });


            console.log('OrderHeaderA1_shipCount-->' + this.shipCount);



        } else {
            //           console.log('OrderHeaderz1_nodata -->');
            this.shipCount = 0;
            this.multiship = 0;
            this.showdata = 0;
            this.nodata = 1;

            this.shipments = {
                total: 0,
                processing: 0,
                shipped: 0,
                delivered: 0
            };
            /*
            console.log('OrderStatusResults_SHIPMENTS-SENDtoFilterB-->' + JSON.stringify(this.shipments));
            publish(this.messageContext, SHIPMENTCOUNTS_MESSAGE, {shipments: this.shipments
            });
            */
            this.orderHeader = [];  // Reset orderHeader on filter no data
        }


    }




    connectedCallback() {
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
    }

    handleFilterChange(message) {
        this.filters = { ...message.filters };
        //        this.pageNumber = 1;
        //       this.shipments = { ...message.shipments };
        console.log('Z_OrderStatusResults_Filter-->' + JSON.stringify(this.filters));

        refreshApex();
    }

    /**
     * Fires a Portal_Analytics__c event when the user clicks the help@amplify.com
     * link shown in the no-data state.
     */
    handleHelpEmailClick() {
        try {
            const sessionId  = sessionStorage.getItem(SESSION_KEY);
            const isInternal = sessionStorage.getItem(IS_INTERNAL_KEY) === 'true';

            createEvent({
                sessionId,
                pageName    : document.title || null,
                pageUrl     : 'mailto:help@amplify.com',
                referrerUrl : window.location.href,
                eventType   : 'SSP - Help Email Link Clicked',
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
            }).catch(error => console.error('[OrderStatusResults] tracking failed:', error));
        } catch (e) {
            console.error('[OrderStatusResults] tracking failed:', e);
        }
    }

    //    handlePreviousPage() {
    //       this.pageNumber = this.pageNumber - 1;
    //   }

    //   handleNextPage() {
    //       this.pageNumber = this.pageNumber + 1;
    //   }

}