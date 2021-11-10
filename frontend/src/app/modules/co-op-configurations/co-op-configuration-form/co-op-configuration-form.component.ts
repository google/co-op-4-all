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
import { CoopConfiguration } from '../../../models/co-op-configuration/co-op-configuration';
import { CoopConfigurationsService } from '../services/co-op-configurations.service';
import { RetailersService } from '../../retailers/services/retailers.service';
import { Retailer } from '../../../models/retailer/retailer';
import { Filter } from '../../../models/co-op-configuration/filter';
import { GoogleAdsDestination } from '../../../models/co-op-configuration/google-ads-destination';
import { DV360Destination } from '../../../models/co-op-configuration/dv360-destination';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatOptionSelectionChange } from '@angular/material/core/option';
import { MatDialog } from "@angular/material/dialog";
import { ConfirmDialogComponent } from '../../../modules/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-co-op-configuration-form',
  templateUrl: './co-op-configuration-form.component.html',
  styleUrls: ['./co-op-configuration-form.component.css']
})
export class CoopConfigurationFormComponent implements OnInit {

  title: string
  coopConfigurationForm: FormGroup
  coopConfiguration: CoopConfiguration
  retailers: Array<Retailer>
  isNew: boolean
  filterTypeOptions: Array<any>
  destinationTypeOptions: Array<any>
  showSpinner: boolean = false
  coopCampaignName: string = '';

  constructor(private router: Router,
    private route: ActivatedRoute,
    private coopConfigurationsService: CoopConfigurationsService,
    private retailersService: RetailersService,
    private _snackBar: MatSnackBar,
    private dialog: MatDialog) {
    this.isNew = this.router.url.endsWith('new');
    this.title = this.isNew ? 'New Co-op Campaign Configuration' : 'Edit Co-op Campaign Configuration';
    this.retailers = [];
    this.coopConfiguration = {} as CoopConfiguration;
    this.coopConfigurationForm = this.buildCoopFormGroup();
    this.filterTypeOptions = this.buildFilterOptionsForSelect();
    this.destinationTypeOptions = this.buildDestinationOptionsForSelect();
  }

  ngOnInit(): void {
    this.showSpinner = true;
    this.getRetailers();
    this.route.params.subscribe(params => {
      let name = params.name;
      if (this.isNew) {
        // Builds an empty default config
        this.buildNewCoopConfiguration();
        this.setFormGroupValues(this.coopConfiguration);
        this.showSpinner = false;
      } else {
        this.coopCampaignName = name;
        // Retrieves an existing config
        this.getExistingCoopConfiguration(name);
      }
    });
  }

  buildNewCoopConfiguration() {
    let filter: Filter = {
      'type': 'item_brand',
      'data': []
    }
    let destination: GoogleAdsDestination = {
      'type': 'google_ads',
      'customer_id': ''
    }
    this.coopConfiguration = {
      'name': '',
      'retailer_name': '',
      'attribution_window': 30,
      'utm_campaigns': [],
      'filters': [filter],
      'destinations': [destination],
      'is_active': true,
    }
  }

  buildCoopFormGroup(): FormGroup {
    return new FormGroup({
      'name': new FormControl('', [Validators.required, Validators.pattern('^[A-Za-z0-9\_]{3,50}$')]),
      'retailer_name': new FormControl('', [Validators.required, Validators.pattern('^[A-Za-z0-9\_]{3,50}$')]),
      'attribution_window': new FormControl(30, [Validators.required, Validators.min(1), Validators.max(30)]),
      'filters': this.buildFiltersFormGroup(),
      'utm_campaigns': new FormControl('', [Validators.required]),
      'destinations': this.buildDestinationsFromGroup(),
      'is_active': new FormControl('on'),
    });
  }

  buildFiltersFormGroup(): FormGroup {
    return new FormGroup({
      'types': new FormControl([], [Validators.required]),
      'item_brand': new FormGroup({}),
      'item_name': new FormGroup({}),
      'item_id': new FormGroup({}),
    })
  }

