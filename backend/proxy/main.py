# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import requests
from flask import Flask, Response
from google.auth.transport.requests import Request
from google.oauth2 import id_token

app = Flask(__name__)

def make_iap_request(url, client_id, method='GET'):
    '''Makes a request to an application protected by Identity-Aware Proxy.

    Args:
      url: The Identity-Aware Proxy-protected URL to fetch.
      client_id: The client ID used by Identity-Aware Proxy.
      method: The http request method to use.

    Returns:
      The page body, or raises an exception if the page couldn't be retrieved.
    '''

    open_id_connect_token = id_token.fetch_id_token(Request(), client_id)
    headers = {'Authorization': 'Bearer {}'.format(open_id_connect_token)}
    resp = requests.request(method, url, headers=headers, timeout=90)
    if resp.status_code == 403:
        raise Exception('Service account does not have permission to '
                        'access the IAP-protected application.')
    elif resp.status_code != 200:
        raise Exception(
            'Bad response from application: {!r} / {!r} / {!r}'.format(
                resp.status_code, resp.headers, resp.text))
    else:
        return resp.text

@app.route('/google_ads_conversions/<string:name>', methods=['GET'])
def get_ads_conversions(name):
    '''Endpoint to retrieve the Google Ads conversions for
    the specified Co-Op Configuration.

        Args:
        name (str): The Co-Op Configuration name.

        Returns:
        conversions (str): a list of Google Ads conversions in csv format.
    '''

    IAP_CLIENT_ID = os.environ.get('IAP_CLIENT_ID')
    PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT')
    URL = f'https://api-service-dot-{PROJECT_ID}.appspot.com' \
          f'/api/scheduler/get_google_ads_conversions/{name}'

    try:
        conversions = make_iap_request(URL, IAP_CLIENT_ID)
    except Exception as error:
        return f'Failed to get conversions: {error}', 500
    response = Response(response=conversions,
                        status=200, mimetype='text/csv')
    return response


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

