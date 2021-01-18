import sys
import logging
import time

import mssql_db_functions
from unittest import TestCase

this = sys.modules[__name__]
this.logger = logging.getLogger(__name__)
this.logger.setLevel(logging.DEBUG)
this.logger.addHandler(logging.StreamHandler())


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

        this.logger.info(results)

    def test_retrieve_sample_dataset(self):
        """ simple example to retrieve a dataset of only occurrences and measurementorfact records
            Note: This is not useful for the update, as there are no ids to push the QC back to DB
            for the moment it is only an experiment. (and the number of datasets does not match)
        """

        start_time = time.time()

        collection = 'BayOfPuck'

        mssql_db_functions.open_db()
        cursor1 = mssql_db_functions.conn.cursor()
        cursor1.execute(f"SELECT  * from eurobis where collectionCode ='BayOfPuck';")
        columns = [column[0] for column in cursor1.description]
        event_or_occurrences = []
        for row in cursor1:
            event_or_occurrences.append(dict(zip(columns, row)))
        # cursor1.close()

        # cursor2 = mssql_db_functions.conn.cursor()
        cursor1.execute(
            f"SELECT  eurobis_measurementorfact.* from eurobis join eurobis_measurementorfact on "
            f"eurobis.occurrenceID = "
            f"eurobis_measurementorfact.occurrenceID where eurobis.CollectionCode ='{collection}'")

        columns = [column[0] for column in cursor1.description]
        emof = []
        for row in cursor1:
            emof.append(dict(zip(columns, row)))
        cursor1.close()

        this.logger.info(f"Duration: {time.time() - start_time}")
        this.logger.info(
            f"Number of event/occurrences: {len(event_or_occurrences)}, number of emof records: {len(emof)}")
        this.logger.info(event_or_occurrences[len(event_or_occurrences) - 1])
        this.logger.info(emof[len(emof) - 1])
