import { NgModule } from '@angular/core';
import { SharedModule } from '../shared/shared.module';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { RetailersComponent } from './retailers.component';
import { RetailerComponent } from './retailer/retailer.component';
import { RetailerFormComponent } from './retailer-form/retailer-form.component';

@NgModule({
  declarations: [
    RetailersComponent,
    RetailerComponent,
    RetailerFormComponent
  ],
  imports: [
    SharedModule,
    RouterModule,
    CommonModule
  ],
  exports: [
    RetailersComponent,
    RetailerComponent,
    RetailerFormComponent
  ]
})
export class RetailersModule { }