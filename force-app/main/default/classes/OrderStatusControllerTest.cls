@isTest
public class OrderStatusControllerTest {

    @IsTest
    static void testGetOrderShipto() {
        // Step 1: Set up the necessary test data
        OrderStatusWrappers.Filters filters = new OrderStatusWrappers.Filters();
        filters.tracking = 'XYZ123';
        //filters.PQ = 'ABC123';
        filters.shipToName = 'TAcct';
        filters.searchKey = '123456';

        // Create sample records for Tracking_Information__c and Fulfillment_Sales_Order_Item__c

        //Account
        Account AcctIns = new Account();
            AcctIns.Name='TAcct';
        insert AcctIns;

        //Product   (ISBN / Name)
        Product2 ProdIns = new Product2();
            ProdIns.ProductCode = 'ABC123';
            ProdIns.Name = 'TProduct';
            ProdIns.ISBN__c = '123456';
        insert ProdIns;

        //Opportunity
        Opportunity OppIns = new Opportunity();
            OppIns.AccountId = AcctIns.Id;
            OppIns.Name = 'TOpp';
            OppIns.StageName = 'Discovery';
            OppIns.CloseDate = Date.newInstance(2023, 01, 01);
            //Quote_Number__c;
        insert OppIns;

        OppIns = [select Id, Quote_Number__c from Opportunity where id = : OppIns.id]; //Get PQ Number (AutoNumber) after Opp Insert
        filters.PQ = OppIns.Quote_Number__c;

        //Fulfillment Sales Order
        Fulfillment_Sales_Order__c FulSalesOrderIns = new Fulfillment_Sales_Order__c();
            FulSalesOrderIns.Customer_PO_Number__c = 'TPO';
            FulSalesOrderIns.Name = 'TFSO';
            FulSalesOrderIns.InternalId__c = 'ABC123';
            FulSalesOrderIns.Opportunity__c = OppIns.Id;
            FulSalesOrderIns.Ship_To_School__c = 'TAcct';
            FulSalesOrderIns.Ship_To_Contact__c = 'ABC123';
            FulSalesOrderIns.Shipping_Street__C = 'ABC123';
            FulSalesOrderIns.Shipping_City__c = 'ABC123';
            FulSalesOrderIns.Shipping_State__c = 'ABC123';
            FulSalesOrderIns.Shipping_Postal_Code__c = 'ABC123';
            FulSalesOrderIns.Shipping_Country__c = 'ABC123';
            FulSalesOrderIns.Status__c = 'Pending Fulfillment';
            //FulSalesOrderIns.XX = 'ABC123';
        insert FulSalesOrderIns;

        //Fulfillment Sales Order Item
        Fulfillment_Sales_Order_Item__c FulSalesOrderItemIns = new Fulfillment_Sales_Order_Item__c();
            FulSalesOrderItemIns.Quantity_Ordered__c = 1;
            FulSalesOrderItemIns.Product__c = ProdIns.Id;
            FulSalesOrderItemIns.Fulfillment_Sales_Order__c = FulSalesOrderIns.id;
            FulSalesOrderItemIns.Estimated_Delivery_Date_1__c = Date.newInstance(2023, 01, 01);
            FulSalesOrderItemIns.Estimated_Delivery_Date_2__c = Date.newInstance(2023, 01, 01);
            FulSalesOrderItemIns.Name = 'ABC123';
            //FulSalesOrderItemIns.XX = 'ABC123';
        insert FulSalesOrderItemIns;

        //Order Fulfillment
        Order_Fulfillment__c OrderFulIns = new Order_Fulfillment__c();
            OrderFulIns.Fulfillment_Sales_Order__c = FulSalesOrderIns.Id;
            OrderFulIns.Name = 'TFSO';
            OrderFulIns.InternalId__c = 'ABC123';
            OrderFulIns.Opportunity__c = OppIns.Id;
            OrderFulIns.Ship_To_Account__c = 'TAcct';
            OrderFulIns.Ship_To_Contact__c = 'ABC123';
            OrderFulIns.Shipping_Street__C = 'ABC123';
            OrderFulIns.Shipping_City__c = 'ABC123';
            OrderFulIns.Shipping_State__c = 'ABC123';
            OrderFulIns.Shipping_Postal_Code__c = 'ABC123';
            OrderFulIns.Shipping_Country__c = 'ABC123';
            OrderFulIns.Overall_Shipment_Status__c = 'Delivered';
            OrderFulIns.Status__c = 'Shipped';
            OrderFulIns.Shipment_Date__c = Date.newInstance(2023, 01, 01);
            //OrderFulIns.XX = 'ABC123';
        insert OrderFulIns;

        //Order Fulfillment Item
        Order_Fulfillment_Items__c OrderFulItemIns = new Order_Fulfillment_Items__c();
            OrderFulItemIns.Product__c = ProdIns.Id;
            OrderFulItemIns.Order_Fulfillment__c = OrderFulIns.Id;
            OrderFulItemIns.Ordered_Quantity__c = 1;
            //OrderFItemIns.XX = 'ABC123';
        insert OrderFulItemIns;

        //Tracking Information
        Tracking_Information__c TrackInfoIns = new Tracking_Information__c();
            TrackInfoIns.Tracking_Number__c = 'ABC123';
            TrackInfoIns.Carrier__c = 'ABC123';
            TrackInfoIns.Fulfillment__c = OrderFulIns.Id;
            TrackInfoIns.Order_FulFillment_Item__c = OrderFulItemIns.Id;
            TrackInfoIns.Quantity__c = 1;
            TrackInfoIns.Carrier_Code__c = 'FEDEX';
            //TrackInfoIns.XX = 'ABC123';
        insert TrackInfoIns;

        // Step 2: Call the getOrderDetail method
        List<OrderStatusWrappers.OrderShiptoWrapper> result = OrderStatusController.getOrderShipto(filters, 1);

        // Step 3: Perform assertions to verify the expected results or behavior
        System.assertEquals(2, result.size(), 'A1)Incorrect result size');

        //// Assert properties of the first OrderShiptoWrapper object in the result
        OrderStatusWrappers.OrderShiptoWrapper firstWrapper = result[0];
        System.assertEquals(FulSalesOrderItemIns.Id, firstWrapper.Id, 'A1)Incorrect Id value');
        //System.assertEquals('ExpectedQueryString1', firstWrapper.QueryString1, 'A1)Incorrect QueryString1 value');
        //System.assertEquals('ExpectedQueryString2', firstWrapper.QueryString2, 'A1)Incorrect QueryString2 value');
        System.assertEquals('TAcct', firstWrapper.Name, 'A1)Incorrect Name value');
        //System.assertEquals(null, firstWrapper.ShipToAccount, 'A1)Incorrect ShipToAccount value');
        System.assertEquals('ABC123', firstWrapper.ShipToStreet, 'A1)Incorrect ShipToStreet value');
        System.assertEquals('ABC123', firstWrapper.ShipToCity, 'A1)Incorrect ShipToCity value');
        System.assertEquals('ABC123', firstWrapper.ShipToState, 'A1)Incorrect ShipToState value');
        System.assertEquals('ABC123', firstWrapper.ShipToZip, 'A1)Incorrect ShipToZip value');
        System.assertEquals('ABC123', firstWrapper.ShipToContact, 'A1)Incorrect ShipToContact value');
        System.assertEquals('ABC123', firstWrapper.ShipToCountry, 'A1)Incorrect ShipToCountry value');
        //System.assertEquals('ABC123', firstWrapper.ShipmentDate, 'A1)Incorrect ShipmentDate value');
        System.assertEquals(null, firstWrapper.Parent, 'A1)Incorrect Parent value');
        System.assertEquals('TAcct', firstWrapper.UltimateParent, 'A1)Incorrect UltimateParent value');
        System.assertEquals('TPO', firstWrapper.CustomerPO, 'A1)Incorrect CustomerPO value');
        System.assertEquals('1', firstWrapper.RowCount, 'A1)Incorrect RowCount value');
        System.assertEquals('TAcct', firstWrapper.DistrictName, 'A1)Incorrect DistrictName value');

        //// Assert properties of the second OrderShiptoWrapper object in the result
        OrderStatusWrappers.OrderShiptoWrapper secondWrapper = result[1];
        System.assertEquals(TrackInfoIns.Id, secondWrapper.Id, 'B1)Incorrect Id value');
        //System.assertEquals('ExpectedQueryString1', secondWrapper.QueryString1, 'B1)Incorrect QueryString1 value');
        //System.assertEquals('ExpectedQueryString2', secondWrapper.QueryString2, 'B1)Incorrect QueryString2 value');
        System.assertEquals('TAcct', secondWrapper.Name, 'B1)Incorrect Name value');
        //System.assertEquals('ABC123', firstWrapper.ShipToAccount, 'A1)Incorrect ShipToAccount value');
        System.assertEquals('ABC123', secondWrapper.ShipToStreet, 'B1)Incorrect ShipToStreet value');
        System.assertEquals('ABC123', secondWrapper.ShipToCity, 'B1)Incorrect ShipToCity value');
        System.assertEquals('ABC123', secondWrapper.ShipToState, 'B1)Incorrect ShipToState value');
        System.assertEquals('ABC123', secondWrapper.ShipToZip, 'B1)Incorrect ShipToZip value');
        System.assertEquals('ABC123', secondWrapper.ShipToContact, 'B1)Incorrect ShipToContact value');
        System.assertEquals('ABC123', secondWrapper.ShipToCountry, 'B1)Incorrect ShipToCountry value');
        //System.assertEquals('ABC123', firstWrapper.ShipmentDate, 'A1)Incorrect ShipmentDate value');
        System.assertEquals(null, secondWrapper.Parent, 'B1)Incorrect Parent value');
        System.assertEquals('TAcct', secondWrapper.UltimateParent, 'B1)Incorrect UltimateParent value');
        System.assertEquals('TPO', secondWrapper.CustomerPO, 'B1)Incorrect CustomerPO value');
        System.assertEquals('1', secondWrapper.RowCount, 'B1)Incorrect RowCount value');
        System.assertEquals('TAcct', secondWrapper.DistrictName, 'B1)Incorrect DistrictName value');

    }

