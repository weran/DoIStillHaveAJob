'''
Manages our table of employees.
'''

from azure.common import AzureException
from os import getenv

STORAGE_ACCOUNT_NAME = getenv("STORAGE_ACCOUNT_NAME")
STORAGE_ACCOUNT_KEY = getenv("STORAGE_ACCOUNT_KEY")
EMPLOYEE_TABLE_NAME = 'employees'

if STORAGE_ACCOUNT_NAME and STORAGE_ACCOUNT_KEY:
    from azure.storage.table import TableService
    table_service = TableService(STORAGE_ACCOUNT_NAME, STORAGE_ACCOUNT_KEY)
else:
    # If no connection string has been provided, create a mock service class
    # that simply keeps values in memory.

    from collections import defaultdict

    class TableService(object):
        def __init__(self):
            self.tables = defaultdict(dict)

        def insert_or_replace_entity(self, table, entity):
            self.tables[table][(entity['PartitionKey'], entity['RowKey'])] = entity

        def delete_entity(self, table, pkey, rkey):
            self.tables[table].pop((pkey, rkey), None)

        def get_entity(self, table, pkey, rkey):
            try:
                return self.tables[table][(pkey, rkey)]
            except LookupError:
                raise AzureException

    table_service = TableService()


class Employee(object):
    def __init__(self, name, has_a_job):
        self.name = name
        self.has_a_job = has_a_job

    def fix(self):
        if self.has_a_job:
            table_service.delete_entity(EMPLOYEE_TABLE_NAME, "_", self.name)
            self.has_a_job = False
        else:
            table_service.insert_or_replace_entity(EMPLOYEE_TABLE_NAME, {
                "PartitionKey": "_",
                "RowKey": self.name,
            })
            self.has_a_job = True

def get_employee(name):
    try:
        table_service.get_entity(EMPLOYEE_TABLE_NAME, "_", name)
    except AzureException:
        return Employee(name, False)
    return Employee(name, True)

