import { LightningElement, api } from 'lwc';
import LightningModal from 'lightning/modal';

export default class ConfigureModal extends LightningModal {
    @api allocationId;
    inputVariables = [];
    displayName;
    connectedCallback() {
        console.log('allocationId ' + this.allocationId);
        this.inputVariables = [ 
            {
                name: 'Input_Order_Allocation_Id',
                type: 'String',
                value: this.allocationId
            }
        ];
    }

    handleStatusChange(event) {
        console.log(event.detail.status);
        if (event.detail.status === "FINISHED") {
            const outputVariables = event.detail.outputVariables;
            for (let i = 0; i < outputVariables.length; i++) {
              const outputVar = outputVariables[i];
              console.log("outputVar: ", outputVar);
              if (outputVar.name == "OA_Confirmed") {
                this.newOAStatus = outputVar.value;
                //console.log("this.newOAStatus: ", this.newOAStatus);
                //this.outputMessage.push(this.newOrderAllocation);
              }
              if (outputVar.name == "Output_OA_Display_Name") {
                this.displayName = outputVar.value;
                //console.log("this.displayName: ", this.displayName);
                //this.outputMessage.push(this.newOrderAllocation);
              }
              if (outputVar.name == "TEMP_Order_Allocation") {
                this.newOAFields = outputVar.value;
                //console.log("this.displayName: ", this.displayName);
                //this.outputMessage.push(this.newOrderAllocation);
              }
            }
            //this.outputMessage = this.newOAStatus;
            //console.log('flow finished');
            //console.log("this.outputMessage: ", this.outputMessage);
            //this.close(this.outputMessage);

            this.outputMessage = [this.newOAStatus, this.displayName, this.newOAFields];
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