  buildDestinationsFromGroup(): FormGroup {
    return new FormGroup({
      'types': new FormControl([], [Validators.required]),
      'google_ads': new FormGroup({}),
      'dv360': new FormGroup({})
    })
  }

  getFilterInformation(filterTye: any, option: string): string {
    let options: { [key: string]: any } = {};
    options['item_brand'] = {
      'type': 'item_brand',
      'optionLabel': 'Brand',
      'textAreaLabel': 'Brand Filter',
      'placeholder': `Brand1\nBrand 2`,
      'formControlName': 'item_brand_filter'
    };
    options['item_name'] = {
      'type': 'item_name',
      'optionLabel': "Product Name",
      'textAreaLabel': 'Product Name Filter',
      'placeholder': `Product Name 1\nProduct Name 2`,
      'formControlName': 'item_name_filter'
    };
    options['item_id'] = {
      'type': 'item_id',
      'optionLabel': "Product SKU",
      'textAreaLabel': 'Product SKU Filter',
      'placeholder': `ABCD1234567\nFGHI1234567`,
      'formControlName': 'item_id_filter'
    };
    return options[filterTye][option];
  }

  buildFilterOptionsForSelect() {
    return [{
      'value': 'item_brand',
      'label': 'Brand'
    }, {
      'value': 'item_name',
      'label': "Product Name"
    }, {
      'value': 'item_id',
      'label': "Product SKU"
    }];
  }

  buildDestinationOptionsForSelect() {
    return [{
      'value': 'google_ads',
      'label': "Google Ads"
    }, {
      'value': 'dv360',
      'label': 'DV360/CM'
    }];
  }

  getExistingCoopConfiguration(name: string) {
    this.coopConfigurationsService.getCoopConfiguration(name).then(coopConfiguration => {
      this.coopConfiguration = coopConfiguration as CoopConfiguration;
      this.setFormGroupValues(this.coopConfiguration);
      this.showSpinner = false;
    }).catch(error => {
      console.error(error);
      this.openSnackBar(`ERROR: ${error}`);
      this.showSpinner = false;
    });
  }

  setFormGroupValues(coopConfiguration: CoopConfiguration) {
    this.coopConfigurationForm.patchValue({ 'name': coopConfiguration.name });
    if (!this.isNew) {
      this.coopConfigurationForm.controls['name'].disable();
    }
    this.coopConfigurationForm.patchValue({ 'retailer_name': coopConfiguration.retailer_name });
    this.coopConfigurationForm.patchValue({ 'attribution_window': coopConfiguration.attribution_window });
    this.coopConfigurationForm.patchValue({ 'utm_campaigns': this.normalizeTextAreaDataForForm(coopConfiguration.utm_campaigns) });
    let filters = this.buildFormFilterValues(coopConfiguration.filters);
    this.coopConfigurationForm.patchValue({ 'filters': filters });
    let destinations = this.buildFormDestinationValues(coopConfiguration.destinations);
    this.coopConfigurationForm.patchValue({ 'destinations': destinations });
    this.coopConfigurationForm.patchValue({ 'is_active': coopConfiguration.is_active ? 'on' : '' });
  }

  buildFormFilterValues(filters: Array<Filter>) {
    let filterTypes: string[] = [];
    let formFilters: any = {};
    filters.forEach((filter) => {
      filterTypes.push(filter.type);
      this.addFilterControls(filter.type);
      formFilters[filter.type] = {
        [`${filter.type}_filter`]: this.normalizeTextAreaDataForForm(filter.data)
      };
    });
    formFilters['types'] = filterTypes;
    return formFilters
  }

