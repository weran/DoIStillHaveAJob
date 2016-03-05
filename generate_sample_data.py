'''
Manages a list of tasks 
'''

from datetime import datetime, timedelta
from tasklist import STORAGE_ACCOUNT_NAME, STORAGE_ACCOUNT_KEY, TASK_TABLE_NAME

from azure.storage import TableService
table_service = TableService(STORAGE_ACCOUNT_NAME, STORAGE_ACCOUNT_KEY)

if __name__ == '__main__':
    table_service.create_table(TASK_TABLE_NAME)

    for i, name in enumerate([
        'Leave work',
        'Go home',
        'Make dinner',
        'Do dishes',
    ]):
        table_service.insert_or_replace_entity(
            TASK_TABLE_NAME,
            '_',
            str(i),
            { 'name': name, 'due': datetime.today() }
        )

    for i, name in enumerate([
        'Wake up',
        'Make lunch',
        'Go to work',
    ]):
        table_service.insert_or_replace_entity(
            TASK_TABLE_NAME,
            '_2',
            str(i),
            { 'name': name, 'due': datetime.today() + timedelta(days=1) }
        )
