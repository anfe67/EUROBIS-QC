from unittest import TestCase

from eurobisqc import eurobis_dataset
from dbworks import mssql_db_functions


class Test(TestCase):
    # picked dataset meso_meiofauna_knokke_1969
    test_dataset = 1303
    test_imis_no = 4595
    test_dataset_events = 23
    test_dataset_occurences = 341
    test_dataset_emof = 164

    def test_query_builder_eve_occur(self):
        """ Retrieving events and occurrence records in a dataset from MS SQL
            using the assembled query string """

        data_archive = eurobis_dataset.EurobisDataset()

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

        assert (len(records) == self.test_dataset_events + self.test_dataset_occurences)

    def test_query_builder_emof(self):
        """ Retrieving eMof records in a dataset from MS SQL
            using the assembled query string """

        data_archive = eurobis_dataset.EurobisDataset()

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
        """ retrieving EML from the IMIS service to extract
            areas after having queried the DB for dataset info """

        data_archive = eurobis_dataset.EurobisDataset()
        data_archive.get_provider_data(self.test_dataset)
        data_archive.get_areas_from_eml(data_archive.imis_das_id)

        print(data_archive.areas)

    def test_get_eml_negative(self):
        """ Verify that the solution can handle cases when EML data
            is not available (it does not fail for that reason) """

        fake_imis_das_id = 10000
        data_archive = eurobis_dataset.EurobisDataset()
        data_archive.get_areas_from_eml(fake_imis_das_id)

        # Negative
        print(
            f"Found {'No interesting' if data_archive.areas is None else len(data_archive.areas)} "
            f"areas in IMIS Dataset N,{fake_imis_das_id}")
        # Positive
        data_archive.get_areas_from_eml(self.test_imis_no)
        print(
            f"Found {'No interesting' if data_archive.areas is None else len(data_archive.areas)} "
            f"areas in IMIS Dataset N,{self.test_imis_no}")
        # NOTE: API not OK at the moment, it returns the globe as an area, which is wrong.

    def test_load_dataset(self):

        data_archive = eurobis_dataset.EurobisDataset()
        data_archive.load_dataset(self.test_dataset)

        assert (len(data_archive.event_recs) == self.test_dataset_events)
        assert (len(data_archive.occurrence_recs) == self.test_dataset_occurences)
        assert (len(data_archive.emof_recs) == self.test_dataset_emof)
        assert (data_archive.imis_das_id == self.test_imis_no)

        sum_len = 0
        for key in data_archive.emof_indices:
            sum_len += len(data_archive.emof_indices[key])

        assert (sum_len == len(data_archive.emof_recs))

        # Second dataset where core = 1
        test_dataset2 = 558
        data_archive2 = eurobis_dataset.EurobisDataset()
        data_archive2.load_dataset(test_dataset2)

        sum_len = 0
        for key in data_archive2.emof_indices:
            sum_len += len(data_archive2.emof_indices[key])

        assert (sum_len == len(data_archive2.emof_recs))
