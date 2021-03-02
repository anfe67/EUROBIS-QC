import sys
import logging
from unittest import TestCase

from eurobisqc import required_fields
from eurobisqc import location
from eurobisqc import taxonomy
from eurobisqc import time_qc
from eurobisqc import measurements
from eurobisqc import qc_flags
from eurobisqc import eurobis_dataset
from dbworks import mssql_db_functions

this = sys.modules[__name__]
this.logger = logging.getLogger(__name__)
this.logger.level = logging.DEBUG
this.logger.addHandler(logging.StreamHandler())

class Test(TestCase):

    def test_dataset_nulls_in_occurrences(self):
        test_dataset = 1079
        test_event_id = "HS2014_12"
        # Custom query to limit the results (26 records)
        data_archive = eurobis_dataset.EurobisDataset()
        sql_string = data_archive.query_builder_eve_occur(test_dataset)[:-1]
        sql_string += f" and EventID = '{test_event_id}';"
        num_records = 26


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

        assert (len(records) == num_records)

        res = []

        for record in records:
            if record["qc"] is None:
                record["qc"] = 0

                # QC for the occ records: required fields: (1, 10)
            record["qc"] |= required_fields.check_record_required(record)
            record["qc"] |= required_fields.check_record_obis_format(record)

            # QC for the occ. records : location basic (4, 5, 18)
            record["qc"] |= location.check_basic_record(record)

            # QC for the ev. records : areas (9) - SKIP FOR NOW

            records_for_lookup =[]

            # QC for the occ. records : building batch for API call (6, 19)
            if record["qc"] & (qc_flags.QCFlag.GEO_LAT_LON_VALID.bitmask | qc_flags.QCFlag.GEO_LAT_LON_PRESENT.bitmask):
                records_for_lookup.append(record)
                # Execute lookup if necessary
            if len(records_for_lookup) > 0:
                location.check_xy(records_for_lookup)

            # QC for the occ. records: taxonomy (2, 3)
            record["qc"] |= taxonomy.check_record(record)

            # QC for the occ. records : time (7, 11, 12, 13)
            record["qc"] |= time_qc.check_record(record, 0)

            # QC for occ. : sex (17)
            record["qc"] |= measurements.check_sex_record(record)

            # Do the measurement of facts QC for the event records (14, 15, 16, 17)
            # This processes all emof records belonging to this occurrence record

            # This is useful for when core record = event
            res.append(record["qc"])

        print(res)
