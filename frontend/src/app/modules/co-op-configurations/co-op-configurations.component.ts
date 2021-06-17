import { Component, ViewChild, OnInit, ChangeDetectorRef} from '@angular/core';
import { MatPaginator, MatPaginatorIntl } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { MatSort } from '@angular/material/sort';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CoopConfiguration } from '../../models/co-op-configuration/co-op-configuration';
import { CoopConfigurationsService } from './services/co-op-configurations.service';

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
    private _snackBar: MatSnackBar) {
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
        console.log(`There was an error while fetching the Co-Op configurations: ${error}`);
        this.openSnackBar(`There was an error while fetching the Co-Op configurations: ${error}`);
        this.showSpinner = false;
    });
  }

  deleteCoopConfiguration(name: string) {
    this.showSpinner = true;
    let index = this.coopConfigurations.findIndex(coopConfiguration => {
      return coopConfiguration.name === name
    });
    if (index !== -1) {
      let coopConfiguration : CoopConfiguration = this.coopConfigurations[index];
      this.coopConfigurationsService.deleteCoopConfiguration(coopConfiguration.name).then((response) => {
        this.openSnackBar(`The Co-Op Configuration ${coopConfiguration.name} was deleted successfully.`);
        this.coopConfigurations.splice(index, 1);
        this.dataSource.data = this.coopConfigurations;
        this.showSpinner = false;
      })
      .catch(error => {
        console.log(`There was an error while deleting the Co-Op Configuration ${coopConfiguration.name}: ${error}.`)
        this.openSnackBar(`There was an error while deleting the Co-Op Configuration ${coopConfiguration.name}: ${error}.`);
        this.showSpinner = false;
      });
    } else {
      console.log(`The Co-Op Configuration was not found.`);
      this.openSnackBar(`The Co-Op Configuration was not found.`);
      this.showSpinner = false;
    }
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