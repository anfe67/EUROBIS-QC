from unittest import TestCase

from eurobisqc import dataset
from dbworks import mssql_db_functions


class Test(TestCase):

    test_dataset = 1303
    test_dataset_eve_occur = 23
    test_dataset_emof = 164


    def test_query_builder_eve_occur(self):

        data_archive = dataset.Dataset()

        sql_string = data_archive.query_builder_eve_occur(self.test_dataset)

        # Try to execute it..
        if not mssql_db_functions.conn:
            conn = mssql_db_functions.open_db()
        else:
            conn = mssql_db_functions.conn

        cursor = conn.cursor()
        cursor.execute(sql_string)

        columns = [column[0] for column in cursor.description]
        records = []
        for row in cursor:
            records.append(dict(zip(columns, row)))

        assert (len(records) == self.test_dataset_eve_occur)

        # print(records[2])
        # print(records[len(records) - 1])


    def test_query_builder_emof(self):

        data_archive = dataset.Dataset()

        sql_string = data_archive.query_builder_emof(self.test_dataset)

        # Try to execute it..
        if not mssql_db_functions.conn:
            conn = mssql_db_functions.open_db()
        else:
            conn = mssql_db_functions.conn

        cursor = conn.cursor()
        cursor.execute(sql_string)

        columns = [column[0] for column in cursor.description]
        records = []
        for row in cursor:
            records.append(dict(zip(columns, row)))

        assert (len(records) == self.test_dataset_emof)

    def test_get_eml(self):

        data_archive = dataset.Dataset()
        data_archive.get_provider_data(self.test_dataset)
        data_archive.get_areas_from_eml(data_archive.imis_das_id)

        print(data_archive.areas)
