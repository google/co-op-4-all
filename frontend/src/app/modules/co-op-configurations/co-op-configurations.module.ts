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
import { SharedModule } from '../shared/shared.module';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { CoopConfigurationsComponent } from './co-op-configurations.component';
import { CoopConfigurationFormComponent } from './co-op-configuration-form/co-op-configuration-form.component';
import { CoopConfigurationsService } from './services/co-op-configurations.service';

@NgModule({
  declarations: [
    CoopConfigurationsComponent,
    CoopConfigurationFormComponent,
  ],
  imports: [
    SharedModule,
    RouterModule,
    CommonModule,
    ReactiveFormsModule
  ],
  exports: [
    CoopConfigurationsComponent,
    CoopConfigurationFormComponent
  ],
  providers: [
    CoopConfigurationsService
  ]
})
export class CoopConfigurationsModule { }