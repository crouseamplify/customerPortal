public with sharing class OrderStatusWrappers {

        public class OrderShiptoWrapper implements Comparable {
            @AuraEnabled public string Id{get; set;}
            //@AuraEnabled public string QueryString1{get; set;}
            //@AuraEnabled public string QueryString2{get; set;}
            @AuraEnabled public string Name{get; set;}
            //@AuraEnabled public string ShipToAccount{get; set;}
            @AuraEnabled public string ShipToContact{get; set;}
            //@AuraEnabled public string ShipmentDate{get; set;}
            @AuraEnabled public string ShipToCity{get; set;}
            @AuraEnabled public string ShipToCountry{get; set;}
            @AuraEnabled public string ShipToZip{get; set;}
            @AuraEnabled public string ShipToState{get; set;}
            @AuraEnabled public string ShipToStreet{get; set;}
            @AuraEnabled public string DistrictName{get; set;}
            @AuraEnabled public string Parent{get; set;}
            @AuraEnabled public string UltimateParent{get; set;}
            @AuraEnabled public string CustomerPO{get; set;}
            @AuraEnabled public string RowCount{get; set;}

            public Integer compareTo(Object compareTo)
            {
                OrderShiptoWrapper OrderShiptoWrapper = (OrderShiptoWrapper) compareTo;
                if (Name == OrderShiptoWrapper.Name) return 0;
                if (Name > OrderShiptoWrapper.Name) return 1;
                return -1;
            }

        }

        public class OrderHeaderWrapper{
            @AuraEnabled public string Id{get; set;}
            //@AuraEnabled public string QueryString1{get; set;}
            //@AuraEnabled public string QueryString2{get; set;}
            @AuraEnabled public string Name{get; set;}
            @AuraEnabled public string DetailFilter{get; set;}
            @AuraEnabled public string GroupItem{get; set;}
            @AuraEnabled public string Status{get; set;}
            @AuraEnabled public string InternalId{get; set;}
            @AuraEnabled public string RowCount{get; set;}
            @AuraEnabled public string TrackingLinkPortal2{get; set;}
            @AuraEnabled public string Carrier{get; set;}
            @AuraEnabled public Boolean DisplayTracking{get; set;}
            @AuraEnabled public string ShipDate{get; set;}
        }

        public class OrderDetailWrapper{
            @AuraEnabled public string Id{get; set;}
            //@AuraEnabled public string QueryString1{get; set;}
            //@AuraEnabled public string QueryString2{get; set;}
            @AuraEnabled public string Name{get; set;}
            //@AuraEnabled public string ISBN{get; set;}
            @AuraEnabled public Decimal Quantity{get; set;}
            //@AuraEnabled public string Carrier{get; set;}
            //@AuraEnabled public string TrackingNumber{get; set;}
            //@AuraEnabled public string TrackingLinkPortal{get; set;}
            //@AuraEnabled public Date   DetailDate{get; set;}
            @AuraEnabled public Decimal ShippedQty{get; set;}
            @AuraEnabled public string Product{get; set;}
            @AuraEnabled public Boolean DisplayTracking{get; set;}
        }

        public class Filters {
            @AuraEnabled public String status { get; set; }
            //@AuraEnabled public String isbn { get; set; }
            @AuraEnabled public String searchKey { get; set; }
            @AuraEnabled public String PQ { get; set; }
            @AuraEnabled public String shipToName { get; set; }
            @AuraEnabled public String tracking { get; set; }
            @AuraEnabled public Decimal shipCount { get; set; }
        }

        public class Shipments {
            @AuraEnabled public Decimal total { get; set; }
            @AuraEnabled public Decimal processing { get; set; }
            @AuraEnabled public Decimal shipped { get; set; }
            @AuraEnabled public Decimal delivered { get; set; }
            @AuraEnabled public Boolean change { get; set; }
        }

}