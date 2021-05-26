import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-retailer-form',
  templateUrl: './retailer-form.component.html',
  styleUrls: ['./retailer-form.component.css']
})
export class RetailerFormComponent implements OnInit {

  title = 'New Retailer'

  constructor(private router: Router, private route: ActivatedRoute) {
    this.title = this.router.url.endsWith('new') ? 'New Retailer' : 'Edit Retailer';
   }

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      console.log("params")
      console.log(params)
    });
  }

}
