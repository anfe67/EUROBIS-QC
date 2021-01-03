import mssql_db_functions
from unittest import TestCase


class Test(TestCase):
    table = 'dp_countries'

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

    def test_retrieve_sample_dataset(self):
        """ simple example to retrieve a dataset of only occurrences and measurementorfact records
            Note: This is not useful for the update, as there are no ids to push the QC back to DB
            for the moment it is only an experiment. (and the number of datasets does not match)
        """

        collection = 'BayOfPuck'

        mssql_db_functions.open_db()
        cursor1 = mssql_db_functions.conn.cursor()
        cursor1.execute(f"SELECT  * from eurobis where collectionCode ='BayOfPuck';")
        columns = [column[0] for column in cursor1.description]
        event_or_occurrences = []
        for row in cursor1:
            event_or_occurrences.append(dict(zip(columns, row)))

        cursor2 = mssql_db_functions.conn.cursor()
        cursor2.execute(
            f"SELECT  eurobis_measurementorfact.* from eurobis join eurobis_measurementorfact on eurobis.occurrenceID = "
            f"eurobis_measurementorfact.occurrenceID where eurobis.CollectionCode ='{collection}'")

        columns = [column[0] for column in cursor2.description]
        emof = []
        for row in cursor2:
            emof.append(dict(zip(columns, row)))

        print(f"Number of event/occurrences: {len(event_or_occurrences)}, number of emof records: {len(emof)}")
        print(event_or_occurrences[len(event_or_occurrences) - 1])
        print(emof[len(emof) - 1])
