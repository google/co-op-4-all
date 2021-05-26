import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit {

  links = [{link:'Retailers', route:'retailers'},
  {link:'Co-op Configurations', route: 'co-op-configurations'}/*,
  {link: 'Retailers', route: 'retailers-list'},
  {link: 'Co-op Configurations', route: 'co-op-configurations-list'},
{link: 'Logs', route: 'logs-list' }*/];
  activeLink = this.links[0].link

  constructor() { }

  ngOnInit(): void {
  }

}
