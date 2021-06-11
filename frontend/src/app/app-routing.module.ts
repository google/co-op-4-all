import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { RetailersComponent } from './modules/retailers/retailers.component';
import { CoopConfigurationsComponent } from './modules/co-op-configurations/co-op-configurations.component';

const routes: Routes = [{
  path: 'retailers',
  component: RetailersComponent,
  pathMatch: 'full'
},
{
  path: 'co-op-configurations',
  component: CoopConfigurationsComponent
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