    @IsTest
    static void testGetOrderHeader() {
        // Step 1: Set up the necessary test data
        OrderStatusWrappers.Filters filters = new OrderStatusWrappers.Filters();
        filters.tracking = 'XYZ123';
        //filters.PQ = 'ABC123';
        filters.shipToName = 'TAcct';
        filters.searchKey = '123456';

        // Create sample records for Tracking_Information__c and Fulfillment_Sales_Order_Item__c

        //Account
        Account AcctIns = new Account();
            AcctIns.Name='TAcct';
        insert AcctIns;

        //Product   (ISBN / Name)
        Product2 ProdIns = new Product2();
            ProdIns.ProductCode = 'ABC123';
            ProdIns.Name = 'TProduct';
            ProdIns.ISBN__c = '123456';
        insert ProdIns;

        //Opportunity
        Opportunity OppIns = new Opportunity();
            OppIns.AccountId = AcctIns.Id;
            OppIns.Name = 'TOpp';
            OppIns.StageName = 'Discovery';
            OppIns.CloseDate = Date.newInstance(2023, 01, 01);
            //Quote_Number__c;
        insert OppIns;

        OppIns = [select Id, Quote_Number__c from Opportunity where id = : OppIns.id]; //Get PQ Number (AutoNumber) after Opp Insert
        filters.PQ = OppIns.Quote_Number__c;

        //Fulfillment Sales Order
        Fulfillment_Sales_Order__c FulSalesOrderIns = new Fulfillment_Sales_Order__c();
            FulSalesOrderIns.Customer_PO_Number__c = 'TPO';
            FulSalesOrderIns.Name = 'TFSO';
            FulSalesOrderIns.InternalId__c = 'ABC123';
            FulSalesOrderIns.Opportunity__c = OppIns.Id;
            FulSalesOrderIns.Ship_To_School__c = 'TAcct';
            FulSalesOrderIns.Ship_To_Contact__c = 'ABC123';
            FulSalesOrderIns.Shipping_Street__C = 'ABC123';
            FulSalesOrderIns.Shipping_City__c = 'ABC123';
            FulSalesOrderIns.Shipping_State__c = 'ABC123';
            FulSalesOrderIns.Shipping_Postal_Code__c = 'ABC123';
            FulSalesOrderIns.Shipping_Country__c = 'ABC123';
            FulSalesOrderIns.Status__c = 'Pending Fulfillment';
            //FulSalesOrderIns.XX = 'ABC123';
        insert FulSalesOrderIns;

        //Fulfillment Sales Order Item
        Fulfillment_Sales_Order_Item__c FulSalesOrderItemIns = new Fulfillment_Sales_Order_Item__c();
            FulSalesOrderItemIns.Quantity_Ordered__c = 1;
            FulSalesOrderItemIns.Product__c = ProdIns.Id;
            FulSalesOrderItemIns.Fulfillment_Sales_Order__c = FulSalesOrderIns.id;
            FulSalesOrderItemIns.Estimated_Delivery_Date_1__c = Date.newInstance(2023, 01, 01);
            FulSalesOrderItemIns.Estimated_Delivery_Date_2__c = Date.newInstance(2023, 01, 01);
            FulSalesOrderItemIns.Expected_Ship_Date_Confirmed__c = 'true';
            FulSalesOrderItemIns.No_Supply__c = 'false';
            FulSalesOrderItemIns.Name = 'ABC123';
            //FulSalesOrderItemIns.XX = 'ABC123';
        insert FulSalesOrderItemIns;

        //Order Fulfillment
        Order_Fulfillment__c OrderFulIns = new Order_Fulfillment__c();
            OrderFulIns.Fulfillment_Sales_Order__c = FulSalesOrderIns.Id;
            OrderFulIns.Name = 'TFSO';
            OrderFulIns.InternalId__c = 'ABC123';
            OrderFulIns.Opportunity__c = OppIns.Id;
            OrderFulIns.Ship_To_Account__c = 'TAcct';
            OrderFulIns.Ship_To_Contact__c = 'ABC123';
            OrderFulIns.Shipping_Street__C = 'ABC123';
            OrderFulIns.Shipping_City__c = 'ABC123';
            OrderFulIns.Shipping_State__c = 'ABC123';
            OrderFulIns.Shipping_Postal_Code__c = 'ABC123';
            OrderFulIns.Shipping_Country__c = 'ABC123';
            OrderFulIns.Overall_Shipment_Status__c = 'Delivered';
            OrderFulIns.Status__c = 'Shipped';
            OrderFulIns.Shipment_Date__c = Date.newInstance(2023, 01, 01);
            //OrderFulIns.XX = 'ABC123';
        insert OrderFulIns;

        //Order Fulfillment Item
        Order_Fulfillment_Items__c OrderFulItemIns = new Order_Fulfillment_Items__c();
            OrderFulItemIns.Product__c = ProdIns.Id;
            OrderFulItemIns.Order_Fulfillment__c = OrderFulIns.Id;
            OrderFulItemIns.Ordered_Quantity__c = 1;
            //OrderFItemIns.XX = 'ABC123';
        insert OrderFulItemIns;

        //Tracking Information
        Tracking_Information__c TrackInfoIns = new Tracking_Information__c();
            TrackInfoIns.Tracking_Number__c = 'ABC123';
            TrackInfoIns.Carrier__c = 'ABC123';
            TrackInfoIns.Fulfillment__c = OrderFulIns.Id;
            TrackInfoIns.Order_FulFillment_Item__c = OrderFulItemIns.Id;
            TrackInfoIns.Quantity__c = 1;
            TrackInfoIns.Carrier_Code__c = 'FEDEX';
            //TrackInfoIns.XX = 'ABC123';
        insert TrackInfoIns;

        // Step 2: Call the getOrderDetail method
        List<OrderStatusWrappers.OrderHeaderWrapper> result = OrderStatusController.getOrderHeader(filters, 1);

        // Step 3: Perform assertions to verify the expected results or behavior
        // Assert the size of the result
        System.assertEquals(2, result.size(), 'A2)Incorrect result size');

        //// Assert properties of the first OrderHeaderWrapper object in the result
        OrderStatusWrappers.OrderHeaderWrapper firstWrapper = result[0];
        System.assertEquals(FulSalesOrderItemIns.Id, firstWrapper.Id, 'A2)Incorrect Id value');
        System.assertEquals('ESTIMATED DELIVERY: 1/1/2023 - 1/1/2023', firstWrapper.Name, 'A2)Incorrect Name value');
        System.assertEquals('ESTIMATED DELIVERY: 1/1/2023 - 1/1/2023', firstWrapper.DetailFilter, 'A2)Incorrect DetailFilter value');
        //System.assertEquals('ExpectedQueryString1', firstWrapper.QueryString1, 'A2)Incorrect QueryString1 value');
        //System.assertEquals('ExpectedQueryString2', firstWrapper.QueryString2, 'A2)Incorrect QueryString2 value');
        System.assertEquals('order', firstWrapper.GroupItem, 'A2)Incorrect GroupItem value');
        System.assertEquals('Preparing Your Order', firstWrapper.Status, 'A2)Incorrect Status value');
        System.assertEquals('ABC123', firstWrapper.InternalId, 'A2)Incorrect InternalId value');
        System.assertEquals('', firstWrapper.TrackingLinkPortal2, 'A2)Incorrect TrackingLinkPortal2 value');
        System.assertEquals('1', firstWrapper.RowCount, 'A2)Incorrect RowCount value');
        System.assertEquals(false, firstWrapper.DisplayTracking, 'A2)Incorrect DisplayTracking value');

        //// Assert properties of the second OrderHeaderWrapper object in the result
        OrderStatusWrappers.OrderHeaderWrapper secondWrapper = result[1];
        System.assertEquals(TrackInfoIns.Id, secondWrapper.Id, 'B2)Incorrect Id value');
        System.assertEquals('TRACKING NUMBER:ABC123', secondWrapper.Name, 'B2)Incorrect Name value');
        System.assertEquals('ABC123', secondWrapper.DetailFilter, 'B2)Incorrect DetailFilter value');
        //System.assertEquals('ExpectedQueryString1', secondWrapper.QueryString1, 'B2)Incorrect QueryString1 value');
        //System.assertEquals('ExpectedQueryString2', secondWrapper.QueryString2, 'B2)Incorrect QueryString2 value');
        System.assertEquals('ship', secondWrapper.GroupItem, 'B2)Incorrect GroupItem value');
        System.assertEquals('Delivered', secondWrapper.Status, 'B2)Incorrect Status value');
        System.assertEquals('ABC123', secondWrapper.InternalId, 'B2)Incorrect InternalId value');
        System.assertEquals('https://www.fedex.com/fedextrack/?trknbr=ABC123', secondWrapper.TrackingLinkPortal2, 'B2)Incorrect TrackingLinkPortal2 value');
        System.assertEquals('1', secondWrapper.RowCount, 'B2)Incorrect RowCount value');
        System.assertEquals(true, secondWrapper.DisplayTracking, 'B2)Incorrect DisplayTracking value');

    }


