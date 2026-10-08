import { LightningElement, api } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';

export default class OrderStatusResultsTileItem extends NavigationMixin(LightningElement) {
    @api listdetailitem;
}