import { NgModule } from '@angular/core';
import { AppComponent } from './app.component';
import { ToolbarComponent } from './modules/toolbar/toolbar.component';
import { NavbarComponent } from './modules/navbar/navbar.component';
import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { SharedModule } from './modules/shared/shared.module';

import { RetailersModule } from './modules/retailers/retailers.module';
import { RetailersRoutingModule } from './modules/retailers/retailers-routing.module';
/*import { RetailersComponent } from './modules/retailers/retailers.component';
import { RetailerComponent } from './modules/retailers/retailer/retailer.component';
import { RetailerFormComponent } from './modules/retailers/retailer-form/retailer-form.component';*/

import { CoopConfigurationsModule } from './modules/co-op-configurations/co-op-configurations.module';

@NgModule({
  declarations: [
    AppComponent,
    ToolbarComponent,
    NavbarComponent,
    /*RetailersComponent,
    RetailerComponent,
    RetailerFormComponent*/
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    SharedModule,
    RetailersModule,
    RetailersRoutingModule,
    CoopConfigurationsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
