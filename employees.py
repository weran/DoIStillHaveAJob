'''
Manages our table of employees.
'''

from azure.common import AzureException
from os import getenv

STORAGE_ACCOUNT_NAME = getenv("STORAGE_ACCOUNT_NAME")
STORAGE_ACCOUNT_KEY = getenv("STORAGE_ACCOUNT_KEY")
EMPLOYEE_TABLE_NAME = 'employees'

if STORAGE_ACCOUNT_NAME and STORAGE_ACCOUNT_KEY:
    # We have connection details, so use the real
    # table service class.
    from azure.storage.table import TableService

else:
    # No connection has been provided, so create a
    # mock service class that keeps values in memory.
    from mocktableservice import TableService

table_service = TableService(STORAGE_ACCOUNT_NAME, STORAGE_ACCOUNT_KEY)

# Ensure the table exists.
table_service.create_table(EMPLOYEE_TABLE_NAME)

class Employee(object):
    def __init__(self, name, has_a_job):
        self.name = name
        self.has_a_job = has_a_job

    def fix(self):
        self.has_a_job = not self.has_a_job
        table_service.insert_or_replace_entity(EMPLOYEE_TABLE_NAME, {
            "PartitionKey": "_",
            "RowKey": self.name,
            "has_a_job": self.has_a_job,
        })

    @classmethod
    def get(cls, name):
        try:
            e = table_service.get_entity(
                table_name=EMPLOYEE_TABLE_NAME,
                partition_key="_",
                row_key=name,
            )
        except AzureException:
            return cls(name, False)
        return cls(name, e.get("has_a_job", False))

