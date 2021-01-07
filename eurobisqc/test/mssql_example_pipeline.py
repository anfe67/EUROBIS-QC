import sys
import logging
from eurobisqc.test.util import dataset_chooser
from eurobisqc import dataset
from eurobisqc import location
from eurobisqc import time_qc

# All QCs

# Use "this" trick
this = sys.modules[__name__]
this.logger = logging.getLogger(__name__)


def dataset_qc_labeling(dataset_id, with_print=False, with_logging=True):
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

    data_archive = dataset.Dataset()
    data_archive.load_dataset(dataset_id)

    if with_print:
        print(f"Loaded dataset {data_archive.dataset_name}, id = {data_archive.dataprovider_id}")

    if with_logging:
        this.logger.log(0, f"Loaded dataset {data_archive.dataset_name}, id = {data_archive.dataprovider_id} ")

    # Starting the QCs: First events, then occurrences. For each one, the QC shall be
    # augmented with the emof records. What to do if the records already have QC assigned ?

    # Build a batch for coordinate lookup

    for record in data_archive.event_recs:
        # None means that records have not been quality checked 0 means that QCs have been attempted
        if record["qc"] is None:
            record["qc"] = 0

        # QC for the ev. records : location basic (4, 5, 18)
        record["qc"] |= location.check_basic_record(record)
        # QC for the ev. records : areas (9)
        if data_archive.areas is not None:
            record["qc"] |= location.check_record_in_areas(record, data_archive.areas)
        # QC for the ev. records : time (7, 11, 12, 13)
        record["qc"] |= time_qc.check_record(record, 0)


dataset_qc_labeling(None, with_print=True, with_logging=False)
