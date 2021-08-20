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
import { Log } from '../../models/log/log';
import { LogsService } from './services/logs.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-logs',
  templateUrl: './logs.component.html',
  styleUrls: ['./logs.component.css']
})
export class LogsComponent implements OnInit {

  displayedColumns: Array<string>;
  logs: Array<Log>;
  dataSource: MatTableDataSource<Log>;
  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;
  showSpinner = false;

  constructor(private logsService: LogsService,
    private _snackBar: MatSnackBar) {
    this.logs = [];
    this.paginator = new MatPaginator(new MatPaginatorIntl(), ChangeDetectorRef.prototype);
    this.sort = new MatSort();
    this.dataSource = new MatTableDataSource<Log>([]);
    this.displayedColumns = this.buildColumns();
  }

  ngOnInit(): void {
    this.getLogs();
  }

  ngAfterViewInit() {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  getLogs() {
    this.showSpinner = true;
    this.logsService.getLogs().then(logs => {
      this.logs = logs as Array<Log>;
      this.dataSource.data = this.logs;
      this.showSpinner = false;
    }).catch(error => {
      console.error(error);
      this.openSnackBar(`ERROR: ${error}`);
      this.showSpinner = false;
    });
  }

  buildColumns() {
    return ['date', 'message']
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
