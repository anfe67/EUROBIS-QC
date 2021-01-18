import sys
import logging
import time
from _functools import reduce
from eurobisqc import required_fields
from eurobisqc import eurobis_dataset
from eurobisqc import location
from eurobisqc import time_qc
from eurobisqc import measurements
from eurobisqc import taxonomy
from eurobisqc.util import qc_flags
from dbworks import mssql_db_functions as mssql
from eurobisqc.util import misc

# Use "this" trick
this = sys.modules[__name__]
this.logger = logging.getLogger(__name__)
this.logger.level = logging.DEBUG
this.logger.addHandler(logging.StreamHandler())

this.count_pyxylookups = 0


def qc_event(record, data_archive):
    # None means that records have not been quality checked 0 means that QCs have been attempted
    if record["qc"] is None:
        record["qc"] = 0

    # QC for the ev. records : location basic (4, 5, 18)
    record["qc"] |= location.check_basic_record(record)
    # QC for the ev. records : areas (9)
    if data_archive.areas is not None:
        record["qc"] |= location.check_record_in_areas(record, data_archive.areas)

    # QC for the ev. records : building batch for API call (6, 19)
    if record["qc"] & (qc_flags.QCFlag.GEO_LAT_LON_VALID.bitmask | qc_flags.QCFlag.GEO_LAT_LON_PRESENT.bitmask):
        data_archive.records_for_lookup.append(record)
        # Execute lookup if necessary
        if len(data_archive.records_for_lookup) >= data_archive.LOOKUP_BATCH_SIZE:
            location.check_xy(data_archive.records_for_lookup)
            this.count_pyxylookups += 1
            this.logger.debug(f"Lookups: {this.count_pyxylookups}")
            # Empty the list
            data_archive.records_for_lookup = []

    # QC for the ev. records : time (7, 11, 12, 13)
    record["qc"] |= time_qc.check_record(record, 0)

    # Look at the event related eMoF records  (14, 15, 16, 17)
    record["qc"] |= qc_emof(record, data_archive)

    return record["qc"]


def qc_occurrence(record, data_archive):
    if record["qc"] is None:
        record["qc"] = 0

    # QC for the occ records: required fields: (1, 10)
    record["qc"] |= required_fields.check_record_required(record)
    record["qc"] |= required_fields.check_record_obis_format(record)

    # QC for the occ. records : location basic (4, 5, 18)
    record["qc"] |= location.check_basic_record(record)

    # QC for the ev. records : areas (9)
    if data_archive.areas is not None:
        record["qc"] |= location.check_record_in_areas(record, data_archive.areas)

    # QC for the occ. records : building batch for API call (6, 19)
    if record["qc"] & (qc_flags.QCFlag.GEO_LAT_LON_VALID.bitmask | qc_flags.QCFlag.GEO_LAT_LON_PRESENT.bitmask):
        data_archive.records_for_lookup.append(record)
        # Execute lookup if necessary
        if len(data_archive.records_for_lookup) >= data_archive.LOOKUP_BATCH_SIZE:
            location.check_xy(data_archive.records_for_lookup)
            this.count_pyxylookups += 1
            this.logger.debug(f"Lookups: {this.count_pyxylookups}")
            # Empty the list
            data_archive.records_for_lookup = []

    # QC for the occ. records: taxonomy (2, 3)
    record["qc"] |= taxonomy.check_record(record)

    # QC for the occ. records : time (7, 11, 12, 13)
    record["qc"] |= time_qc.check_record(record, 0)

    # QC for occ. : sex (17)
    record["qc"] |= measurements.check_sex_record(record)

    # Do the measurement of facts QC for the event records (14, 15, 16, 17)
    # This processes all emof records belonging to this occurrence record
    record["qc"] |= qc_emof(record, data_archive)

    # This is useful for when core record = event
    return record["qc"]


def qc_emof(record, data_archive):
    """ Processes all emof records for record (both event type or occurrence)
        :param record: The Occurrence or Event Record
        :param data_archive: The archive being processed
        :returns the calculated joined qc for the emof records """

    qc_em = 0

    if data_archive.darwin_core_type == data_archive.EVENT:
        key = f"{record['dataprovider_id']}_{'NULL' if record['eventID'] is None else record['eventID']}_" \
              f"{'NULL' if record['occurrenceID'] is None else record['occurrenceID']}"
    else:
        key = f"{record['dataprovider_id']}_NULL_" \
              f"{'NULL' if record['occurrenceID'] is None else record['occurrenceID']}"

    if key in data_archive.emof_indices:
        measurements_qc = measurements.check(data_archive.emof_indices[key])
        # These are per single emof record, "or" them together
        qc_em |= reduce(lambda x, y: x | y, measurements_qc)

    return qc_em


