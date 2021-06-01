import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { RetailersComponent } from './modules/retailers/retailers.component';
import { CoopConfigurationFormComponent } from './modules/co-op-configurations/co-op-configuration-form/co-op-configuration-form.component';


const routes: Routes = [{
  path: 'retailers',
  component: RetailersComponent,
  pathMatch: 'full'
},
{
  path: 'co-op-configurations',
  component: CoopConfigurationFormComponent
},{
  path: '',
  redirectTo: '/retailers',
  pathMatch: 'full'
}];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
