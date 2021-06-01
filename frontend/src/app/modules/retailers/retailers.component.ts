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
import { Retailer } from '../../models/retailer';
import { RetailersService } from './services/retailers.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-retailers',
  templateUrl: './retailers.component.html',
  styleUrls: ['./retailers.component.css']
})
export class RetailersComponent implements OnInit {

  retailers: Retailer[]

  constructor(private retailersService: RetailersService,
    private _snackBar: MatSnackBar) {
    this.retailers = [];
  }

  ngOnInit(): void {
    this.getRetailers();
  }

  getRetailers() {
    this.retailersService.getRetailers()
    .then(retailers => {
      this.retailers = retailers as Retailer[];
    }).catch(response => {
      if (response.status === 404) {
        console.log(`The retailers were not found.`);
        this.openSnackBar(`The retailers were not found`);
      } else {
        console.log(`There was an error while loading the retailers.`);
        this.openSnackBar(`There was an error while loading the retailers.`);
      }
    });
  }

  deleteRetailer(name: string) {
    let index = this.retailers.findIndex(retailer => {
      return retailer.name === name
    });
    if (index !== -1) {
      let retailer = this.retailers[index];
      this.retailersService.deleteRetailer(retailer.name).then((response) => {
        this.openSnackBar(`The retailer ${retailer.name} was deleted successfully.`);
        this.retailers.splice(index, 1);
      })
      .catch(response => {
        if (response.status === 404) {
          console.log(`Retailer ${retailer.name} could not be deleted.`)
          this.openSnackBar(`Retailer ${retailer.name} could not be deleted.`);
        } else {
          console.log(`There was a problem deleting the retailer ${retailer.name}.`);
          this.openSnackBar(`There was a problem deleting the retailer ${retailer.name}.`);
        }
      });
    } else {
      console.log(`The retailer was not found.`);
      this.openSnackBar(`The retailer was not found.`);
    }
  }

  openSnackBar(message: string) {
    let config = {
      duration: 2000
    }
    this._snackBar.open(message, "OK", config);
  }
}
