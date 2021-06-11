import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CoopConfigurationsComponent } from './co-op-configurations.component';
import { CoopConfigurationFormComponent } from './co-op-configuration-form/co-op-configuration-form.component';

const routes: Routes = [{
  path: 'co-op-configurations',
  component: CoopConfigurationsComponent,
  pathMatch: 'full'
},{
  path: 'co-op-configurations/new',
  component: CoopConfigurationFormComponent
},{
  path: 'co-op-configurations/:name/edit',
  component: CoopConfigurationFormComponent
}];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class CoopConfigurationsRoutingModule { }
