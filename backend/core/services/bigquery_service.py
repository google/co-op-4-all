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
from google.api_core.exceptions import NotFound
from google.cloud import bigquery
from jinja2 import Template


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

    def get_table(self, name):
        """Gets a table from BigQuery.

        Returns:
            bigquery.Table
        """

        try:
            table = self.client.get_table(name)
        except NotFound as e:
            # TODO: Add Logging
            return
        return table

    def execute_query(self, sql_file, query_params):
        """Executes a query as a job and waits for the results.

        Args:
            sql_file (str): The query to be executed.
            query_params(dict): Parameters to include in the query.

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

    def create(self, model):
        """Creates the datasets and tables in BigQuery for a Retailer or CoopCampaign.

        Args:
            model: A Pydantic model representing a CoopCampaingConfig
            or a RetailerConfig.
        """

        model_type = model.__class__.__name__
        model_params = model.dict()
        if model_type == 'RetailerConfig':
            query = self.get_query('sql/create_retailer_bqtables.sql', model_params)
        else:
            query = self.get_query('sql/create_or_update_coop.sql', model_params)
        job = self.client.query(query)

    def update(self, model):
        """Updates tables in BigQuery for a Retailer or CoopCampaign.

        Args:
            model: A Pydantic model representing a CoopCampaingConfig
            or a RetailerConfig.
        """

        model_type = model.__class__.__name__
        model_params = model.dict()
        if model_type == 'RetailerConfig':
            query = self.get_query('sql/update_retailer_bqtables', model_params)
        else:
            query = self.get_query('sql/create_or_update_coop.sql', model_params)
        job = self.client.query(query)

    def delete(self, model_params):
        """Deletes datasets and tables for a Retailer or CoopCampaign

        Args:
            model_params (dict): Parameters from a Pydantic Model of a CoopCampaignConfig
            or RetailerConfig.
        """

        name = model_params.get('name')
        retailer = model_params.get('retailer_name')
        if not retailer:
            self.client.delete_dataset(name, delete_contents=True)
        else:
            table_id = f'{retailer}.{name}'
            self.client.delete_table(table_id)
