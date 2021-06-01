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
import { ApiService } from '../../../services/api.service';
import { Retailer } from '../../../models/retailer';

@Injectable()
export class RetailersService extends ApiService {

    private url = `${this.getHost()}/retailers`;

    getRetailers() {
        this.removeContentTypeHeader();
        return this.http.get(this.url, this.options)
            .toPromise()
            .catch(this.handleError);
    }

    getRetailer(name: string) {
        this.removeContentTypeHeader();
        return this.http.get(this.getRetailersUrl(name))
            .toPromise()
            .catch(this.handleError);
    }

    addRetailer(retailer: Retailer) {
        this.addContentTypeHeader();
        return this.http.post(this.url, JSON.stringify(retailer), this.options)
            .toPromise()
            .catch(this.handleError);
    }

    updateRetailer(retailer: Retailer) {
        this.addContentTypeHeader();
        return this.http.put(this.getRetailersUrl(retailer.name), JSON.stringify(retailer), this.options)
            .toPromise()
            .catch(this.handleError);
    }

    deleteRetailer(name: string) {
        this.removeContentTypeHeader();
        return this.http.delete(this.getRetailersUrl(name))
            .toPromise()
            .catch(this.handleError);
    }

    private getRetailersUrl(name: string) {
        return this.url + '/' + name;
    }

}