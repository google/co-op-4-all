import { NgModule } from '@angular/core';
import { SharedModule } from '../shared/shared.module';
import { RouterModule } from '@angular/router';
import { CoopConfigurationFormComponent } from './co-op-configuration-form/co-op-configuration-form.component';

@NgModule({
  declarations: [
    CoopConfigurationFormComponent,
  ],
  imports: [
    SharedModule,
    RouterModule,
  ],
  exports: [
    CoopConfigurationFormComponent
  ]
})
export class CoopConfigurationsModule { }