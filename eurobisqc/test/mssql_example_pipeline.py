import sys
import logging
import time
from _functools import reduce

from eurobisqc import required_fields
from eurobisqc.test.util import dataset_chooser
from eurobisqc import eurobis_dataset
from eurobisqc import location
from eurobisqc import time_qc
from eurobisqc import measurements
from eurobisqc import taxonomy
from eurobisqc.util import qc_flags


# All QCs

# Use "this" trick
this = sys.modules[__name__]
this.logger = logging.getLogger(__name__)


def dataset_qc_labeling(dataset_id, with_print=False, with_logging=True, with_record_times=False):
    """ Processes an eurobis dataset if it is passed as a dataset_id,
        shall popup a file chooser dialog if this is None
        :param dataset_id (The dataset identifier from the dataproviderstable)
        :param with_print (Extensive printing of the records)
        :param with_logging (every QC passed is printed) """

    if dataset_id is None:
        # Adding a simple file chooser...
        dataset_id = dataset_chooser.get_dataset_chooser()

        # No choice made...
        if dataset_id is None:
            exit(0)

    data_archive = eurobis_dataset.EurobisDataset()
    data_archive.load_dataset(dataset_id)

    if with_print:
        print(f"Loaded dataset {data_archive.dataset_name}, id = {data_archive.dataprovider_id}")
        print(f"Number of event records: {len(data_archive.event_recs)}")
        print(f"Number of occurrence records: {len(data_archive.occurrence_recs)}")
        print(f"Number of emof records: {len(data_archive.emof_recs)}")
        print(f"Interesting areas: {data_archive.areas}")
        print(f"Imis dataset ID: {data_archive.imis_das_id}")
        print(f"Type of core records: {'Event' if data_archive.darwin_core_type ==2 else 'Occurrence'}")


    if with_logging:
        this.logger.log(0, f"Loaded dataset {data_archive.dataset_name}, id = {data_archive.dataprovider_id} ")
        this.logger.log(0,f"Number of event records: {len(data_archive.event_recs)}")
        this.logger.log(0,f"Number of occurrence records: {len(data_archive.occurrence_recs)}")
        this.logger.log(0,f"Number of emof records: {len(data_archive.emof_recs)}")
        this.logger.log(0,f"Interesting areas: {data_archive.areas}")
        this.logger.log(0,f"Imis dataset ID: {data_archive.imis_das_id}")
        this.logger.log(0,f"Type of core records: {'Event' if data_archive.darwin_core_type ==2 else 'Occurrence'}")

    # Starting the QCs: First events, then occurrences. For each one, the QC shall be
    # augmented with the emof records. What to do if the records already have QC assigned ?

    # After loading, measure processing time
    time_start = time.time()

    # Build a batch for coordinate lookup
    # Batch lookup size (should verify)
    lookup_batch_size = 1000
    count_lookups = 0
    records_for_lookup = []

    event_count = 0

    for record in data_archive.event_recs:

        event_start = time.time()
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
            records_for_lookup.append(record)
            # Execute lookup if necessary
            if len(records_for_lookup) >= lookup_batch_size:
                location.check_xy(records_for_lookup)
                count_lookups += 1
                # Empty the list
                records_for_lookup = []

        # QC for the ev. records : time (7, 11, 12, 13)
        record["qc"] |= time_qc.check_record(record, 0)

        # Do the measurement of facts QC for the event records (14, 15, 16, 17)
        # Construct "key"
        key = f"{record['dataprovider_id']}_{'NULL' if record['eventID'] is None else record['eventID']}_" \
              f"{'NULL' if record['occurrenceID'] is None else record['occurrenceID']}"

        if key in data_archive.emof_indices:
            measurements_qc = measurements.check(data_archive.emof_indices[key])

            # These are per single emof record, or them together and then to the event record
            record["qc"] |= reduce(lambda x, y: x | y, measurements_qc)

        event_elapsed = time.time() - event_start
        if with_record_times:
            print(f"Event record {event_count} processed in {event_elapsed}")
        event_count += 1

    # Before proceeding to the occurrence records, check that lookups are all done
    if len(records_for_lookup) > 0:
        location.check_xy(records_for_lookup)
        count_lookups += 1
        # Empty the list
        records_for_lookup = []

    # FLAG: EVENT Records do no get checked for basic required fields and taxonomy (occurrence do).
    # Done with event records, processing Occurrences, same criteria, additional QCs
    occurrence_count = 0
    for record in data_archive.occurrence_recs:

        occurrence_start = time.time()
        # None means that records have not been quality checked 0 means that QCs have been attempted
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
            records_for_lookup.append(record)
            # Execute lookup if necessary
            if len(records_for_lookup) >= lookup_batch_size:
                location.check_xy(records_for_lookup)
                count_lookups += 1
                # Empty the list
                records_for_lookup = []

        # QC for the occ. records: taxonomy (2, 3)
        record["qc"] |= taxonomy.check_record(record)

        # QC for the occ. records : time (7, 11, 12, 13)
        record["qc"] |= time_qc.check_record(record, 0)

        # Do the measurement of facts QC for the event records (14, 15, 16, 17)
        # Construct "key"
        key = f"{record['dataprovider_id']}_{'NULL' if record['eventID'] is None else record['eventID']}_" \
              f"{'NULL' if record['occurrenceID'] is None else record['occurrenceID']}"

        if key in data_archive.emof_indices:
            measurements_qc = measurements.check(data_archive.emof_indices[key])

            # These are per single emof record, or them together and then to the event record
            record["qc"] |= reduce(lambda x, y: x | y, measurements_qc)
            record["qc"] |= reduce(lambda x, y: x | y, measurements_qc)
        else :
            # Noticed difference in keying
            key = f"{record['dataprovider_id']}_NULL_{'NULL' if record['occurrenceID'] is None else record['occurrenceID']}"
            if key in data_archive.emof_indices:
                measurements_qc = measurements.check(data_archive.emof_indices[key])
                # These are per single emof record, or them together and then to the event record
                record["qc"] |= reduce(lambda x, y: x | y, measurements_qc)


        # QC for occ. : sex (17)
        record["qc"] |= measurements.check_sex_record(record)

        occurrence_elapsed = time.time() - occurrence_start
        if with_record_times:
            print(f"Occurrence record {occurrence_count} processed in {occurrence_elapsed}")

        occurrence_count += 1

    # Before proceeding to the occurrence records, check that lookups are all done
    if len(records_for_lookup) > 0:
        location.check_xy(records_for_lookup)
        count_lookups += 1
        # Empty the list
        records_for_lookup = []

    duration = time.time() - time_start
    # Dataset QC finished, taking time.
    if with_print:
        print(f"All records processed")
        print(f"Total net processing time for {data_archive.dataset_name}: {duration}")
    if with_logging:
        this.logger.log(0, f"Processed dataset {data_archive.dataset_name} in: {duration} ")


# To call it...
dataset_qc_labeling(None, with_print=True, with_logging=False, with_record_times=False)