  buildFormDestinationValues(destinations: Array<GoogleAdsDestination | DV360Destination>) {
    let destinationTypes: string[] = [];
    let formDestinations: any = {};
    destinations.forEach((destination) => {
      destinationTypes.push(destination.type);
      this.addDestinationControls(destination.type);
      switch (destination.type) {
        case 'google_ads':
          formDestinations[destination.type] = {
            'customer_id': (<GoogleAdsDestination>destination).customer_id
          };
          break;
        case 'dv360':
          formDestinations[destination.type] = {
            'cm_profile_id': (<DV360Destination>destination).cm_profile_id,
            'floodlight_activity_id': (<DV360Destination>destination).floodlight_activity_id,
            'floodlight_configuration_id': (<DV360Destination>destination).floodlight_configuration_id
          };
          break;
        default:
          break;
      }
    });
    formDestinations['types'] = destinationTypes;
    return formDestinations
  }

  normalizeTextAreaDataForForm(data: Array<string>): string {
    return data.join("\n")
  }

  normalizeTextAreaDataToSave(data: string) {
    return data.split("\n").map((d: string) => { return d.trim() })
  }

  save() {
    this.buildCoopConfiguration();
    if (this.isNew) {
      this.showSpinner = true;
      this.addCoopConfiguration();
    } else {
      this.dialog
      .open(ConfirmDialogComponent, {
        data: {
          title: 'Edit Co-op Campaign Configuration',
          message: `Are you sure you want to edit the Co-op Campaign Configuration <strong>${this.coopCampaignName}</strong>?</br></br>
          <strong>WARNING:</strong> The data in the BigQuery table that is linked to this configuration will be replaced and
          some information might be lost.`
        }
      }).afterClosed()
      .subscribe((confirm: boolean) => {
          if (confirm) {
            this.showSpinner = true;
            this.updateCoopConfiguration();
          }
      });
    }
    // TODO reset form after submit?
  }

  buildCoopConfiguration() {
    this.coopConfiguration.name = this.coopConfigurationForm.get('name')?.value;
    this.coopConfiguration.retailer_name = this.coopConfigurationForm.get('retailer_name')?.value;
    this.coopConfiguration.attribution_window = this.coopConfigurationForm.get('attribution_window')?.value;
    this.coopConfiguration.utm_campaigns = this.normalizeTextAreaDataToSave(this.coopConfigurationForm.get('utm_campaigns')?.value);
    this.coopConfiguration.filters = this.buildCoopConfigurationFilters();
    this.coopConfiguration.destinations = this.buildCoopConfigurationDestinations();
    this.coopConfiguration.is_active = this.coopConfigurationForm.get('is_active')?.value;
    if (this.coopConfiguration['modified_at'] || this.coopConfiguration['modified_at'] === '') {
      delete this.coopConfiguration['modified_at'];
    }
  }

  buildCoopConfigurationFilters(): Array<Filter> {
    let filters: Array<Filter> = [];
    let filterTypes = this.coopConfigurationForm.get('filters.types')?.value;
    filterTypes.forEach((filterType: string) => {
      let filter = {} as Filter;
      let data = this.coopConfigurationForm.get(`filters.${filterType}.${filterType}_filter`)?.value;
      filter.type = filterType
      filter.data = this.normalizeTextAreaDataToSave(data);
      filters.push(filter);
    });
    return filters
  }

  buildCoopConfigurationDestinations(): Array<GoogleAdsDestination | DV360Destination> {
    let destinations: Array<GoogleAdsDestination | DV360Destination> = [];
    let destinationTypes = this.coopConfigurationForm.get('destinations.types')?.value;
    destinationTypes.forEach((destinationType: string) => {
      let params = this.coopConfigurationForm.get(`destinations.${destinationType}`)?.value;
      switch (destinationType) {
        case 'google_ads':
          let googleAdsDestination = {} as GoogleAdsDestination;
          googleAdsDestination.type = destinationType;
          googleAdsDestination.customer_id = params.customer_id;
          destinations.push(googleAdsDestination);
          break;
        case 'dv360':
          let dv360Destination = {} as DV360Destination
          dv360Destination.type = destinationType;;
          dv360Destination.cm_profile_id = params.cm_profile_id;
          dv360Destination.floodlight_activity_id = params.floodlight_activity_id;
          dv360Destination.floodlight_configuration_id = params.floodlight_configuration_id
          destinations.push(dv360Destination);
          break;
        default:
          break;
      }
    });
    return destinations
  }

