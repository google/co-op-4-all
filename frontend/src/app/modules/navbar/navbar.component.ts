import { Component } from '@angular/core';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent {

  links: Array<any>
  activeLink: string

  constructor() {
   this.links = [{
      link:'Retailers',
      route:'retailers',
      icon: 'store'
    },{
      link:'Co-Op Campaign Configurations',
      route: 'co-op-configurations',
      icon: 'settings'
    }];
    this.activeLink = this.links[0].link;
  }

}
