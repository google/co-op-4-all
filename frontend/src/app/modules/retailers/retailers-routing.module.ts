import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { RetailersComponent } from './retailers.component';
import { RetailerFormComponent } from './retailer-form/retailer-form.component';

const routes: Routes = [{
  path: 'retailers',
  component: RetailersComponent,
  pathMatch: 'full'
},{
  path: 'retailers/new',
  component: RetailerFormComponent
},{
  path: 'retailers/:name/edit',
  component: RetailerFormComponent
}];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class RetailersRoutingModule { }
