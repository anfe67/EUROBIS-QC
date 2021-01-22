""" Module to demonstrate QC labeling of a random record """

import sys
import time
import logging
from random import randint

from eurobisqc import required_fields
from dbworks import mssql_db_functions as mssql
from eurobisqc import eurobis_dataset
from eurobisqc.examples import mssql_example_pipeline
from eurobisqc.util.qc_flags import QCFlag
from eurobisqc import location

this = sys.modules[__name__]
this.logger = logging.getLogger(__name__)
this.logger.level = logging.DEBUG
this.logger.addHandler(logging.StreamHandler())


def select_random_ds(with_logging = True):
    """ select a random dataset, then a random core event from it and perform QC """

    # This selects 1 dataset with  less than 10000 events/occurrences reported in the dataproviders table
    sql_random_dataset = f"SELECT TOP 1  d.id, count(e.dataprovider_id) FROM  dataproviders d " \
                         f" inner join eurobis e on d.id = e.dataprovider_id group by d.id " \
                         f" having count(e.dataprovider_id) < 10000 ORDER BY NEWID()"

    # Go and get the id!
    dataset_id = None
    # Connect to the database to get dataset list
    if not mssql.conn:
        mssql.open_db()

    if mssql.conn is None:
        # Should find a way to exit and advice
        this.logger.error("No connection to DB, nothing can be done! ")
        exit(0)
    else:
        # Fetch a random set of datasets
        cur = mssql.conn.cursor()
        cur.execute(sql_random_dataset)
        dataset = cur.fetchone()
        dataset_id = dataset[0]

    data_archive = eurobis_dataset.EurobisDataset()
    data_archive.load_dataset(dataset_id)

    if with_logging:
        this.logger.info(f"--------------------------------------------------")
        this.logger.info(f"Loaded dataset {data_archive.dataset_name}, id = {data_archive.dataprovider_id} ")
        this.logger.info(f"Number of event records: {len(data_archive.event_recs)}")
        this.logger.info(f"Number of occurrence records: {len(data_archive.occurrence_recs)}")
        this.logger.info(f"Number of emof records: {len(data_archive.emof_recs)}")
        this.logger.info(f"Interesting areas: {data_archive.areas}")
        this.logger.info(f"Imis dataset ID: {data_archive.imis_das_id}")
        this.logger.info(f"Type of core records: {'Event' if data_archive.darwin_core_type == 2 else 'Occurrence'}")
        this.logger.info(f"--------------------------------------------------")
    pass

    # Now everything is in data_archive, we must select a random CORE record, and its children, calculate QC and
    # display all records that originate that reasoning.
    # Proceed top-down as in pipeline ...
    if data_archive.darwin_core_type == data_archive.EVENT:
        # select random core event:
        record_idx = randint(0, len(data_archive.event_recs)-1)
        record = data_archive.event_recs[record_idx]

        # Perform basic QC:
        qc_ev = mssql_example_pipeline.qc_event(record, data_archive)

        # Generate key and lookup occurrences...
        key = f"{record['dataprovider_id']}_{record['eventID']}"
        if key in data_archive.occ_indices:
            for occ_record in data_archive.occ_indices[key]:
                # qc_occurrence sall also take care of emof for occurrence
                qc_occ = mssql_example_pipeline.qc_occurrence(occ_record, data_archive)
                occ_record['qc'] |= qc_occ  # also give to occurrence record
                qc_ev |= qc_occ
            record['qc'] |= qc_ev

            # Needs to propagate the REQUIRED FIELDS CHECK for the event and its occurrences
            qc_req_agg = []
            qc_req_agg.append(record)
            qc_req_agg.extend(data_archive.occ_indices[key])
            record["qc"] |= required_fields.check_aggregate(qc_req_agg)
            qc_ev |= record["qc"]

        # Are there any lookups left to do (any record type)?
        if len(data_archive.records_for_lookup):
            location.check_xy(data_archive.records_for_lookup)
            # Grab the QCs and then empty the list
            for lookup_record in data_archive.records_for_lookup:
                record["qc"] |= lookup_record["qc"]
                qc_ev |= lookup_record["qc"]
            # Empty the lookup "table"
            data_archive.records_for_lookup = []

        this.logger.info(f"Calculated quality mask: {qc_ev}, consisting of:")
        this.logger.info(f"QC NUMBERS: -------------> {QCFlag.decode_numbers(qc_ev)}")
        this.logger.info(f"QC FLAG NAMES: ----------> {QCFlag.decode_mask(qc_ev)}")
        this.logger.info(f"--------------------------------------------------")
        this.logger.info(f"Event Record: {record}")
        this.logger.info(f"--------------------------------------------------")

        if key in data_archive.occ_indices:
            for occ_record in data_archive.occ_indices[key]:
                this.logger.info(f"Occurrence Record: {occ_record}")
                this.logger.info(f"Calculated quality mask: {occ_record['qc']}, consisting of:")
                this.logger.info(f"QC NUMBERS: -------------> {QCFlag.decode_numbers(occ_record['qc'])}")
                this.logger.info(f"QC FLAG NAMES: ----------> {QCFlag.decode_mask(occ_record['qc'])}")
                this.logger.info(f"--------------------------------------------------")
                key_o =  f"{record['dataprovider_id']}_{'NULL' if record['eventID'] is None else record['eventID']}_" \
                         f"{'NULL' if record['occurrenceID'] is None else record['occurrenceID']}"
                if key_o in data_archive.emof_indices:
                    for emof in data_archive.emof_indices[key_o]:
                        this.logger.info(f"eMoF Record: {emof}")
                        this.logger.info(f"--------------------------------------------------")

    else:
        # The QC is either 0 or a QC mask
        record_idx = randint(0, len(data_archive.occurrence_recs)-1)
        record = data_archive.occurrence_recs[record_idx]
        qc_occ = mssql_example_pipeline.qc_occurrence(record, data_archive)

        # Are there any lookups left to do (any record type)?
        if len(data_archive.records_for_lookup):
            location.check_xy(data_archive.records_for_lookup)

            for lookup_record in data_archive.records_for_lookup:
                record['qc'] |= lookup_record["qc"]
                qc_occ |= lookup_record["qc"]

            data_archive.records_for_lookup = []

        this.logger.info(f"Calculated quality mask: {qc_occ}, consisting of:")
        this.logger.info(f"QC NUMBERS: -------------> {QCFlag.decode_numbers(qc_occ)}")
        this.logger.info(f"QC FLAG NAMES: ----------> {QCFlag.decode_mask(qc_occ)}")
        this.logger.info(f"--------------------------------------------------")
        this.logger.info(f"Occurrence Record: {record}")
        this.logger.info(f"--------------------------------------------------")

        key_o = f"{record['dataprovider_id']}_NULL_" \
              f"{'NULL' if record['occurrenceID'] is None else record['occurrenceID']}"
        if key_o in data_archive.emof_indices:
            for emof in data_archive.emof_indices[key_o]:
                this.logger.info(f"eMoF Record: {emof}")
                this.logger.info(f"--------------------------------------------------")

select_random_ds()
