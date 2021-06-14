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

import { Component, ViewChild, OnInit, ChangeDetectorRef} from '@angular/core';
import { MatPaginator, MatPaginatorIntl } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { MatSort } from '@angular/material/sort';
import { Retailer } from '../../models/retailer/retailer';
import { RetailersService } from './services/retailers.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-retailers',
  templateUrl: './retailers.component.html',
  styleUrls: ['./retailers.component.css']
})
export class RetailersComponent implements OnInit {

  displayedColumns: Array<string>;
  retailers: Retailer[]
  dataSource: MatTableDataSource<Retailer>
  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;

  constructor(private retailersService: RetailersService,
    private _snackBar: MatSnackBar) {
    this.retailers = [];
    this.paginator = new MatPaginator(new MatPaginatorIntl(), ChangeDetectorRef.prototype);
    this.sort = new MatSort();
    this.dataSource = new MatTableDataSource<Retailer>([]);
    this.displayedColumns = this.buildColumns();
  }

  ngOnInit(): void {
    this.getRetailers();
  }

  ngAfterViewInit() {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  getRetailers() {
    this.retailersService.getRetailers().then(retailers => {
      retailers.forEach((retailer: Retailer) => {
        // Push each element, for some reason the table does not work if we assign it
        this.retailers.push(retailer);
        this.dataSource.data = this.retailers;
      });
    }).catch(error => {
      console.log(`There was an error while fetching the retailers: ${error}`);
      this.openSnackBar(`There was an error while fetching the retailers: ${error}`);
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
        this.dataSource.data = this.retailers;
      })
      .catch(error => {
        console.log(`There was an error while deleting the retailer ${retailer.name}: ${error}`);
        this.openSnackBar(`There was an error while deleting the retailer ${retailer.name}: ${error}`);
      });
    } else {
      console.log(`The retailer was not found.`);
      this.openSnackBar(`The retailer was not found.`);
    }
  }

  buildColumns() {
    return ['name', 'created_at', 'bq_ga_table', 'time_zone', 'max_backfill', 'is_active', 'actions']
  }

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }

  openSnackBar(message: string) {
    let config = {
      duration: 2000
    }
    this._snackBar.open(message, "OK", config);
  }
}