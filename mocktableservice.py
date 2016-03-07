
from azure.common import AzureException
from collections import defaultdict

class TableService(object):
    def __init__(self, account_name=None, account_key=None):
        self.tables = defaultdict(dict)

    def create_table(self, table):
        self.tables[table]

    def insert_or_replace_entity(self, table_name, entity):
        self.tables[table_name][(entity['PartitionKey'], entity['RowKey'])] = entity

    def delete_entity(self, table_name, partition_key, row_key):
        self.tables[table_name].pop((partition_key, row_key), None)

    def get_entity(self, table_name, partition_key, row_key):
        try:
            return self.tables[table_name][(partition_key, row_key)]
        except LookupError:
            raise AzureException