    @IsTest
    static void testGetOrderDetail_ship() {
        // Step 1: Set up the necessary test data
        String headerIdval = 'ABC123';
        String groupItemval = 'ship';
        OrderStatusWrappers.Filters filters = new OrderStatusWrappers.Filters();
        filters.tracking = 'XYZ123';
        //filters.PQ = 'ABC123';
        filters.shipToName = 'TAcct';
        filters.searchKey = '123456';

        // Create sample records for Tracking_Information__c and Fulfillment_Sales_Order_Item__c

        //Account
        Account AcctIns = new Account();
            AcctIns.Name='TAcct';
        insert AcctIns;

        //Product   (ISBN / Name)
        Product2 ProdIns = new Product2();
            ProdIns.ProductCode = 'ABC123';
            ProdIns.Name = 'TProduct';
            ProdIns.ISBN__c = '123456';
        insert ProdIns;

        //Opportunity
        Opportunity OppIns = new Opportunity();
            OppIns.AccountId = AcctIns.Id;
            OppIns.Name = 'TOpp';
            OppIns.StageName = 'Discovery';
            OppIns.CloseDate = Date.newInstance(2023, 01, 01);
            //Quote_Number__c;
        insert OppIns;

        OppIns = [select Id, Quote_Number__c from Opportunity where id = : OppIns.id]; //Get PQ Number (AutoNumber) after Opp Insert
        filters.PQ = OppIns.Quote_Number__c;

        //Fulfillment Sales Order
        Fulfillment_Sales_Order__c FulSalesOrderIns = new Fulfillment_Sales_Order__c();
            FulSalesOrderIns.Customer_PO_Number__c = 'TPO';
            FulSalesOrderIns.Name = 'TFSO';
            FulSalesOrderIns.InternalId__c = 'ABC123';
            FulSalesOrderIns.Opportunity__c = OppIns.Id;
            FulSalesOrderIns.Ship_To_School__c = 'TAcct';
            FulSalesOrderIns.Ship_To_Contact__c = 'ABC123';
            FulSalesOrderIns.Shipping_Street__C = 'ABC123';
            FulSalesOrderIns.Shipping_City__c = 'ABC123';
            FulSalesOrderIns.Shipping_State__c = 'ABC123';
            FulSalesOrderIns.Shipping_Postal_Code__c = 'ABC123';
            FulSalesOrderIns.Shipping_Country__c = 'ABC123';
            FulSalesOrderIns.Status__c = 'Pending Fulfillment';
            //FulSalesOrderIns.XX = 'ABC123';
        insert FulSalesOrderIns;

        //Fulfillment Sales Order Item
        Fulfillment_Sales_Order_Item__c FulSalesOrderItemIns = new Fulfillment_Sales_Order_Item__c();
            FulSalesOrderItemIns.Quantity_Ordered__c = 1;
            FulSalesOrderItemIns.Product__c = ProdIns.Id;
            FulSalesOrderItemIns.Fulfillment_Sales_Order__c = FulSalesOrderIns.id;
            FulSalesOrderItemIns.Estimated_Delivery_Date_1__c = Date.newInstance(2023, 01, 01);
            FulSalesOrderItemIns.Estimated_Delivery_Date_2__c = Date.newInstance(2023, 01, 01);
            FulSalesOrderItemIns.Name = 'ABC123';
            //FulSalesOrderItemIns.XX = 'ABC123';
        insert FulSalesOrderItemIns;

        //Order Fulfillment
        Order_Fulfillment__c OrderFulIns = new Order_Fulfillment__c();
            OrderFulIns.Fulfillment_Sales_Order__c = FulSalesOrderIns.Id;
            OrderFulIns.Name = 'TFSO';
            OrderFulIns.InternalId__c = 'ABC123';
            OrderFulIns.Opportunity__c = OppIns.Id;
            OrderFulIns.Ship_To_Account__c = 'TAcct';
            OrderFulIns.Ship_To_Contact__c = 'ABC123';
            OrderFulIns.Shipping_Street__C = 'ABC123';
            OrderFulIns.Shipping_City__c = 'ABC123';
            OrderFulIns.Shipping_State__c = 'ABC123';
            OrderFulIns.Shipping_Postal_Code__c = 'ABC123';
            OrderFulIns.Shipping_Country__c = 'ABC123';
            OrderFulIns.Overall_Shipment_Status__c = 'Delivered';
            OrderFulIns.Status__c = 'Shipped';
            OrderFulIns.Shipment_Date__c = Date.newInstance(2023, 01, 01);
            //OrderFulIns.XX = 'ABC123';
        insert OrderFulIns;

        //Order Fulfillment Item
        Order_Fulfillment_Items__c OrderFulItemIns = new Order_Fulfillment_Items__c();
            OrderFulItemIns.Product__c = ProdIns.Id;
            OrderFulItemIns.Order_Fulfillment__c = OrderFulIns.Id;
            OrderFulItemIns.Ordered_Quantity__c = 1;
            //OrderFItemIns.XX = 'ABC123';
        insert OrderFulItemIns;

        //Tracking Information
        Tracking_Information__c TrackInfoIns = new Tracking_Information__c();
            TrackInfoIns.Tracking_Number__c = 'ABC123';
            TrackInfoIns.Carrier__c = 'ABC123';
            TrackInfoIns.Fulfillment__c = OrderFulIns.Id;
            TrackInfoIns.Order_FulFillment_Item__c = OrderFulItemIns.Id;
            TrackInfoIns.Quantity__c = 1;
            TrackInfoIns.Carrier_Code__c = 'FEDEX';
            //TrackInfoIns.XX = 'ABC123';
        insert TrackInfoIns;

        // Step 2: Call the getOrderDetail method
        List<OrderStatusWrappers.OrderDetailWrapper> result = OrderStatusController.getOrderDetail(headerIdval, groupItemval, filters, 1);

        // Step 3: Perform assertions to verify the expected results or behavior
        // Assert the size of the result
        System.assertEquals(1, result.size(), 'A3)Incorrect result size'); //getting 1

        //// Assert properties of the first OrderDetailWrapper object in the result
        OrderStatusWrappers.OrderDetailWrapper firstWrapper = result[0];
        System.assertEquals(TrackInfoIns.Id, firstWrapper.Id, 'A3)Incorrect Id value');
        //System.assertEquals('ExpectedQueryString1', firstWrapper.QueryString1, 'A3)Incorrect QueryString1 value');
        //System.assertEquals('ExpectedQueryString2', firstWrapper.QueryString2, 'A3)Incorrect QueryString2 value');
        System.assertEquals('123456', firstWrapper.Name, 'A3)Incorrect Name value');

        //System.assertEquals(null, firstWrapper.ISBN, 'A3)Incorrect ISBN value');
        //System.assertEquals(null, firstWrapper.Carrier, 'A3)Incorrect Carrier value');
        //System.assertEquals('ABC123', firstWrapper.TrackingNumber, 'A3)Incorrect TrackingNumber value');
        //System.assertEquals('ABC123', firstWrapper.TrackingLinkPortal, 'A3)Incorrect TrackingLinkPortal value');
        //System.assertEquals(Date.newInstance(2023, 01, 01), firstWrapper.DetailDate, 'A3)Incorrect DetailDate value');

        System.assertEquals(1, firstWrapper.Quantity, 'A3)Incorrect Quantity value');
        System.assertEquals(1, firstWrapper.ShippedQty, 'A3)Incorrect ShippedQty value');
        System.assertEquals('TProduct', firstWrapper.Product, 'A3)Incorrect Product value');
        System.assertEquals(true, firstWrapper.DisplayTracking, 'A3)Incorrect DisplayTracking value');

    }

