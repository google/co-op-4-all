import { Component, OnInit } from '@angular/core';
import { Retailer } from '../../models/retailer'

@Component({
  selector: 'app-retailers',
  templateUrl: './retailers.component.html',
  styleUrls: ['./retailers.component.css']
})
export class RetailersComponent implements OnInit {

  retailers: Retailer[]

  constructor() {
    this.retailers = [];
   }

  ngOnInit(): void {
    this.getRetailers();
  }

  getRetailers() {
    // TODO: Replace this by call to the server
    let retailersJson = [{
      'name': 'Magalu',
      'createdAt': new Date().toISOString(),
      'bqGaTable': 'co-op-table',
      'bqDataSet': 'co-op-dataset',
      'timezone': 'America/Mexico_City',
      'maxBackfill': 3,
      'active': true
    },{
      'name': 'Walmart',
      'createdAt': new Date().toISOString(),
      'bqGaTable': 'co-op-table',
      'bqDataSet': 'co-op-dataset',
      'timezone': 'America/Mexico_City',
      'maxBackfill': 3,
      'active': true
    },{
      'name': 'Coppel',
      'createdAt': new Date().toISOString(),
      'bqGaTable': 'co-op-table',
      'bqDataSet': 'co-op-dataset',
      'timezone': 'America/Mexico_City',
      'maxBackfill': 3,
      'active': true
    }];
    retailersJson.forEach(retailerJ => {
      let retailer = new Retailer();
      retailer.name = retailerJ.name;
      retailer.createdAt = retailerJ.createdAt;
      retailer.bqGaTable = retailerJ.bqGaTable;
      retailer.bqDataSet = retailerJ.bqDataSet;
      retailer.timezone = retailerJ.timezone;
      retailer.maxBackfill = retailerJ.maxBackfill;
      retailer.active = retailerJ.active;
      this.retailers.push(retailer);
    });
  }

  removeRetailer(name: string) {
    let index = this.retailers.findIndex(retailer => {
      return retailer.name === name
    });
    if(index !== -1) {
      this.retailers.splice(index, 1);
    }
  }
}
