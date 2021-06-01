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
import { Retailer } from 'src/app/models/retailer';
import { RetailersService } from '../services/retailers.service';
import { MatSnackBar } from '@angular/material/snack-bar';
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

  constructor(private router: Router,
    private route: ActivatedRoute,
    private retailersService: RetailersService,
    private _snackBar: MatSnackBar) {
    this.isNew = this.router.url.endsWith('new');
    this.title = this.isNew ? 'New Retailer' : 'Edit Retailer';
    this.retailerForm = new FormGroup({
      'name': new FormControl('', [Validators.required, Validators.pattern('^[A-Za-z0-9\_]{3,50}$')]),
      'bq_ga_table': new FormControl('', [Validators.required, Validators.pattern('^[A-Za-z0-9\-\.]{10,50}events_$')]),
      'time_zone': new FormControl('', [Validators.required, Validators.pattern('^[A-Za-z\_\/]{3,25}$')]),
      'max_backfill': new FormControl('3', [Validators.required, Validators.min(1), Validators.max(3), Validators.pattern('[0-9]')]),
      'is_active': new FormControl('on'),
    });
    this.retailer = new Retailer();
  }

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      let name = params.name;
      if (!this.isNew && name) {
        // Edit mode
        this.retailersService.getRetailer(name).then(retailer => {
          this.retailer = retailer as Retailer;
          this.setFormGroup(this.retailer);
        })
        .catch(response => {
          if (response.status === 404) {
            console.log(`The retailer ${name} was not found.`);
            this.openSnackBar(`The retailer ${name} was not found.`);
          } else {
            console.log(`There was an error while loading the retailer ${name}.`);
            this.openSnackBar(`There was an error while loading the retailer ${name}.`);
          }
        });
      }
    });
  }

  save() {
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
    this.retailer.max_backfill = this.retailerForm.get('max_backfill')?.value;
    this.retailer.is_active = this.retailerForm.get('is_active')?.value;
    if(this.retailer['modified_at'] || this.retailer['modified_at'] === ''){
      delete this.retailer['modified_at'];
    }
  }

  addRetailer() {
    this.retailersService.addRetailer(this.retailer).then((newRetailer) => {
      this.openSnackBar(this.buildMessage('created'));
      this.moveToRetailers();
    })
    .catch(response => {
      if (response.status === 404) {
        console.log(`Retailer ${this.retailer.name} could not be created.`);
        this.openSnackBar(`Retailer ${this.retailer.name} could not be created.`);
      } else {
        console.log(`There was a problem creating the retailer ${this.retailer.name}.`);
        this.openSnackBar(`There was a problem creating the retailer ${this.retailer.name}.`);
      }
    });
  }

  updateRetailer() {
    this.retailersService.updateRetailer(this.retailer).then((updatedRetailer) => {
      this.openSnackBar(this.buildMessage('updated'));
      this.moveToRetailers();
    })
    .catch(response => {
      if (response.status === 404) {
        console.log(`Retailer ${this.retailer.name} could not be updated.`)
        this.openSnackBar(`Retailer ${this.retailer.name} could not be updated.`);
      } else {
        console.log(`There was a problem updating the retailer ${this.retailer.name}.`);
        this.openSnackBar(`There was a problem updating the retailer ${this.retailer.name}.`);
      }
    });
  }

  getNewRetailer() {
    return {
      'name': '',
      'bq_ga_table': '',
      'time_zone': '',
      'max_backfill': '3',
      'is_active': 'on',
    }
  }

  setFormGroup(retailer: Retailer) {
    this.retailerForm.patchValue({ "name": retailer.name });
    this.retailerForm.controls['name'].disable();
    this.retailerForm.patchValue({ "bq_ga_table": retailer.bq_ga_table });
    this.retailerForm.patchValue({ "time_zone": retailer.time_zone });
    this.retailerForm.patchValue({ "max_backfill": retailer.max_backfill });
    this.retailerForm.patchValue({ "is_active": retailer.is_active });
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
