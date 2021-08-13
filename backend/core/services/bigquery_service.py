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

import utils
import os
from google.api_core.exceptions import NotFound
from google.cloud import bigquery
from jinja2 import Template

LOGGER_NAME = 'coop4all.bigquery_service'
logger = utils.get_coop_logger(LOGGER_NAME)

class BigqueryService():
    def __init__(self):
        self.client = bigquery.Client()

    def get_query(self, sql_file, query_params):
        """Reads a sql file and adds query parameters.

        Args:
            sql_file (str): Path to the sql file.
            query_params(dict): Parameters to include in the query.

        Returns:
            A string representing the sql query.
        """

        path = os.path.join(os.path.dirname(__file__), os.pardir, sql_file)
        with open(path, 'r') as f:
            file = f.read()
        query = Template(file)
        return query.render(params=query_params)

    def execute_query(self, sql_file, query_params):
        """Executes a query as a job and waits for the results.

        Args:
            sql_file (str): The query to be executed.
            query_params (dict): Parameters to include in the query.

        Returns:
            result: the rows retrieved by the executed query.
        """

        query = self.get_query(sql_file, query_params)
        job = self.client.query(query)
        result = job.result()
        return result

    def get_table_data(self, sql_file, query_params):
        """Gets the table data of the specified query as a dataFrame.

        Args:
            sql_file (str): The query to be executed.
            query_params (dict): The parameters to include in the query.

        Returns:
            rows_df (dataFrame): A dataFrame with the query results.
        """

        result = self.execute_query(sql_file, query_params)
        rows_df = result.to_dataframe()
        return rows_df

    def create(self, model_type, model_params):
        """Creates the datasets and tables in BigQuery
        for a Retailer or CoopCampaign.

        Args:
            model_type (str): The model type (CoopCampaingConfig or
            RetailerConfig).
            model_params (dict): Parameters to include in the query.
        """

        if model_type == 'RetailerConfig':
            query = self.get_query('sql/create_retailer_bqtables.sql', model_params)
        else:
            query = self.get_query('sql/create_or_update_coop.sql', model_params)
        job = self.client.query(query)

    def update(self, model_type, model_params):
        """Updates tables in BigQuery for a Retailer or CoopCampaign.

        Args:
            model_type (str): The model type (CoopCampaingConfig or
            RetailerConfig).
            model_params (dict): Parameters to include in the query.
        """

        if model_type == 'RetailerConfig':
            query = self.get_query('sql/update_retailer_bqtables.sql', model_params)
        else:
            query = self.get_query('sql/create_or_update_coop.sql', model_params)
        job = self.client.query(query)

    def delete(self, model_params):
        """Deletes datasets and tables for a Retailer or CoopCampaign

        Args:
            model_params (dict): Parameters from a Pydantic Model of
            a CoopCampaignConfig or RetailerConfig.
        """

        name = model_params.get('name')
        retailer = model_params.get('retailer_name')
        if not retailer:
            self.client.delete_dataset(name, delete_contents=True)
        else:
            table_id = f'{retailer}.{name}'
            self.client.delete_table(table_id)

    def get_table(self, table_name):
        """Gets a table by name.

        Args:
            table_name (str): Name of the table.

        Returns:
            bigquery.Table: Bigquery table object. Returns None
            if table was not found.
        """

        try:
            table = self.client.get_table(table_name)
        except NotFound as error:
            return None
        return table