    @IsTest
    static void testGetOrderDetail_order() {
        // Step 1: Set up the necessary test data
        String headerIdval = 'ESTIMATED DELIVERY: 1/1/2023 - 1/1/2023';
        String groupItemval = 'order';
        OrderStatusWrappers.Filters filters = new OrderStatusWrappers.Filters();
        filters.tracking = 'XYZ123';
        //filters.PQ = 'ABC123';
        filters.shipToName = 'TAcct';
        filters.searchKey = '123456';

        // Create sample records for Tracking_Information__c and Fulfillment_Sales_Order_Item__c

        //Account
        Account AcctIns = new Account();
            AcctIns.Name='TAcct';
        insert AcctIns;

        //Product   (ISBN / Name)
        Product2 ProdIns = new Product2();
            ProdIns.ProductCode = 'ABC123';
            ProdIns.Name = 'TProduct';
            ProdIns.ISBN__c = '123456';
        insert ProdIns;

        //Opportunity
        Opportunity OppIns = new Opportunity();
            OppIns.AccountId = AcctIns.Id;
            OppIns.Name = 'TOpp';
            OppIns.StageName = 'Discovery';
            OppIns.CloseDate = Date.newInstance(2023, 01, 01);
            //Quote_Number__c;
        insert OppIns;

        OppIns = [select Id, Quote_Number__c from Opportunity where id = : OppIns.id]; //Get PQ Number (AutoNumber) after Opp Insert
        filters.PQ = OppIns.Quote_Number__c;

        //Fulfillment Sales Order
        Fulfillment_Sales_Order__c FulSalesOrderIns = new Fulfillment_Sales_Order__c();
            FulSalesOrderIns.Customer_PO_Number__c = 'TPO';
            FulSalesOrderIns.Name = 'TFSO';
            FulSalesOrderIns.InternalId__c = 'ABC123';
            FulSalesOrderIns.Opportunity__c = OppIns.Id;
            FulSalesOrderIns.Ship_To_School__c = 'TAcct';
            FulSalesOrderIns.Ship_To_Contact__c = 'ABC123';
            FulSalesOrderIns.Shipping_Street__C = 'ABC123';
            FulSalesOrderIns.Shipping_City__c = 'ABC123';
            FulSalesOrderIns.Shipping_State__c = 'ABC123';
            FulSalesOrderIns.Shipping_Postal_Code__c = 'ABC123';
            FulSalesOrderIns.Shipping_Country__c = 'ABC123';
            FulSalesOrderIns.Status__c = 'Pending Fulfillment';
            //FulSalesOrderIns.XX = 'ABC123';
        insert FulSalesOrderIns;

        //Fulfillment Sales Order Item
        Fulfillment_Sales_Order_Item__c FulSalesOrderItemIns = new Fulfillment_Sales_Order_Item__c();
            FulSalesOrderItemIns.Quantity_Ordered__c = 1;
            FulSalesOrderItemIns.Product__c = ProdIns.Id;
            FulSalesOrderItemIns.Fulfillment_Sales_Order__c = FulSalesOrderIns.id;
            FulSalesOrderItemIns.Estimated_Delivery_Date_1__c = Date.newInstance(2023, 01, 01);
            FulSalesOrderItemIns.Estimated_Delivery_Date_2__c = Date.newInstance(2023, 01, 01);
            FulSalesOrderItemIns.Name = 'ABC123';
            //FulSalesOrderItemIns.XX = 'ABC123';
        insert FulSalesOrderItemIns;

        //Order Fulfillment
        Order_Fulfillment__c OrderFulIns = new Order_Fulfillment__c();
            OrderFulIns.Fulfillment_Sales_Order__c = FulSalesOrderIns.Id;
            OrderFulIns.Name = 'TFSO';
            OrderFulIns.InternalId__c = 'ABC123';
            OrderFulIns.Opportunity__c = OppIns.Id;
            OrderFulIns.Ship_To_Account__c = 'TAcct';
            OrderFulIns.Ship_To_Contact__c = 'ABC123';
            OrderFulIns.Shipping_Street__C = 'ABC123';
            OrderFulIns.Shipping_City__c = 'ABC123';
            OrderFulIns.Shipping_State__c = 'ABC123';
            OrderFulIns.Shipping_Postal_Code__c = 'ABC123';
            OrderFulIns.Shipping_Country__c = 'ABC123';
            OrderFulIns.Overall_Shipment_Status__c = 'Delivered';
            OrderFulIns.Status__c = 'Shipped';
            OrderFulIns.Shipment_Date__c = Date.newInstance(2023, 01, 01);
            //OrderFulIns.XX = 'ABC123';
        insert OrderFulIns;

        //Order Fulfillment Item
        Order_Fulfillment_Items__c OrderFulItemIns = new Order_Fulfillment_Items__c();
            OrderFulItemIns.Product__c = ProdIns.Id;
            OrderFulItemIns.Order_Fulfillment__c = OrderFulIns.Id;
            OrderFulItemIns.Ordered_Quantity__c = 1;
            //OrderFItemIns.XX = 'ABC123';
        insert OrderFulItemIns;

        //Tracking Information
        Tracking_Information__c TrackInfoIns = new Tracking_Information__c();
            TrackInfoIns.Tracking_Number__c = 'ABC123';
            TrackInfoIns.Carrier__c = 'ABC123';
            TrackInfoIns.Fulfillment__c = OrderFulIns.Id;
            TrackInfoIns.Order_FulFillment_Item__c = OrderFulItemIns.Id;
            TrackInfoIns.Quantity__c = 1;
            TrackInfoIns.Carrier_Code__c = 'FEDEX';
            //TrackInfoIns.XX = 'ABC123';
        insert TrackInfoIns;

        // Step 2: Call the getOrderDetail method
        List<OrderStatusWrappers.OrderDetailWrapper> result = OrderStatusController.getOrderDetail(headerIdval, groupItemval, filters, 1);

        // Step 3: Perform assertions to verify the expected results or behavior
        // Assert the size of the result
        System.assertEquals(1, result.size(), 'A4)Incorrect result size'); //getting 1

        //// Assert properties of the first OrderDetailWrapper object in the result
        OrderStatusWrappers.OrderDetailWrapper firstWrapper = result[0];
        System.assertEquals(FulSalesOrderItemIns.Id, firstWrapper.Id, 'A4)Incorrect Id value');
        //System.assertEquals('ExpectedQueryString1', firstWrapper.QueryString1, 'A4)Incorrect QueryString1 value');
        //System.assertEquals('ExpectedQueryString2', firstWrapper.QueryString2, 'A4)Incorrect QueryString2 value');
        System.assertEquals('123456', firstWrapper.Name, 'A4)Incorrect Name value');
        System.assertEquals(1, firstWrapper.Quantity, 'A4)Incorrect Quantity value');
        System.assertEquals(null, firstWrapper.ShippedQty, 'A4)Incorrect ShippedQty value');
        System.assertEquals('TProduct', firstWrapper.Product, 'A4)Incorrect Product value');
        System.assertEquals(false, firstWrapper.DisplayTracking, 'A4)Incorrect DisplayTracking value');

    }


}