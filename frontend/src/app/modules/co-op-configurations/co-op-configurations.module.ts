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