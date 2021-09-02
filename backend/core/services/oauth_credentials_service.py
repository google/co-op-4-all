# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import utils
from google.cloud import secretmanager
from core.models.oauth_credentials import OAuthCredentials
from core.exceptions.coop_exception import CoopException

# Environment variables
PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT', '')
COOP_CLIENT_ID_SNAME = os.environ.get('COOP_CLIENT_ID_SNAME', '')
COOP_CLIENT_SECRET_SNAME = os.environ.get('COOP_CLIENT_SECRET_SNAME', '')
COOP_ACCESS_TOKEN_SNAME = os.environ.get('COOP_ACCESS_TOKEN_SNAME', '')
COOP_REFRESH_TOKEN_SNAME = os.environ.get('COOP_REFRESH_TOKEN_SNAME', '')
LOGGER_NAME = 'coop4all.oauth_credentials_service'
logger = utils.get_coop_logger(LOGGER_NAME)

class OAuthCredentialService():
    '''
    Service that builds the required credentials to authenticate to Google APIs.

        Attributes:
            secret_manager_client: the Secret Manager client to access the API
            oauth_credentials: the credentials used in other services to authenticate
            to Google APIs
    '''

    def __init__(self):
        self.secret_manager_client = secretmanager.SecretManagerServiceClient()
        self.oauth_credentials = self.__buildCredentials()

    def __buildCredentials(self):
        parent = f'projects/{PROJECT_ID}'
        client_id = ''
        client_secret = ''
        access_token = ''
        refresh_token = ''
        for secret in self.secret_manager_client.list_secrets(request={'parent': parent}):
            # Build the resource name of the secret version.
            name = secret.name.split('/')[-1]
            # Use always the latest version of the secret
            full_name = f'{parent}/secrets/{name}/versions/latest'
            # Access the secret version.
            response = self.secret_manager_client.access_secret_version(request={'name': full_name})
            payload = response.payload.data.decode("UTF-8")
            if name == COOP_CLIENT_ID_SNAME:
                client_id = payload
            if name == COOP_CLIENT_SECRET_SNAME:
                client_secret = payload
            if name == COOP_ACCESS_TOKEN_SNAME:
                access_token = payload
            if name == COOP_REFRESH_TOKEN_SNAME:
                refresh_token = payload
        if not self.__keys_valid(client_id, client_secret, access_token, refresh_token):
            raise CoopException(f'OAuthCredentialService - The authentication keys are invalid. ' \
            f'Please check they exist in the Secret Manager UI.', status_code=500)
        return OAuthCredentials(client_id, client_secret, access_token, refresh_token)

    def get_oauth_credentials(self):
        return self.oauth_credentials

    def __keys_valid(self, client_id, client_secret, access_token, refresh_token):
        return client_id and client_secret and access_token and refresh_token
