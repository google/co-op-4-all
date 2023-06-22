# Co-op4All - Branch: Ecommerce events

This branch add some recommended ecommerce events (purchase, begin_checkout, add_to_cart, view_item) to co-op backend solution.

To install the entire solution from zero go to master's README and follow the instructions. 

To add this branch to the solution follow this guide.

***Disclaimer: Co-op4All is not an officially supported Google product.***

## License

Copyright 2021 Google LLC

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

***Note that this solution is not an official Google product and
is not formally supported.***

- [1. Requirements](#1-requirements)
- [2. Installation](#2-installation)

## 1. Requirements

The transaction_id must be tagged in each event since It is still necessary for deduplication proposes. As It currently works with the purchase event, a transaction_id could involve various items for each conversion.

## 2. Installation

1. Open a Google Cloud shell console.
2. Check the Node version using ```node -v```. Make sure it is greater or equal than 16.10.0.
   - Use nvm to install the Node version, execute ```nvm install 16.10.0```. Details about nvm [here](https://github.com/nvm-sh/nvm)
3. Create a new folder to clone this branch ```mkdir co-op-4-all-branch-ecommerce-events``` and positioning ```cd co-op-4-all-branch-ecommerce-events``` 
4. Clone the Co-op4All repository branch ```git clone --branch ecommerce_events https://github.com/google/co-op-4-all.git ```
5. Go to the backend folder ```cd co-op-4-all/backend``` and execute the backend deploy: ```gcloud app deploy backend.yaml``` follow the instructions and when it's done, execute the dispatch deploy: ```gcloud app deploy dispatch.yaml```
