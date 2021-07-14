/***************************************************************************
*
*  Copyright 2021 Google Inc.
*
*  Licensed under the Apache License, Version 2.0 (the "License");
*  you may not use this file except in compliance with the License.
*  You may obtain a copy of the License at
*
*      https://www.apache.org/licenses/LICENSE-2.0
*
*  Unless required by applicable law or agreed to in writing, software
*  distributed under the License is distributed on an "AS IS" BASIS,
*  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*  See the License for the specific language governing permissions and
*  limitations under the License.
*
*  Note that these code samples being shared are not official Google
*  products and are not formally supported.
*
***************************************************************************/

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { Retailer } from '../../../models/retailer/retailer';
import { RetailersService } from '../services/retailers.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { getTimezones } from  '../../../utils/timezones';
import { getCurrencyCodes } from  '../../../utils/currency-codes';

@Component({
  selector: 'app-retailer-form',
  templateUrl: './retailer-form.component.html',
  styleUrls: ['./retailer-form.component.css']
})
export class RetailerFormComponent implements OnInit {

  title: string
  retailerForm: FormGroup
  retailer: Retailer
  isNew: boolean
  showSpinner = false;
  timezones: Array<string>
  selectedTimezones : Array<string>
  currencyCodes: Array<string>
  selectedCurrencyCodes: Array<string>

  constructor(private router: Router,
    private route: ActivatedRoute,
    private retailersService: RetailersService,
    private _snackBar: MatSnackBar) {
    this.isNew = this.router.url.endsWith('new');
    this.title = this.isNew ? 'New Retailer' : 'Edit Retailer';
    this.retailerForm = this.buildRetailerFormGroup();
    this.retailer = {} as Retailer;
    this.timezones = getTimezones();
    this.selectedTimezones = this.timezones;
    this.currencyCodes = getCurrencyCodes();
    this.selectedCurrencyCodes = this.currencyCodes;
  }

  ngOnInit(): void {
    this.showSpinner = true;
    this.route.params.subscribe(params => {
      let name = params.name;
      if (this.isNew) {
        // Builds an empty default retailer
        this.buildNewRetailer();
        this.setFormGroupValues(this.retailer);
        this.showSpinner = false;
      } else {
        // Retrieves an existing retailer
        this.getExistingRetailer(name);
      }
    });
  }

  buildNewRetailer() {
    this.retailer = {
      'name': '',
      'bq_ga_table': '',
      'time_zone': '',
      'currency': '',
      'coop_max_backfill': 90,
      'is_active': true,
    }
  }

  buildRetailerFormGroup() {
    return new FormGroup({
      'name': new FormControl('', [Validators.required, Validators.pattern('^[A-Za-z0-9\_]{3,50}$')]),
      'bq_ga_table': new FormControl('', [Validators.required, Validators.pattern('^([A-Za-z0-9\-]{6,30})\.([A-Za-z0-9\_]{1,30})\.(events\_\\*)$')]),
      'time_zone': new FormControl('', [Validators.required, Validators.pattern('^[A-Za-z\_\/]{3,25}$')]),
      'currency': new FormControl('', [Validators.required, Validators.pattern('^[A-Za-z]{3}$')]),
      'coop_max_backfill': new FormControl('90', [Validators.required, Validators.min(30), Validators.max(180)]),
      'is_active': new FormControl('on'),
    });
  }

  getExistingRetailer(name: string) {
    this.retailersService.getRetailer(name).then(retailer => {
      this.retailer = retailer as Retailer;
      this.setFormGroupValues(this.retailer);
      this.showSpinner = false;
    })
    .catch(error => {
      console.error(error);
      this.openSnackBar(`ERROR: ${error}`);
      this.showSpinner = false;
    });
  }

  save() {
    this.showSpinner = true;
    this.buildRetailer();
    if(this.isNew) {
      this.addRetailer();
    } else {
      this.updateRetailer();
    }
    // TODO reset form after submit?
  }

  buildRetailer() {
    this.retailer.name = this.retailerForm.get('name')?.value;
    this.retailer.bq_ga_table = this.retailerForm.get('bq_ga_table')?.value;
    this.retailer.time_zone = this.retailerForm.get('time_zone')?.value;
    this.retailer.currency = this.retailerForm.get('currency')?.value;
    this.retailer.coop_max_backfill = this.retailerForm.get('coop_max_backfill')?.value;
    this.retailer.is_active = this.retailerForm.get('is_active')?.value;
    if(this.retailer['bq_updated_at'] || this.retailer['bq_updated_at'] === ''){
      delete this.retailer['bq_updated_at'];
    }
  }

  addRetailer() {
    this.retailersService.addRetailer(this.retailer).then((newRetailer) => {
      this.openSnackBar(this.buildMessage('created'));
      this.moveToRetailers();
      this.showSpinner = false;
    })
    .catch(error => {
        console.error(error);
        this.openSnackBar(`ERROR: ${error}`);
        this.showSpinner = false;
    });
  }

  updateRetailer() {
    this.retailersService.updateRetailer(this.retailer).then((updatedRetailer) => {
      this.openSnackBar(this.buildMessage('updated'));
      this.moveToRetailers();
      this.showSpinner = false;
    })
    .catch(error => {
      console.error(error);
      this.openSnackBar(`ERROR: ${error}`);
      this.showSpinner = false;
    });
  }

  setFormGroupValues(retailer: Retailer) {
    this.retailerForm.patchValue({ "name": retailer.name });
    if(!this.isNew) {
      this.retailerForm.controls['name'].disable();
    }
    this.retailerForm.patchValue({ "bq_ga_table": retailer.bq_ga_table });
    this.retailerForm.patchValue({ "time_zone": retailer.time_zone });
    this.retailerForm.patchValue({ "currency": retailer.currency });
    this.retailerForm.patchValue({ "coop_max_backfill": retailer.coop_max_backfill });
    this.retailerForm.patchValue({ "is_active": retailer.is_active });
  }

  isInvalidInput(property: string) {
    return !this.retailerForm.get(property)?.valid
      && this.retailerForm.get(property)?.touched
  }

  applyTimezoneFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.selectedTimezones = this.filter(this.timezones, filterValue);
  }

  applyCurrencyCodesFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.selectedCurrencyCodes = this.filter(this.currencyCodes, filterValue);
  }

  filter(list: Array<string>, value: string) {
    let filter = value.toLowerCase();
    return list.filter(option =>
      option.toLowerCase().startsWith(filter)
    );
  }

  buildMessage(action: string) {
    let message;
    message = `The retailer ${this.retailer.name} was ${action} successfully!`;
    return message
  }

  openSnackBar(message: string) {
    let config = {
      duration: 2000
    }
    this._snackBar.open(message, "OK", config);
  }

  moveToRetailers() {
    setTimeout(() => {
      this.router.navigate(['retailers']);
    }, 2500)
  }

}
