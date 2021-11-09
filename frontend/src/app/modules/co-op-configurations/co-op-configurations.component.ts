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

import { Component, ViewChild, OnInit, ChangeDetectorRef } from '@angular/core';
import { MatPaginator, MatPaginatorIntl } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { MatSort } from '@angular/material/sort';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CoopConfiguration } from '../../models/co-op-configuration/co-op-configuration';
import { CoopConfigurationsService } from './services/co-op-configurations.service';
import { MatDialog } from "@angular/material/dialog";
import { ConfirmDialogComponent } from '../../modules/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-co-op-configurations',
  templateUrl: './co-op-configurations.component.html',
  styleUrls: ['./co-op-configurations.component.css']
})

export class CoopConfigurationsComponent implements OnInit {

  displayedColumns: Array<string>;
  coopConfigurations: Array<CoopConfiguration>;
  dataSource: MatTableDataSource<CoopConfiguration>
  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;
  showSpinner = false

  constructor(private coopConfigurationsService: CoopConfigurationsService,
    private _snackBar: MatSnackBar,
    private dialog: MatDialog) {
    this.paginator = new MatPaginator(new MatPaginatorIntl(), ChangeDetectorRef.prototype);
    this.sort = new MatSort();
    this.coopConfigurations = [];
    this.dataSource = new MatTableDataSource<CoopConfiguration>([]);
    this.displayedColumns = this.buildColumns();
  }

  ngOnInit(): void {
    this.getCoopConfigurations();
  }

  ngAfterViewInit() {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  getCoopConfigurations() {
    this.showSpinner = true;
    this.coopConfigurationsService.getCoopConfigurations().then(coopConfigurations => {
      this.coopConfigurations = coopConfigurations as Array<CoopConfiguration>;
      this.dataSource.data = this.coopConfigurations;
      this.showSpinner = false;
    }).catch(error => {
      console.error(error);
      this.openSnackBar(`ERROR: ${error}`);
      this.showSpinner = false;
    });
  }

  deleteCoopConfiguration(name: string) {
    this.dialog
      .open(ConfirmDialogComponent, {
        data: {
          title: 'Delete Co-op Campaign Configuration',
          message: `Are you sure you want to delete the Co-op Campaign Configuration <strong>${name}</strong>?`
        }
      }).afterClosed()
      .subscribe((confirm: boolean) => {
        if (confirm) {
          this.showSpinner = true;
          let index = this.coopConfigurations.findIndex(coopConfiguration => {
            return coopConfiguration.name === name
          });
          if (index !== -1) {
            let coopConfiguration: CoopConfiguration = this.coopConfigurations[index];
            this.coopConfigurationsService.deleteCoopConfiguration(coopConfiguration.name).then((response) => {
              this.openSnackBar(`The Co-op Configuration ${coopConfiguration.name} was deleted successfully.`);
              this.coopConfigurations.splice(index, 1);
              this.dataSource.data = this.coopConfigurations;
              this.showSpinner = false;
            })
              .catch(error => {
                console.error(error);
                this.openSnackBar(`ERROR: ${error}.`);
                this.showSpinner = false;
              });
          } else {
            console.log(`The Co-op Configuration was not found.`);
            this.openSnackBar(`The Co-op Configuration was not found.`);
            this.showSpinner = false;
          }

        }
    });
  }

  buildColumns() {
    return ['name', 'created_at', 'retailer_name', 'attribution_window', 'is_active', 'actions']
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