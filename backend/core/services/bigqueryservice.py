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
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from google.api_core.exceptions import AlreadyExists, NotFound
from google.cloud import bigquery
from jinja2 import Template

client = bigquery.Client()

class BqService():
    """Interfaces with Bigquery to create datasets and tables

    Attributes:
        config_model: A pydantic model representing a RetailerConfig or a CoopConfig.
        model_type: A string representing the type of the model.
        model_params: A dict with paremeters to be included in the SQL query.
    """

    def __init__(self, model_config):
        self.model_config = model_config
        self.model_params = model_config.dict()
        self.model_type = model_config.__class__.__name__

    def get_query(self, sql_file):
        """Reads a sql file and adds query parameters.

        Args:
            sql_file (str): Path to the sql file.

        Returns:
            A string representing the sql query.
        """

        path = os.path.join(os.path.dirname(__file__), os.pardir, sql_file)
        with open(path, 'r') as f:
            file = f.read()
        query = Template(file)
        return query.render(params=self.model_params)

    def ga_table_ready(self):
        """Checks if the GA4 table from the day before is ready.

        Returns:
            bigquery.Table: The most recent GA4 table
        """

        table_reference = self.model_params.get('bq_ga_table')
        time_zone = self.model_params.get('time_zone')
        date = datetime.strftime(datetime.now(ZoneInfo(time_zone)) - timedelta(1), '%Y%m%d')
        try:
            table = client.get_table(table_reference)
        except NotFound as e:
            # TODO: Add logging
            return None
        return table

    def create(self):
        """Creates the datasets and tables in BigQuery for a retailer or CoopCampaign.

        Returns:
            None
        """
        if self.model_type == 'RetailerConfig':
            try:
                dataset_name = self.model_params.get('name')
                dataset_reference = client.dataset(dataset_name)
                dataset = client.create_dataset(dataset_reference)
            except AlreadyExists as e:
                # TODO: add logging
                return None
            query = self.get_query('sql/create_retailer.sql')
            job = client.query(query)
        else:
            query = self.get_query('sql/create_or_update_coop.sql')
            job = client.query(query)

    def update(self):
        pass

    def delete(self):
        pass
