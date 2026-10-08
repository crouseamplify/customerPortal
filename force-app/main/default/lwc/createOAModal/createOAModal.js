import { LightningElement, api } from 'lwc';
import LightningModal from 'lightning/modal';
//import OA from '@salesforce/schema/Order_Allocation__c';
//import NAME_FIELD from '@salesforce/schema/Order_Allocation__c.Name';
//import ADDRESS_FIELD from '@salesforce/schema/Order_Allocation__c.Shipping_Address__c';
//import BSO_FIELD from '@salesforce/schema/Order_Allocation__c.Related_Blanket_Sales_Order__c';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
//import INDUSTRY_FIELD from '@salesforce/schema/Order_Allocation__c.Industry';

export default class createOAModal extends LightningModal {
    @api bsoId;
    @api oaRequestId;
    newOrderAllocation;
    //inputVariables = [];
    //connectedCallback() {
    //    console.log(this.bsoId);
        //BSO_FIELD = this.bsoId;
        //console.log("🚀 ~ file: createOAModal.js:15 ~ ConfigureModal ~ connectedCallback ~ BSO_FIELD:", BSO_FIELD)
      
        //console.log('allocationId ' + this.allocationId);
        /*this.inputVariables = [ 
            {
                name: 'AllocationId',
                type: 'String',
                value: this.allocationId
            }
        ];*/
    //}
    //objectApiName = OA;
    //fields = [NAME_FIELD, ADDRESS_FIELD, BSO_FIELD];
    /*handleSuccess(event) {
        const evt = new ShowToastEvent({
            title: "Account created",
            message: "Record ID: " + event.detail.id,
            variant: "success"
        });
        this.dispatchEvent(evt);
    }*/
    //@api allocationId;
    inputVariables = [];
    connectedCallback() {
        console.log('bsoId ' + this.bsoId);
        this.inputVariables = [ 
            {
                name: 'bsoId',
                type: 'String',
                value: this.bsoId
            },
            {
                name: 'oaRequestId',
                type: 'String',
                value: this.oaRequestId
            }
        ];
    }

    outputMessage = [];

    newOrderAllocationProducts = [];

    handleStatusChange(event) {
        console.log(event.detail.status);
        if (event.detail.status === "FINISHED") {
            const outputVariables = event.detail.outputVariables;
            console.log("outputVariables: ", outputVariables);
            for (let i = 0; i < outputVariables.length; i++) {
              const outputVar = outputVariables[i];
              console.log("outputVar: ", outputVar);
              if (outputVar.name == "v_OUTPUT_OrderAllocation") {
                this.newOrderAllocation = outputVar.value;
                console.log("this.newOrderAllocation: ", this.newOrderAllocation);
                //this.outputMessage.push(this.newOrderAllocation);
              }
              if (outputVar.name == "v_Coll_Order_Allocation_Products") {
                this.newOrderAllocationProducts = outputVar.value;
                console.log("this.newOrderAllocationProducts: ", this.newOrderAllocationProducts);
                //this.outputMessage = this.outputMessage.push(this.newOrderAllocationProducts);
              }
            }
            this.outputMessage = [this.newOrderAllocation, this.newOrderAllocationProducts]
            console.log('flow finished');
            console.log("this.outputMessage: ", this.outputMessage);
            //console.log("this.outputMessage[0]: ", this.outputMessage[0]);
            //console.log("this.outputMessage[1]: ", this.outputMessage[1]);
            if(this.outputMessage[0] === null && this.outputMessage[1] === null) {
                this.close(null);
            }
            else {
                this.close(this.outputMessage);
            }
          }
    }
}