def dataset_qc_labeling(dataset_id, with_logging=True):
    """ Processes an eurobis dataset if it is passed as a dataset_id,
        shall popup a file chooser dialog if this is None
        :param dataset_id (The dataset identifier from the dataproviderstable)
        :param with_logging (every QC passed is printed)
        """

    if dataset_id is None:
        exit(0)

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


    # Starting the QCs:

    # After loading, measure processing time
    time_start = time.time()

    # Proceed top-down...
    if data_archive.darwin_core_type == data_archive.EVENT:
        # For all event records, qc event, then occurrence records
        # (which shall recurse into eMof), then own eMof and then "or" all
        for record in data_archive.event_recs:
            # qc_event shall also take care of emof for event
            qc_ev = qc_event(record, data_archive)

            # Generate key and lookup occurrences...
            key = f"{record['dataprovider_id']}_{record['eventID']}"
            if key in data_archive.occ_indices:
                for occ_record in data_archive.occ_indices[key]:
                    # qc_occurrence sall also take care of emof for occurrence
                    qc_occ = qc_occurrence(occ_record, data_archive)
                    occ_record['qc'] |= qc_occ  # also give to occurrence record
                    qc_ev |= qc_occ
                record['qc'] |= qc_ev

    else:  # Only occurrence and emof records
        for occ_record in data_archive.occurrence_recs:
            # The QC is either 0 or a QC mask
            qc_occurrence(occ_record, data_archive)

    # Are there any lookups left to do (any record type)?
    if len(data_archive.records_for_lookup):
        location.check_xy(data_archive.records_for_lookup)
        this.count_pyxylookups += 1
        this.logger.debug(f"Lookups: {this.count_pyxylookups}")
        # Empty the list
        data_archive.records_for_lookup = []

    # RECORD UPDATE!
    process_batch = []
    process_batch_size = 500  # Shall commit at every batch
    for idx, record in enumerate(data_archive.event_recs, 1):
        # pass batches of 100 records to the update method
        process_batch.append(record)
        if idx % process_batch_size == 0:
            eurobis_dataset.EurobisDataset.update_record_qc(process_batch, process_batch_size)
            process_batch = []

    # Leftovers
    if len(process_batch):
        eurobis_dataset.EurobisDataset.update_record_qc(process_batch, process_batch_size)
        process_batch = []

    eurobis_dataset.EurobisDataset.record_batch_update_count = 0

    for idx, record in enumerate(data_archive.occurrence_recs, 1):
        # pass batches of 100 records to the update method
        process_batch.append(record)
        if idx % process_batch_size == 0:
            eurobis_dataset.EurobisDataset.update_record_qc(process_batch, process_batch_size)
            process_batch = []
    # Leftovers
    if len(process_batch):
        eurobis_dataset.EurobisDataset.update_record_qc(process_batch, process_batch_size)

    duration = time.time() - time_start
    # Dataset QC finished, taking time.

    if with_logging:
        this.logger.info(f"Total net processing time for {data_archive.dataprovider_id} : {data_archive.dataset_name} in: {duration} ")


def process_dataset_list(pool_no, dataset_id_list, with_logging=False):
    """ Processes a list of DwCA archives, ideally to be called in parallel
        :param pool_no - Pool number to take track of the pools
        :param dataset_id_list (The list of datasets to be processed)
        :param with_logging (Logging enabled or not) """
    # Prints pool data
    start = time.time()
    if with_logging:
        this.logger.info(f"Pool {pool_no} started")

    # Connect to the database, each pool should have its own connection
    conn = None
    if not mssql.conn:
        conn = mssql.open_db()

    if conn is None:
        # Should find a way to exit and advice
        this.log.error("No connection to DB, nothing can be done! ")
        return pool_no

    for dataset_id in dataset_id_list:
        start_file = time.time()

        if with_logging:
            this.logger.info(f"Pool Number: {pool_no}, processsing dataset {dataset_id} ")

        dataset_qc_labeling(dataset_id, with_logging)
        if with_logging:
            this.logger.info(f"Processed dataset {dataset_id} in  {time.time() - start_file}")

    if with_logging:
        this.logger.info(f"Pool {pool_no} completed in {time.time() - start}")
    return pool_no


# To call single file labelling with a chooser use run_mssql_pipeline

# Single dataset  - Fixed - need eurobis.dataprovider_id (id in dataproviders table)
# dataset_qc_labeling(447, with_logging=True)

# Launch individual processing of dataset list, datasets to be picked
# process_dataset_list(1, [723, 239], True, False)

