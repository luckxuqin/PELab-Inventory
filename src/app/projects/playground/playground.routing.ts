import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { PlaygroundComponent } from './playground.component';

import { HomeComponent } from './home/home.component';
import { VcfComponent } from './vcf/vcf.component';
import { HostComponent } from './host/host.component';
import { ClusterComponent } from './cluster/cluster.component';
import { VlanComponent } from './vlan/vlan.component';
import { OtherhostsComponent } from './otherhosts/otherhosts.component';
import { UpdateComponent } from './update/update.component';
import { UpdatehostComponent } from './update/updatehost/updatehost.component';
import { UpdatevcfhostComponent } from './update/updatevcfhost/updatevcfhost.component';


const routes: Routes = [
  {
    path: '',
    component: PlaygroundComponent,
    children: [
      {
        path: '',
        pathMatch: 'full',
        redirectTo: 'home',
      },
      {
        path: 'home',
        component: HomeComponent,
      },
      {
        path: 'vlan',
        component: VlanComponent,
      },
      {
        path: 'update',
        component: UpdateComponent,
      },
      {
        path: 'updatehost',
        component: UpdatehostComponent,
      },
      {
        path: 'updatevcfhost',
        component: UpdatevcfhostComponent,
      },
      { path: 'home/:id', component: HomeComponent },
      { path: 'otherhosts', component: OtherhostsComponent },
      { path: 'vcf/:id', component: VcfComponent },
      // { path: 'vcf/:id', component: VcfComponent },
      // { path: 'cluster/:id', component: ClusterComponent },
      { path: 'cluster/:id', component: ClusterComponent },
      { path: 'host/:id', component: HostComponent },
      // { path: 'host/:id', component: HostComponent },
      // { path: 'vcf', component: VcfComponent },
      {
        path: 'rxjs',
        loadChildren: './rxjs/rxjs.module#RxJSModule',
      },
    ],
  },
];


export const declarations = [
  PlaygroundComponent,
  HomeComponent,
  VcfComponent,
  HostComponent,
  ClusterComponent,
  VlanComponent,
  OtherhostsComponent,
  UpdateComponent,
  UpdatehostComponent,
  UpdatevcfhostComponent,
];


@NgModule({
  imports: [ RouterModule.forChild(routes) ],
  exports: [ RouterModule ],
})
export class PlaygroundRoutingModule { }