  addCoopConfiguration() {
    this.coopConfigurationsService.addCoopConfiguration(this.coopConfiguration).then((response) => {
      this.openSnackBar(this.buildMessage('created'));
      this.moveToCoopConfigurations();
      this.showSpinner = false;
    }).catch(error => {
      console.error(error);
      this.openSnackBar(`ERROR: ${error}`);
      this.showSpinner = false;
    });
  }

  updateCoopConfiguration() {
    this.coopConfigurationsService.updateCoopConfiguration(this.coopConfiguration).then((response) => {
      this.openSnackBar(this.buildMessage('updated'));
      this.moveToCoopConfigurations();
      this.showSpinner = false;
    }).catch(error => {
      console.error(error);
      this.openSnackBar(`ERROR: ${error}`);
      this.showSpinner = false;
    });
  }

  getRetailers() {
    this.retailersService.getRetailers().then(retailers => {
      this.retailers = retailers as Array<Retailer>;
      this.showSpinner = false;
    }).catch(error => {
      console.error(error);
      this.openSnackBar(`ERROR: ${error}`);
      this.showSpinner = false;
    });
  }

  showFilter(filterType: string): boolean {
    return this.coopConfigurationForm.get('filters.types')?.value.includes(filterType)
  }

  showDestination(destinationType: string): boolean {
    return this.coopConfigurationForm.get('destinations.types')?.value.includes(destinationType)
  }

  onChangeFilters(event: MatOptionSelectionChange) {
    if (event.isUserInput) {
      let filterType = event.source.value;
      let formGroupName = `filters.${filterType}`;
      if (!event.source.selected) {
        this.removeControls(formGroupName);
        this.removeFilterFromCoopConfiguration(filterType);
      } else {
        this.addFilterControls(filterType);
        this.addFilterToCoopConfiguration(filterType);
      }
    }
  }

  addFilterControls(filterType: string) {
    let formGroupName = `filters.${filterType}`;
    this.buildParentFormGroup(formGroupName);
    if (!this.coopConfigurationForm.get(formGroupName)?.get(`${filterType}_filter`)) {
      (<FormGroup>this.coopConfigurationForm.get(formGroupName)).addControl(`${filterType}_filter`,
        new FormControl('', [Validators.required]));
    }
  }

  addFilterToCoopConfiguration(filterType: string) {
    let found = this.coopConfiguration.filters.filter(f => { return f.type === filterType });
    // Add filter only if it does not exist
    if (found.length === 0) {
      let filter = {} as Filter;
      filter.type = filterType;
      filter.data = []
      this.coopConfiguration.filters.push(filter);
    }
  }

  removeFilterFromCoopConfiguration(filterType: string) {
    let index = this.coopConfiguration.filters.findIndex(
      filter => { return filter.type === filterType });
    if (index !== -1) {
      this.coopConfiguration.filters.splice(index, 1);
    }
  }

  onChangeDestinations(event: MatOptionSelectionChange) {
    if (event.isUserInput) {
      let destinationType = event.source.value;
      let formGroupName = `destinations.${destinationType}`;
      if (!event.source.selected) {
        this.removeControls(formGroupName);
        this.removeDestinationFromCoopConfiguration(destinationType);
      } else {
        this.addDestinationControls(destinationType);
        this.addDestinationToCoopConfiguration(destinationType);
      }
    }
  }

  removeDestinationFromCoopConfiguration(destinationType: string) {
    let index = this.coopConfiguration.destinations.findIndex(
      destination => { return destination.type === destinationType });
    if (index !== -1) {
      this.coopConfiguration.destinations.splice(index, 1);
    }
  }

