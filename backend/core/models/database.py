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

from google.cloud import datastore
from pydantic import BaseModel

db_client = datastore.Client()


class DbModel(BaseModel):
    @classmethod
    def get_all(cls):
        query = db_client.query(kind=cls.__name__)
        results = list(query.fetch())
        return results

    @classmethod
    def get(cls, name):
        key = db_client.key(cls.__name__, name)
        result = db_client.get(key)
        return result

    @classmethod
    def delete(cls, name):
        key = db_client.key(cls.__name__, name)
        db_client.delete(key)

    @classmethod
    def delete_multi(cls, name, field):
        query = db_client.query(kind=cls.__name__)
        query.keys_only()
        query.add_filter(field, '=', name)
        keys = list([entity.key for entity in query.fetch()])
        db_client.delete_multi(keys)

    def add(self):
        with db_client.transaction() as t:
            key = db_client.key(self.__class__.__name__, self.name)
            entity = db_client.get(key)
            if not entity:
                entity = datastore.Entity(key)
                entity.update(self.dict(exclude_none=True))
                t.put(entity)
                return entity

    def update(self, name):
        self.name = name
        with db_client.transaction() as t:
            key = db_client.key(self.__class__.__name__, name)
            entity = db_client.get(key)
            if entity:
                entity = datastore.Entity(key)
                entity.update(self.dict(exclude_none=True))
                t.put(entity)
                return entity
