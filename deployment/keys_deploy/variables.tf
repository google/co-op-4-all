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

variable "project_id" {
    type = string
    description = "The Google Cloud project ID"
}

variable "coop_client_id" {
    type = string
    description = "The client id downloaded from the Credentials page"
}

variable "coop_client_secret" {
    type = string
    description = "The client secret downloaded from the Credentials page"
}

variable "coop_access_token" {
    type = string
    description = "The access token generated with the generate_tokens.sh script"
}

variable "coop_refresh_token" {
    type = string
    description = "The refresh token generated with the generate_tokens.sh script"
}