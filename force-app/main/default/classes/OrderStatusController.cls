public without sharing class OrderStatusController {

    //public static final String s1 = 'ship';
    //public static final String o1 = 'order';

    /*    ****************************************************************************************************************
    LUC - April 2023 - Get list of Ship To Accounts from Tracking_Information__c and Fulfillment_Sales_Order_Item__c filtered to PQ
    ****************************************************************************************************************    */
    @AuraEnabled(cacheable=true)
    public static list<OrderStatusWrappers.OrderShiptoWrapper> getOrderShipto(OrderStatusWrappers.Filters filters, Integer pageNumber){
        String key, tracking, shipToName, PQ, whereClause1, whereClause2 = '';
        // Build Where clause using filter values and static filters as needed (ie created date) - filter per object to support different fields
        if (filters != null) {
            tracking = filters.tracking;
            PQ = filters.PQ;
            shipToName = filters.shipToName;

            String[] criteria = new List<String>{};
            criteria.add('CreatedDate >= 2023-01-01T00:00:00-05:00');
            criteria.add('Portal_Status__c != \''+ 'UNKNOWN'+ '\'');
            criteria.add('Fulfillment__r.Opportunity__r.Quote_Number__c = \''+ PQ +'\'');
            //criteria.add('Fulfillment__r.Ship_to_Account__c = \''+ shipToName +'\'');
            //criteria.add('Tracking_Number__c = \''+ headerId +'\'');
            if (!String.isEmpty(filters.searchKey)) {
                key = '%' + filters.searchKey + '%';
               criteria.add('(Order_Fulfillment_Item__r.Product__r.Name LIKE \''+ key +'\' OR Order_Fulfillment_Item__r.Product__r.ISBN__c LIKE \''+ key +'\')');
            }
            if (criteria.size() > 0) {
                whereClause1 = ' WHERE ' + String.join(criteria, ' AND ');
            }

            String[] criteria2 = new List<String>{};
            criteria2.add('CreatedDate >= 2023-01-01T00:00:00-05:00');
            criteria2.add('Portal_Status__c != \''+ 'UNKNOWN'+ '\'');
            criteria2.add('Fulfillment_Sales_Order__r.Opportunity__r.Quote_Number__c = \''+ PQ +'\'');
            //criteria2.add('Fulfillment_Sales_Order__r.Ship_To_School__c = \''+ shipToName +'\'');
            //criteria2.add('Tracking_Number__c = \''+ headerId +'\'');
            if (!String.isEmpty(filters.searchKey)) {
                key = '%' + filters.searchKey + '%';
               criteria2.add('(Product__r.Name LIKE \''+ key +'\' OR Product__r.ISBN__c LIKE \''+ key +'\')');
            }
            if (criteria2.size() > 0) {
                whereClause2 = ' WHERE ' + String.join(criteria2, ' AND ');
            }
       }

        list<OrderStatusWrappers.OrderShiptoWrapper> OrderRecords = new list<OrderStatusWrappers.OrderShiptoWrapper>();
        String queryString1 = 'SELECT Id, Fulfillment__r.Opportunity__r.Account.Name, Fulfillment__r.Opportunity__r.Account.Parent_Account_Name__c, Fulfillment__r.Opportunity__r.Account.Ultimate_Parent_Account__c, Fulfillment__r.Fulfillment_Sales_Order__r.Customer_PO_Number__c, Fulfillment__r.Opportunity__r.PO__c, Fulfillment__r.Ship_to_Account__c, Fulfillment__r.Ship_to_Contact__c, Fulfillment__r.Shipment_Date__c, Fulfillment__r.Shipping_City__c, Fulfillment__r.Shipping_Country__c, Fulfillment__r.Shipping_Postal_Code__c, Fulfillment__r.Shipping_State__c, Fulfillment__r.Shipping_Street__c FROM Tracking_Information__c  ' 
        + whereClause1;
        List<Tracking_Information__c> shipList = Database.query(queryString1);
        String queryString2 = 'SELECT Id, Fulfillment_Sales_Order__r.Opportunity__r.PO__c, Fulfillment_Sales_Order__r.Customer_PO_Number__c, Fulfillment_Sales_Order__r.Ship_To_Contact__c, Fulfillment_Sales_Order__r.Ship_To_School__c, Fulfillment_Sales_Order__r.Shipping_City__c, Fulfillment_Sales_Order__r.Shipping_Country__c, Fulfillment_Sales_Order__r.Shipping_Postal_Code__c, Fulfillment_Sales_Order__r.Shipping_State__c, Fulfillment_Sales_Order__r.Shipping_Street__c, Fulfillment_Sales_Order__r.Opportunity__r.Account.Name, Fulfillment_Sales_Order__r.Opportunity__r.Account.Parent_Account_Name__c, Fulfillment_Sales_Order__r.Opportunity__r.Account.Ultimate_Parent_Account__c FROM Fulfillment_Sales_Order_Item__c  '
        + whereClause2;
        List<Fulfillment_Sales_Order_Item__c> orderList = Database.query(queryString2);
        for(Fulfillment_Sales_Order_Item__c o: orderList){
            OrderStatusWrappers.OrderShiptoWrapper oWrap = new OrderStatusWrappers.OrderShiptoWrapper();
            oWrap.Id = o.Id;
            //oWrap.QueryString1 = queryString1;
            //oWrap.QueryString2 = queryString2;
            oWrap.Name = o.Fulfillment_Sales_Order__r.Ship_To_School__c;
            oWrap.ShipToStreet = o.Fulfillment_Sales_Order__r.Shipping_Street__c;
            oWrap.ShipToCity = o.Fulfillment_Sales_Order__r.Shipping_City__c;
            oWrap.ShipToState = o.Fulfillment_Sales_Order__r.Shipping_State__c;
            oWrap.ShipToZip = o.Fulfillment_Sales_Order__r.Shipping_Postal_Code__c;
            oWrap.ShipToContact = o.Fulfillment_Sales_Order__r.Ship_To_Contact__c;
            oWrap.ShipToCountry = o.Fulfillment_Sales_Order__r.Shipping_Country__c;
            oWrap.Parent = o.Fulfillment_Sales_Order__r.Opportunity__r.Account.Parent_Account_Name__c;
            oWrap.UltimateParent = o.Fulfillment_Sales_Order__r.Opportunity__r.Account.Ultimate_Parent_Account__c;
            oWrap.CustomerPO = o.Fulfillment_Sales_Order__r.Customer_PO_Number__c;
            oWrap.RowCount = '1'; //used to be aggregate query - now detail - grouped in LWC js
            oWrap.DistrictName = o.Fulfillment_Sales_Order__r.Opportunity__r.Account.Name;
            OrderRecords.add(oWrap);
        }
        for(Tracking_Information__c s: shipList){
            OrderStatusWrappers.OrderShiptoWrapper sWrap = new OrderStatusWrappers.OrderShiptoWrapper();
            sWrap.Id = s.Id;
            //sWrap.QueryString1 = queryString1;
            //sWrap.QueryString2 = queryString2;
            sWrap.Name = s.Fulfillment__r.Ship_to_Account__c;
            sWrap.ShipToStreet = s.Fulfillment__r.Shipping_Street__c;
            sWrap.ShipToCity = s.Fulfillment__r.Shipping_City__c;
            sWrap.ShipToState = s.Fulfillment__r.Shipping_State__c;
            sWrap.ShipToZip = s.Fulfillment__r.Shipping_Postal_Code__c;
            sWrap.ShipToContact = s.Fulfillment__r.Ship_to_Contact__c;
            sWrap.ShipToCountry = s.Fulfillment__r.Shipping_Country__c;
            sWrap.Parent = s.Fulfillment__r.Opportunity__r.Account.Parent_Account_Name__c;
            sWrap.UltimateParent = s.Fulfillment__r.Opportunity__r.Account.Ultimate_Parent_Account__c;
            sWrap.CustomerPO = s.Fulfillment__r.Fulfillment_Sales_Order__r.Customer_PO_Number__c;
            sWrap.RowCount = '1'; //used to be aggregate query - now detail - grouped in LWC js
            sWrap.DistrictName = s.Fulfillment__r.Opportunity__r.Account.Name;
            OrderRecords.add(sWrap);
        }
        OrderRecords.sort();
        system.debug('*****OrderRecords***** >> ' + OrderRecords);
        return OrderRecords;
    }

    /*    ****************************************************************************************************************
    LUC - April 2023 - Get list of Tracking Numbers or Estimated Ship Dates from Tracking_Information__c and Fulfillment_Sales_Order_Item__c filtered to PQ and ShipTo
    ****************************************************************************************************************    */
    @AuraEnabled(cacheable=true)
    public static list<OrderStatusWrappers.OrderHeaderWrapper> getOrderHeader(OrderStatusWrappers.Filters filters, Integer pageNumber){
        String key, sv, tracking, shipToName, PQ, status, whereClause1, whereClause2 = '';
        // Build Where clause using filter values and static filters as needed (ie created date) - filter per object to support different fields
        if (filters != null) {
            tracking = filters.tracking;
            PQ = filters.PQ;
            shipToName = filters.shipToName;

            String[] criteria = new List<String>{};
            criteria.add('CreatedDate >= 2023-01-01T00:00:00-05:00');
            criteria.add('Portal_Status__c != \''+ 'UNKNOWN'+ '\'');
            criteria.add('Fulfillment__r.Opportunity__r.Quote_Number__c = \''+ PQ +'\'');
            criteria.add('Fulfillment__r.Ship_to_Account__c = \''+ shipToName +'\'');
            if (!String.isEmpty(filters.status)) {
                sv = '%' + filters.status + '%';
                criteria.add('Portal_Status__c LIKE \''+ sv +'\'');
            }
            //criteria.add('Tracking_Number__c = \''+ headerId +'\'');
            if (!String.isEmpty(filters.searchKey)) {
                key = '%' + filters.searchKey + '%';
                criteria.add('(Order_Fulfillment_Item__r.Product__r.Name LIKE \''+ key +'\' OR Order_Fulfillment_Item__r.Product__r.ISBN__c LIKE \''+ key +'\')');
            }
            if (criteria.size() > 0) {
                whereClause1 = ' WHERE ' + String.join(criteria, ' AND ');
            }

            String[] criteria2 = new List<String>{};
            criteria2.add('CreatedDate >= 2023-01-01T00:00:00-05:00');
            criteria2.add('Portal_Status__c != \''+ 'UNKNOWN'+ '\'');
            criteria2.add('(Product__c != NULL OR Parent_ISBN__c != NULL)');
            criteria2.add('Fulfillment_Sales_Order__r.Opportunity__r.Quote_Number__c = \''+ PQ +'\'');
            criteria2.add('Fulfillment_Sales_Order__r.Ship_To_School__c = \''+ shipToName +'\'');
            if (!String.isEmpty(filters.status)) {
                sv = '%' + filters.status + '%';
                criteria2.add('Portal_Status__c LIKE \''+ sv +'\'');
            }
            //criteria2.add('Tracking_Number__c = \''+ headerId +'\'');
            if (!String.isEmpty(filters.searchKey)) {
                key = '%' + filters.searchKey + '%';
                criteria2.add('(Product__r.Name LIKE \''+ key +'\' OR Product__r.ISBN__c LIKE \''+ key +'\')');
            }
            if (criteria2.size() > 0) {
                whereClause2 = ' WHERE ' + String.join(criteria2, ' AND ');
            }
        }

        list<OrderStatusWrappers.OrderHeaderWrapper> OrderRecords = new list<OrderStatusWrappers.OrderHeaderWrapper>();
        String queryString1 = 'SELECT Id, Tracking_Number__c, Fulfillment__r.Status__c, Fulfillment__r.InternalId__c, Carrier__c, Fulfillment__r.Shipment_Date__c, Tracking_Link_for_Portal__c, Portal_Status__c FROM Tracking_Information__c '
        + whereClause1 + ' ORDER BY Tracking_Number__c ASC NULLS LAST';
        List<Tracking_Information__c> shipList = Database.query(queryString1);
        String queryString2 = 'SELECT Id, Flight_Start_Date__c, Estimated_Delivery_Date_1__c, Expected_Ship_Date_Confirmed__c, No_Supply__c, Delivery_Date_Display_Message__c, Fulfillment_Sales_Order__r.Status__c, Fulfillment_Sales_Order__r.InternalId__c, Portal_Status__c FROM Fulfillment_Sales_Order_Item__c '
        + whereClause2 + ' ORDER BY Estimated_Delivery_Date_1__c ASC NULLS LAST';
        List<Fulfillment_Sales_Order_Item__c> orderList = Database.query(queryString2);
        for(Fulfillment_Sales_Order_Item__c o: orderList){
            OrderStatusWrappers.OrderHeaderWrapper oWrap = new OrderStatusWrappers.OrderHeaderWrapper();
            oWrap.Id = o.Id;
            oWrap.Name = o.Delivery_Date_Display_Message__c;

            /*if( String.isEmpty(String.valueOf(o.Estimated_Delivery_Date_1__c))) {
                oWrap.DetailFilter = 'NULL';
            } else {
                oWrap.DetailFilter = String.valueOf(o.Estimated_Delivery_Date_1__c);
            }*/

            oWrap.DetailFilter = o.Delivery_Date_Display_Message__c;
            //oWrap.DetailFilter = String.valueOf(o.Estimated_Delivery_Date_1__c);
            //oWrap.QueryString1 = queryString1;
            //oWrap.QueryString2 = queryString2;
            oWrap.GroupItem = 'order';
            oWrap.Status =   o.Portal_Status__c; // o.Fulfillment_Sales_Order__r.Status__c;
            oWrap.InternalId = o.Fulfillment_Sales_Order__r.InternalId__c;
            oWrap.TrackingLinkPortal2 = '';
            oWrap.RowCount = '1';
            oWrap.DisplayTracking = false;
            OrderRecords.add(oWrap);
        }
        for(Tracking_Information__c s: shipList){
            OrderStatusWrappers.OrderHeaderWrapper sWrap = new OrderStatusWrappers.OrderHeaderWrapper();
            sWrap.Id = s.Id;
            sWrap.Name = 'TRACKING NUMBER:' + s.Tracking_Number__c;
            sWrap.DetailFilter = s.Tracking_Number__c;
            //sWrap.QueryString1 = queryString1;
            //sWrap.QueryString2 = queryString2;
            sWrap.GroupItem = 'ship';
            sWrap.Status = s.Portal_Status__c;       // s.Fulfillment__r.Status__c;
            sWrap.InternalId = s.Fulfillment__r.InternalId__c;
            sWrap.Carrier = s.Carrier__c;
            sWrap.RowCount = '1';
            sWrap.ShipDate = String.valueOf(s.Fulfillment__r.Shipment_Date__c.format());
            sWrap.TrackingLinkPortal2 = s.Tracking_Link_for_Portal__c;
            sWrap.DisplayTracking = true;
            OrderRecords.add(sWrap);
        }
        system.debug('*****OrderRecords***** >> ' + OrderRecords);
        return OrderRecords;
    }

    /*    ****************************************************************************************************************
    LUC - April 2023 - Get detail list of Products in each Tracking or Estimated Ship Dates from Tracking_Information__c and Fulfillment_Sales_Order_Item__c filtered to PQ and ShipTo and GroupFilter (Tracking Number or Estimated Ship Date)
            -Future enhancement - split query for ship v order details
    ****************************************************************************************************************    */
    @AuraEnabled(cacheable=true)
    public static list<OrderStatusWrappers.OrderDetailWrapper> getOrderDetail(String headerId, String groupItem, OrderStatusWrappers.Filters filters, Integer pageNumber){
        String key, groupitem1, groupitem2, tracking, shipToName, PQ, whereClause1, whereClause2 = '';
        // Build Where clause using filter values and static filters as needed (ie created date) - filter per object to support different fields
        if (filters != null) {
            tracking = filters.tracking;
            PQ = filters.PQ;
            shipToName = filters.shipToName;

            String[] criteria = new List<String>{};
            criteria.add('CreatedDate >= 2023-01-01T00:00:00-05:00');
            criteria.add('Portal_Status__c != \''+ 'UNKNOWN'+ '\'');
            criteria.add('Fulfillment__r.Opportunity__r.Quote_Number__c = \''+ PQ +'\'');
            criteria.add('Fulfillment__r.Ship_to_Account__c = \''+ shipToName +'\'');
            criteria.add('Tracking_Number__c = \''+ headerId +'\'');
            if (!String.isEmpty(filters.searchKey)) {
                key = '%' + filters.searchKey + '%';
                criteria.add('(Order_Fulfillment_Item__r.Product__r.Name LIKE \''+ key +'\' OR Order_Fulfillment_Item__r.Product__r.ISBN__c LIKE \''+ key +'\')');
            }
            if (criteria.size() > 0) {
                whereClause1 = ' WHERE ' + String.join(criteria, ' AND ');
            }

            String[] criteria2 = new List<String>{};
            criteria2.add('CreatedDate >= 2023-01-01T00:00:00-05:00');
            criteria2.add('Portal_Status__c != \''+ 'UNKNOWN'+ '\'');
            criteria2.add('(Product__c != NULL OR Parent_ISBN__c != NULL)');
            criteria2.add('Fulfillment_Sales_Order__r.Opportunity__r.Quote_Number__c = \''+ PQ +'\'');
            criteria2.add('Fulfillment_Sales_Order__r.Ship_To_School__c = \''+ shipToName +'\'');
                if(groupItem == 'order'){
                    criteria2.add('Delivery_Date_Display_Message__c = \''+ headerId +'\'');
                } else { //If groupItem = 'sales' (for tracking information), we don't want to return any FSOIs. So we query them by a random Delivery Date Display Message value.
                    criteria2.add('Delivery_Date_Display_Message__c = \'Invalid delivery date display message\'');
                }

            if (!String.isEmpty(filters.searchKey)) {
                key = '%' + filters.searchKey + '%';
            criteria2.add('(Product__r.Name LIKE \''+ key +'\' OR Product__r.ISBN__c LIKE \''+ key +'\')');
            }
            if (criteria2.size() > 0) {
                whereClause2 = ' WHERE ' + String.join(criteria2, ' AND ');
            }
        }

        list<OrderStatusWrappers.OrderDetailWrapper> OrderRecords = new list<OrderStatusWrappers.OrderDetailWrapper>();
        String queryString1 = 'SELECT Id, Carrier__c, CreatedDate, Fulfillment__r.Opportunity__r.PO__c, Fulfillment__r.Shipped_Date__c, Fulfillment__r.Status__c, ISBN__c, Quantity__c, Tracking_Number__c, Order_Fulfillment_Item__r.Ordered_Quantity__c, Order_Fulfillment_Item__r.Product__r.Name, Order_Fulfillment_Item__r.Product__r.ISBN__c, Order_Fulfillment_Item__r.FSO_Product_Name__c, Order_Fulfillment_Item__r.FSO_Product_ISBN__c FROM Tracking_Information__c ' 
        + whereClause1;
        system.debug(querystring1);
        List<Tracking_Information__c> shipList = Database.query(queryString1);
        String queryString2 = 'SELECT Id, Product_Name__c, Product_ISBN__c, Acknowledgement_Item_Status__c, CreatedDate, Expected_Ship_Date_Confirmed__c, No_Supply__c, Delivery_Date_Display_Message__c, Estimated_Delivery_Date_1__c, Fulfillment_Sales_Order__r.Opportunity__r.PO__c, Fulfillment_Sales_Order__r.Order_Date__c, Product__r.ISBN__c, Product__r.Name, Quantity_Ordered__c, Quantity_Fulfilled__c FROM Fulfillment_Sales_Order_Item__c '
        + whereClause2;
        system.debug(querystring2);
        List<Fulfillment_Sales_Order_Item__c> orderList = Database.query(queryString2);

        for(Tracking_Information__c s: shipList){
            OrderStatusWrappers.OrderDetailWrapper sWrap = new OrderStatusWrappers.OrderDetailWrapper();
            sWrap.Id = s.Id;
            //sWrap.QueryString1 = queryString1;
            //sWrap.QueryString2 = queryString2;
            sWrap.Name = s.Order_Fulfillment_Item__r.FSO_Product_ISBN__c;
            sWrap.Quantity = s.Order_Fulfillment_Item__r.Ordered_Quantity__c;
            sWrap.ShippedQty = s.Quantity__c;
//            sWrap.Product = s.Order_Fulfillment_Item__r.Product__r.Name;
//            sWrap.Product = s.Order_Fulfillment_Item__r.Fulfillment_Sales_Order_Item__r.Product__r.Name;
            sWrap.Product = s.Order_Fulfillment_Item__r.FSO_Product_Name__c;
            sWrap.DisplayTracking = true;
            OrderRecords.add(sWrap);
        }
        for(Fulfillment_Sales_Order_Item__c o: orderList){
            OrderStatusWrappers.OrderDetailWrapper oWrap = new OrderStatusWrappers.OrderDetailWrapper();
            oWrap.Id = o.Id;
            //oWrap.QueryString1 = queryString1;
            //oWrap.QueryString2 = queryString2;
            oWrap.Name = o.Product_ISBN__c;
            oWrap.Quantity = o.Quantity_Ordered__c;
            oWrap.ShippedQty = o.Quantity_Fulfilled__c;
            oWrap.Product = o.Product_Name__c;
            oWrap.DisplayTracking = false;
            OrderRecords.add(oWrap);
        }
        system.debug('*****OrderRecords-DETAIL****** >> ' + OrderRecords);
        return OrderRecords;
    }

}