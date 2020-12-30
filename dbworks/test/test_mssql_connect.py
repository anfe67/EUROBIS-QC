import mssql_db_functions
from unittest import TestCase


class Test(TestCase):

    table = 'Inventory'

    def test_connect(self):
        """ Demonstrates connectivity with a MS SQL Server DB and
            queries all records in a table, outputting the results
            as a Python dictionary. """

        mssql_db_functions.open_db()
        cursor = mssql_db_functions.conn.cursor()
        cursor.execute(f'SELECT * FROM {self.table};')
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor:
            results.append(dict(zip(columns, row)))

        print(results)

