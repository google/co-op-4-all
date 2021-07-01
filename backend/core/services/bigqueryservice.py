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
        self.model_type = model_config.__class__.__name__
        # To support mixed model params
        self.model_params = model_config.dict() if self.model_type != 'dict' else model_config

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

    def get_ga_table(self):
        """Checks if GA4 table exists.

        Returns:
            bigquery.Table: GA4 Table.
        """

        table_name = self.model_params.get('bq_ga_table')
        try:
            table = client.get_table(table_name)
        except NotFound as e:
            # TODO: Add Logging
            return
        return table

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

    def execute_query(self, sql_file):
        """Executes a query as a job and waits for the results

        Args:
            sql_file (str): The query to be executed.

        Returns:
            result: the rows retrieved by the executed query.
        """
        query = self.get_query(sql_file)
        job = client.query(query)
        result = job.result()
        return result

    def get_table_data(self, sql_file):
        """Gets the table data of the specified query as a dataFrame

            Args:
            sql_file (str): The query to be executed.

            Returns:
                rows_df (dataFrame): A dataFrame with the query results
        """
        result = self.execute_query(sql_file)
        rows_df = result.to_dataframe()
        return rows_df

    def create(self):
        """Creates the datasets and tables in BigQuery for a Retailer or CoopCampaign.

        Returns:
            None
        """

        if self.model_type == 'RetailerConfig':
            query = self.get_query('sql/create_retailer_bqtables.sql')
        else:
            query = self.get_query('sql/create_or_update_coop.sql')
        job = client.query(query)

    def update(self):
        """Updates tables in BigQuery for a Retailer of CoopCampaign.

        Returns:
            None
        """

        if self.model_type == 'RetailerConfig':
            query = self.get_query('sql/update_retailer_bqtables')
        else:
            query = self.get_query('sql/create_or_update_coop.sql')
        job = client.query(query)

    def delete(self):
        """Delests datasets and tables for a Retailer or CoopCampaign

        Returns:
            None
        """

        if self.model_type == 'RetailerConfig':
            dataset_name = self.model_params.get('name')
            client.delete_dataset(dataset_name, delete_contents=True)
        else:
            table_name = self.model_params.get('name')
            dataset_name = self.model_params.get('retailer_name')
            table_id = f'{dataset_name}.{table_name}'
            client.delete_table(table_id)
