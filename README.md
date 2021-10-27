# Co-Op4All

Co-Op4All is a platform to run co-marketing campaigns between brands and retailers, providing campaign performance dashboards and smart bidding optimization capabilities (offline conversions).

***Disclaimer: Co-Op4All is not an officially supported Google product.***

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

## Contents

  - [1. How does it work?](#1-how-does-it-work)
  - [2. Requirements](#2-requirements)
    - [2.1. APIs](#21-apis)
  - [3. Supported Offline Conversion Import Integrations](#3-supported-offline-conversion-import-integrations)
  - [4. Deployment](#4-deployment)
  - [5. Grant permissions to the App Engine default service account](#5-grant-permissions-to-the-app-engine-default-service-account)
  - [6. CM/DV360 Integration - Creating the required access tokens and secrets](#6-cmdv360-integration---creating-the-required-access-tokens-and-secrets)
  - [7. Closing the App using Identity Aware Proxy](#7-closing-the-app-using-identity-aware-proxy)

## 1. How does it work?

<img src="images/co-op-solution.png">

## 2. Requirements

* For Manufactures
    - Media team
    - Data Studio
    - Auto-tagging enabled
    - Google Ads access
    - Campaign Manager / DV360 access

* For Retailers
    - Tech team
    - Google Cloud Platform
        - Billing enabled
        - App Engine
        - BigQuery
        - Cloud Scheduler
        - Secret Manager
    - Google Analytics 4
        - Enhanced Ecommerce enabled
    - Google Ads access
    - Campaign Manager / DV360 access

### 2.1. APIs
- Google Ads
- Campaign Manager
- Datastore
- BigQuery
- Secret Manager

## 3. Supported Offline Conversion Import Integrations
- Google Ads Offline Conversions Import using **gclid** [[details]](https://support.google.com/google-ads/answer/2998031?hl=en)
- Campaign Manager / DV360 Offline Conversions Import using **dclid** [[details]](https://support.google.com/searchads/answer/7384231?hl=en)

## 4. Deployment

This guide assumes that the instructions will be followed inside Google Cloud Platform shell console.

1. Configure the **OAuth consent screen**. Go to the top left menu in Google Cloud, click on **APIs & Services** -> **OAuth consent screen**.
2.  In the **User type** option select **External** and click **Create**.
3. Assign a name to the application, it can be **Coop4All**, and complete all the other required fields.
4. Accept all the defaults and click on **Save and Continue** and then **Back to Dashboard**.
5. Then, In the **Publishing status** option select **PUBLISH APP**.
6. Open a Google Cloud shell console.
7. Clone this repository using ```git clone https://github.com/google/co-op-4-all```
8. Go to the deployment folder inside the root folder using ```cd co-op-4-all/deployment```
    * The deployment consists of 2 parts:
        - **App deployment**, where the terraform script will deploy all the required services in App Engine,
        the required cron jobs and will enable the required APIs.
            - *Default Service* - The web UI
            - *The API Service* - The service handling all the backend calls for CRUD and processing operations.
                - Cron job to execute the **update_all_configs** - a daily cron to update all the co-op campaign configurations.
                - Cron job to execute the **push_dv360_cm_conversions** - a daily cron to push the offline conversions to CM/DV360.
            - *The Proxy Service* - The service handling the Google Ads Offline Conversions Import. Since
            the **Scheduled Import** is configured directly in the Google Ads platform, this endpoint needs to be open using a proxy.
        - **Keys Deployment** (optional if integrating with CM/DV360), where the terraform script will deploy the required
        keys in Secret Manager for the Campaign Manager/DV360 integration and will enable the required APIs.
9. Go to the **app_deploy** folder using ```cd app_deploy``` and execute ```terraform init``` to initialize the terraform configuration.
10. Then, execute ```terraform apply``` and provide all the required parameters.
   -  Follow the steps to get The Identity Aware Proxy Client ID:
    1. Search for the Identity Aware Proxy page and click on the 3 dots menu to the right, next to the **App Engine app** collapsible menu.
    2. Click on the **Go to OAuth configuration** button.
    3. Copy and save the Client ID.
11. Type **yes** when required. *The installation might take up to 10 mins to finish.
12. After the deployment is ready, go to the **App Engine** page to verify the deployed UI in the **Dashboard** option
from the menu, then click on the URL at the top (project-id.uc.r.appspot.com). You should see the following message in the UI: Retailers not found.

## 5. Grant permissions to the App Engine default service account

It is highly recommended that the Co-op4All solution is installed in a new Google Cloud project, so it is required that the App Engine default service account (created during installation in step #4) has access to the BigQuery Export tables, those tables will most likely be on a different project.

1. Go to the project that contains the BigQuery Export, find the dataset with the data and click on the 3 dots menu.
2. Then, click on the **Share** button and then on the **Add principal** button.
3. Add the service account email and then select the **BigQuery Data Viewer** role and save.
 - The App Engine default service account email can be found in the **Service Accounts** page of the
project where the solution was deployed.

## 6. CM/DV360 Integration - Creating the required access tokens and secrets

If the CM/DV360 offline conversion import integration will be used, some tokens
are required to access the Google platforms. This flow will need OAuth tokens for an
account that can authenticate in those systems.

Follow the steps in order to create the tokens:
1. Access the Google Cloud console.
2. Go to the **API & Services** option on the top-left menu.
3. Set the **OAuth Consent Screen** (if not configured before). Configure the application as **External** and **Publish** the app.
4. Go to the **Credentials** page and create an OAuth Client Id with Application type set as **Desktop App**.
This will generate a Client Id and a Client Secret. Save the values since they are required in the next steps.
1. Then, run the ```generate_tokens.sh``` script using
```./generate_tokens.sh client_id client_secret``` and follow the instructions by opening the link and selecting/accepting all
the permissions. Then, copy the generated code and paste it in the console when required.
This will generate the **Access token** and the **Refresh token**, save the values since they will be used later.
- **Important:** The user who opens the generated link and accepts all the permissions, must have access to the platforms that Co-Op4All will integrate.
6. Then, go to the **keys_deploy** in the **deployment** folder.
7. Execute ```terraform init``` to initialize the terraform configuration.
8. Execute ```terraform apply``` and provide all the required parameters.
9. Type **yes** when required.
10. Once the deployment is finished, go to the **Secret Manager** page to verify that the secrets were created.

- **Important:** Do not change the secrets name, they are used as ids to retrieve the data using the Secret Manager API.

## 7. Closing the App using Identity Aware Proxy

The solution uses [Identity Aware Proxy](https://cloud.google.com/iap/docs/concepts-overview) in order to control access to the
web UI and the services. Users need to be added with a specific role to be able to access the resources.

Follow the steps below to close the application and create users.

1. Go to the **IAM** page in Google Cloud.
2. Click on the **Add** button at the top to add a new user.
3. Type the user's email and then select the **IAP-secured Web App User** role.
   - It is important to also add the email of the user deploying the solution, even if they are owner of the project.
4. Repeat the steps 2 and 3 for other users.
5. Go to the IAP page and now close the application by toggling the IAP option next to the App Engine App collapsible menu.
6. Now all the services will be closed using IAP, but the Google Ads proxy service needs to be open
in order to work for the Offline Conversions Import setup in the Google Ads platform.
To open the Google Ads proxy service, select the **checkbox** next to the **ads-conversion-proxy** service and add a new user using the menu on the right.
Click on the **Add principal** button, and type **allUsers**, then select the **IAP-secured Web App User** role.
   - The changes might take approximately 5 mins to take effect.