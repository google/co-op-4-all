/***************************************************************************
*
*  Copyright 2021 Google Inc.
*
*  Licensed under the Apache License, Version 2.0 (the "License");
*  you may not use this file except in compliance with the License.
*  You may obtain a copy of the License at
*
*      https://www.apache.org/licenses/LICENSE-2.0
*
*  Unless required by applicable law or agreed to in writing, software
*  distributed under the License is distributed on an "AS IS" BASIS,
*  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*  See the License for the specific language governing permissions and
*  limitations under the License.
*
*  Note that these code samples being shared are not official Google
*  products and are not formally supported.
*
***************************************************************************/

import { Component, Input, OnInit } from '@angular/core';
import { Retailer } from 'src/app/models/retailer/retailer';
import { Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-retailer',
  templateUrl: './retailer.component.html',
  styleUrls: ['./retailer.component.css']
})
export class RetailerComponent implements OnInit {

  @Input() retailer: Retailer
  @Output() newItemEvent: EventEmitter<string>

  constructor() {
    this.retailer = {} as Retailer;
    this.newItemEvent = new EventEmitter<string>();
   }

  ngOnInit(): void {
  }

  deleteRetailer(name: string) {
    this.newItemEvent.emit(name);
  }

}