  addDestinationToCoopConfiguration(destinationType: string) {
    let found = this.coopConfiguration.destinations.filter(d => { return d.type === destinationType });
    // Add destination only if it does not exist
    if (found.length === 0) {
      switch (destinationType) {
        case 'google_ads':
          let googleAdsDestination = {} as GoogleAdsDestination;
          googleAdsDestination.type = destinationType;
          googleAdsDestination.customer_id = '';
          this.coopConfiguration.destinations.push(googleAdsDestination);
          break;
        case 'dv360':
          let dv360Destination = {} as DV360Destination
          dv360Destination.type = destinationType;;
          dv360Destination.cm_profile_id = '';
          dv360Destination.floodlight_activity_id = '';
          dv360Destination.floodlight_configuration_id = ''
          this.coopConfiguration.destinations.push(dv360Destination);
          break;
        default:
          break;
      }
    }
  }

  addDestinationControls(destinationType: string) {
    let formGroupName = `destinations.${destinationType}`;
    this.buildParentFormGroup(formGroupName);
    switch (destinationType) {
      case 'google_ads':
        if (!this.coopConfigurationForm.get(formGroupName)?.get('customer_id')) {
          (<FormGroup>this.coopConfigurationForm.get(formGroupName)).addControl('customer_id',
            new FormControl('', [Validators.required, Validators.pattern('([0-9]{3})-([0-9]{3})-([0-9]{4})')]));
        }
        break;
      case 'dv360':
        if (!this.coopConfigurationForm.get(formGroupName)?.get('cm_profile_id')) {
          (<FormGroup>this.coopConfigurationForm.get(formGroupName)).addControl('cm_profile_id',
            new FormControl('', [Validators.required, Validators.pattern('^[0-9]{3,11}$')]));
        }
        if (!this.coopConfigurationForm.get(formGroupName)?.get('floodlight_activity_id')) {
          (<FormGroup>this.coopConfigurationForm.get(formGroupName)).addControl('floodlight_activity_id',
            new FormControl('', [Validators.required, Validators.pattern('^[0-9]{3,11}$')]));
        }
        if (!this.coopConfigurationForm.get(formGroupName)?.get('floodlight_configuration_id')) {
          (<FormGroup>this.coopConfigurationForm.get(formGroupName)).addControl('floodlight_configuration_id',
            new FormControl('', [Validators.required, Validators.pattern('^[0-9]{3,11}$')]));
        }
        break;
      default:
        break;
    }
  }

  buildParentFormGroup(parentGroupName: string) {
    if (!this.coopConfigurationForm.get(parentGroupName)) {
      // Add Form Group if not found in form
      let parentLevel = parentGroupName.split('.')[0];
      let childLevel = parentGroupName.split('.')[1];
      // Add common 'types' property
      if (!this.coopConfigurationForm.get(`${parentLevel}.types`)) {
        (<FormGroup>this.coopConfigurationForm.get(parentLevel)).addControl('types', new FormControl([], [Validators.required]));
      } else {
        // Add new child type
        let types = this.coopConfigurationForm.get(`${parentLevel}.types`)?.value;
        if (!types.includes(childLevel)) {
          types.push(childLevel);
          this.coopConfigurationForm.get(parentLevel)?.patchValue({ 'types': types });
        }
      }
      (<FormGroup>this.coopConfigurationForm.get(parentLevel)).addControl(childLevel, new FormGroup({}));
    }
  }

  removeControls(formGroupName: string) {
    let params = this.coopConfigurationForm.get(formGroupName)?.value;
    for (let param in params) {
      (<FormGroup>this.coopConfigurationForm.get(formGroupName)).removeControl(param);
    }
  }

  isInvalidInput(property: string) {
    return !this.coopConfigurationForm.get(property)?.valid
      && this.coopConfigurationForm.get(property)?.touched
  }

  buildMessage(action: string) {
    let message;
    message = `The Co-op Configuration ${this.coopConfiguration.name} was ${action} successfully!`;
    return message
  }

  openSnackBar(message: string) {
    let config = {
      duration: 2000
    }
    this._snackBar.open(message, "OK", config);
  }

  moveToCoopConfigurations() {
    setTimeout(() => {
      this.router.navigate(['co-op-configurations']);
    }, 2500)
  }

}
