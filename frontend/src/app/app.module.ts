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

import { NgModule } from '@angular/core';
import { AppComponent } from './app.component';
import { ToolbarComponent } from './modules/toolbar/toolbar.component';
import { NavbarComponent } from './modules/navbar/navbar.component';
import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';
import { SharedModule } from './modules/shared/shared.module';
import { RetailersModule } from './modules/retailers/retailers.module';
import { RetailersRoutingModule } from './modules/retailers/retailers-routing.module';
import { CoopConfigurationsModule } from './modules/co-op-configurations/co-op-configurations.module';
import { CoopConfigurationsRoutingModule } from './modules/co-op-configurations/co-op-configurations.routing.module';
import { LogsModule } from './modules/logs/logs.module';
import { LogsRoutingModule } from './modules/logs/logs-routing.module';
import { ConfirmDialogComponent } from './modules/confirm-dialog/confirm-dialog.component';

@NgModule({
  declarations: [
    AppComponent,
    ToolbarComponent,
    NavbarComponent,
    ConfirmDialogComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    HttpClientModule,
    SharedModule,
    RetailersModule,
    RetailersRoutingModule,
    CoopConfigurationsModule,
    CoopConfigurationsRoutingModule,
    LogsModule,
    LogsRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
