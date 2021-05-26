import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { RetailerFormComponent } from './retailer-form/retailer-form.component';

const routes: Routes = [{
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
