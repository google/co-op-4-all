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

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable()
export class ApiService {

  protected host = this.getHost();
  protected options: any = {
    headers: {}
  };

  constructor(protected http: HttpClient) { }

  // For local development
  protected getHost() {
    const h = window.location.hostname;
    return h === 'localhost' ? `http://${h}:5000/api` : `https://${h}/api`;
  }

  protected handleError(error: any): Promise<any> {
    console.error('An error occurred', error);
    return Promise.reject((error.error && error.error.message) || error.message || error);
  }

  protected addContentTypeHeader() {
    this.options.headers['Content-Type'] = 'application/json';
  }

  protected removeContentTypeHeader() {
    delete this.options.headers['Content-Type'];
  }
}