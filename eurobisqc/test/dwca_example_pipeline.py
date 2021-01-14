""" Demonstrates processing of a DwCa archive, calculating the QC for all records (Event and Occurrence=
    and escalating the QC for the measurements to their parent records. QCs are not stored.
    Also demonstrated processing of a list of files, that can be used for parallel processing
    (see run_dwca_multiprocess).
    """

import os
import sys
import time
import logging
from dwcaprocessor import DwCAProcessor

from eurobisqc import location
from eurobisqc import required_fields
from eurobisqc import taxonomy
from eurobisqc import time_qc
from eurobisqc import measurements

from eurobisqc.util import extract_area
from eurobisqc.test.util import file_chooser
from eurobisqc.util import qc_flags
from eurobisqc.util import misc

# Use "this" trick
this = sys.modules[__name__]
this.logger = logging.getLogger(__name__)


# for easy record mapping
class DwCACore:
    def __init__(self, core_record):
        self.core = core_record
        self.extensions = {}


# I use this only when printing / Logging. Due to its nature, the DwCAProcessor rescans the records
# and loses the results of QC upon resuming from scratch. DwCAProcessor tries to optimize memory usage
# And does not seem to provide the necessary kit to avoid searching back and forth.
dwca_cores = []


def dwca_file_labeling(filename, with_print=False, with_logging=False):
    """ Processes a DwCA archive if it is passed as a filename,
        shall popup a file chooser dialog if this is None
        :param filename (The DwCA zip file name)
        :param with_print (Extensive printing of the records)
        :param with_logging (every QC passed is printed)
    """

    if filename is None:
        exit(0)

    archive = DwCAProcessor(filename)

    # Once and for all
    geo_areas = extract_area.find_areas(archive.eml)

    archive_core_type = archive.core.type.lower()  # Can be occurrence or event

    # The core records are checked for lat lon in any case
    coord_in_occur = None

    # Determine whether occurrence records have LON LAT
    for ext_record in archive.extensions:
        if ext_record.type.lower() == "occurrence":
            if "decimalLatitude" in ext_record["fields"] and "decimalLongitude" in ext_record["fields"]:
                coord_in_occur = True
            else:
                coord_in_occur = False

    record_count = 0

    # Stock in this list records for lookup to execute QCs 6 and 19
    records_for_lookup = []

    # Batch lookup size (experimentally established, tried 100, 200, 500 and 1000)
    lookup_batch_size = 1000
    count_lookups = 0

    # to display file processing time
    time_start = time.time()
    records_by_key_for_ext_qc = {}

    for coreRecord in archive.core_records():
        record_count += 1

        # Attempt check for lat/lon in full record
        full_core = coreRecord["full"]
        full_core["type"] = archive_core_type

        dwca_core = DwCACore(full_core)
        dwca_cores.append(dwca_core)

        # All the extension records shall contribute to the core record QC
        records_by_key_for_ext_qc[coreRecord["pk"]] = full_core

        # Core Record (any type)
        # Check location
        qc_mask = location.check_basic_record(full_core)
        if "qc" in full_core:
            full_core["qc"] = full_core["qc"] | qc_mask
        else:
            full_core["qc"] = qc_mask

        # If locations are present and valid - QC 6 and 19 - all types
        if qc_mask & (qc_flags.QCFlag.GEO_LAT_LON_PRESENT.bitmask | qc_flags.QCFlag.GEO_LAT_LON_VALID.bitmask):
            records_for_lookup.append(full_core)
            if len(records_for_lookup) >= lookup_batch_size:
                location.check_xy(records_for_lookup)
                count_lookups += 1
                # Empty the list
                records_for_lookup = []

        full_core["type"] = archive.core.type.lower()

        if full_core["type"] == "event":

            # Check location in area
            if geo_areas is not None:
                qc_mask = location.check_record_in_areas(full_core, geo_areas)
                full_core["qc"] = full_core["qc"] | qc_mask

            # Check dates (This is a repeat)
            qc_mask = time_qc.check_record(full_core, 0)
            full_core["qc"] = full_core["qc"] | qc_mask

        elif archive.core.type.lower() == "occurrence":

            # QC 9 (basis of records)
            qc_mask = required_fields.check_record_obis_format(full_core)
            if "qc" in full_core:
                full_core["qc"] = full_core["qc"] | qc_mask
            else:
                full_core["qc"] = qc_mask

            # QC 1 (required fields)
            qc_mask = required_fields.check_record_required(full_core)
            full_core["qc"] = full_core["qc"] | qc_mask

            # QC 4 and 5 (Check location)
            qc_mask = location.check_basic_record(full_core)
            full_core["qc"] = full_core["qc"] | qc_mask

            # QC 9 (Area Check)
            if geo_areas is not None:
                qc_mask = location.check_record_in_areas(full_core, geo_areas)
                full_core["qc"] = full_core["qc"] | qc_mask

            # QC 2 and 3 (Taxonomy)
            qc_mask = taxonomy.check_record(full_core)
            full_core["qc"] = full_core["qc"] | qc_mask

            # QC 7, 11, 12 13 (Dates - times)
            qc_mask = time_qc.check_record(full_core, 0)
            full_core["qc"] = full_core["qc"] | qc_mask

            # Sex
            qc_mask = measurements.check_sex_record(full_core)
            full_core["qc"] = full_core["qc"] | qc_mask

            # Dynamic properties
            qc_mask = measurements.check_dyn_prop_record(full_core)
            full_core["qc"] = full_core["qc"] | qc_mask

        else:
            # Skip taxons and other record types
            full_core["qc"] = 0

        extensions_to_update = {}

        for e in archive.extensions:

            if e.type.lower() not in dwca_core.extensions:
                dwca_core.extensions[e.type.lower()] = []

            if e.type.lower() in ["occurrence", "measurementorfact", "extendedmeasurementorfact"]:
                for extensionRecord in archive.extension_records(e):
                    record_count += 1
                    full_extension = extensionRecord["full"]
                    full_extension["fk"] = extensionRecord["fk"]
                    full_extension["type"] = e.type.lower()

                    if e.type.lower() == "occurrence":

                        # Redundant, it must have ID!
                        occurrence_key = full_extension["occurrenceID"] if "occurrenceID" in full_extension else None

                        if occurrence_key is not None:
                            if occurrence_key in extensions_to_update:
                                # This record does not yet have QC - we are starting
                                full_extension["qc"] = extensions_to_update[occurrence_key]["qc"]
                            else:
                                extensions_to_update[occurrence_key] = full_extension

                        # QC 9 (basis of records)
                        qc_mask = required_fields.check_record_obis_format(full_extension)
                        if "qc" in full_extension:
                            full_extension["qc"] = full_extension["qc"] | qc_mask
                        else:
                            full_extension["qc"] = qc_mask

                        # QC 1 (required fields)
                        qc_mask = required_fields.check_record_required(full_extension)
                        full_extension["qc"] = full_extension["qc"] | qc_mask

                        # Check location if necessary
                        if coord_in_occur:
                            qc_mask = location.check_basic_record(full_extension)
                            full_extension["qc"] = full_extension["qc"] | qc_mask

                            # Also add it for the lookup if OK
                            if qc_mask & (qc_flags.QCFlag.GEO_LAT_LON_PRESENT.bitmask |
                                          qc_flags.QCFlag.GEO_LAT_LON_VALID.bitmask):
                                records_for_lookup.append(full_extension)
                                if len(records_for_lookup) >= lookup_batch_size:
                                    location.check_xy(records_for_lookup)
                                    count_lookups += 1
                                    records_for_lookup = []

                        # Check taxonomy
                        qc_mask = taxonomy.check_record(full_extension)
                        full_extension["qc"] = full_extension["qc"] | qc_mask

                        # Check dates (This is a repeat)
                        qc_mask = time_qc.check_record(full_extension, 0)
                        full_extension["qc"] = full_extension["qc"] | qc_mask

                        # Check sex
                        qc_mask = measurements.check_sex_record(full_extension)
                        full_extension["qc"] = full_extension["qc"] | qc_mask

                        # Check dynamic properties
                        qc_mask = measurements.check_dyn_prop_record(full_extension)
                        full_extension["qc"] = full_extension["qc"] | qc_mask

                        # This is an extension but it is also an occurrence. Update the core event record
                        full_core["qc"] |= full_extension["qc"]

                    elif e.type.lower() in ["measurementorfact", "extendedmeasurementorfact"]:

                        if archive.core.type.lower() == "event":
                            occurrence_key = full_extension[
                                "occurrenceID"] if "occurrenceID" in full_extension else None
                        else:
                            occurrence_key = None

                        full_extension = extensionRecord["full"]
                        # Check measurements
                        qc_mask = measurements.check_record(full_extension)

                        # Need tp update core record and possibly occurrence if core is event
                        if occurrence_key is not None:
                            # Update occurrence record
                            if occurrence_key in extensions_to_update:
                                extensions_to_update[occurrence_key]["qc"] |= qc_mask
                            else:
                                extensions_to_update[occurrence_key] = {"qc": qc_mask}

                        full_core["qc"] |= qc_mask

                    else:
                        # Skip taxons and other types
                        pass

                    dwca_core.extensions[e.type.lower()].append(full_extension)

    # do I need a last lookup ?
    if len(records_for_lookup) >= 0:
        # The records will be modified with the correct QC flags so we do not care about the results
        location.check_xy(records_for_lookup)

        # How do I update the event records if I passed occurrences to the lookup ? Looking them up in the reference!
        for record in records_for_lookup:
            if "fk" in record:
                records_by_key_for_ext_qc[record["fk"]]["qc"] |= record["qc"]

        count_lookups += 1

    if with_print:
        print(f"Filename processed: {filename}")
        print(f"Archive core record type: {archive_core_type}")
        print(f"XY lookups: {count_lookups}")
        print(f"Records looked up: {1000 * (count_lookups - 1) + len(records_for_lookup)}")
        print(f"Records processed: {record_count}")
        print(f"Total time: {time.time() - time_start}")

    if with_logging:
        this.logger.info(f"Filename processed: {filename}")
        this.logger.info(f"Archive core record type: {archive_core_type}")
        this.logger.info(f"XY lookups: {count_lookups}")
        this.logger.info(f"Records looked up: {1000 * (count_lookups - 1) + len(records_for_lookup)}")
        this.logger.info(f"Records processed: {record_count}")
        this.logger.info(f"Total time: {time.time() - time_start}")

    # Rescan the prepared lookup for printing/logging the results
    if with_print:
        for print_record in dwca_cores:
            if print_record.core["qc"] > 0:
                print(f"--- core: {archive_core_type}")
                print(print_record.core)
                print(f"The core record passed quality checks: {qc_flags.QCFlag.decode_mask(print_record.core['qc'])}")

            for e in print_record.extensions.keys():
                for full_extension in print_record.extensions[e]:
                    print(f"--- extension: {e}")
                    if e == "occurrence":
                        print(
                            f"The occurrence record {full_extension}\n Passed quality checks: "
                            f"{qc_flags.QCFlag.decode_mask(full_extension['qc'])}")
                    else:
                        print(full_extension)

    if with_logging:
        for print_record in dwca_cores:
            if print_record["qc"] > 0:
                this.logger.info(f"Core record {print_record}. \nPassed quality checks: "
                                 f"{qc_flags.QCFlag.decode_mask(print_record['qc'])}")

            for e in print_record.extensions.keys():

                for full_extension in print_record.extensions[e]:
                    this.logger.info(f"--- extension: {e}")
                    if e == "occurrence":
                        this.logger.info(f"The occurrence record {full_extension} passed quality checks: "
                                         f"{qc_flags.QCFlag.decode_mask(full_extension['qc'])} ")
                    else:
                        if with_logging:
                            this.logger.info(full_extension)


def dwca_parallel_processing():
    """ Example of processing multiple files at the same time in
        order to exploit the computing resources of the machine """
    import multiprocessing as mp

    # we dedicate to the task the total number of processors - 2 or 1 if we only have 2 cores or less
    if mp.cpu_count() > 2:
        n_cpus = mp.cpu_count() - 2
    else:
        n_cpus = 1

    pool = mp.Pool(n_cpus)

    # Get the list of files in a directory, containing ONLY DwCA zip files...
    folder = file_chooser.browse_for_folder()

    if folder is None or folder.strip() == "":
        this.logger.log(0, "Invalid Directory selection")

    dwca_files = os.listdir(folder)

    if dwca_files is None or len(dwca_files) == 0:
        this.logger.error("No files to process")

    # Adding path info to file names in temp list...
    fnames = [os.path.join(folder, f) for f in dwca_files
              if os.path.isfile(os.path.join(folder, f))
              and f.lower().endswith(".zip")
              ]

    dwca_files = fnames

    if dwca_files is None:
        exit(0)

    dwca_file_lists = misc.split_list(dwca_files, n_cpus)
    print(dwca_file_lists)

    # Each one of the CPUs shall get a similar load...
    result_pool = []
    for i, dwca_file_list in enumerate(dwca_file_lists):
        result_pool.append(pool.apply_async(dwca_process_filelist, args=(i, dwca_file_list, False, False)))

    # We are interested in waiting, not getting the results...
    for r in result_pool:
        r.wait()

    # Should not harm
    pool.terminate()
    pool.join()


def dwca_process_filelist(pool_no, dwca_files, with_print=False, with_logging=False):
    """ Processes a list of DwCA archives, ideally to be called in parallel
        :param pool_no - Pool number to take track of the pools
        :param dwca_files (The list of files to be processed)
        :param with_print (Extensive printouts of records being treated9
        :param with_logging (Logs on screen every QC failed) """

    # Prints pool data
    start = time.time()
    print(f"Pool {pool_no} started")
    for dwca_file in dwca_files:
        start_file = time.time()
        print(f"Pool Number: {pool_no}, processsing {dwca_file} ")

        if with_logging:
            this.logger.log(0, f"Processing DwCA file {dwca_file} ")

        dwca_file_labeling(dwca_file, with_print, with_logging)
        print(f"Processed {dwca_file} in  {time.time() - start_file}")

    print(f"Pool {pool_no} completed in {time.time() - start}")
    return pool_no

# dwca_parallel_processing()
# dwca_file_labeling(None, with_print=True, with_logging=False)
# dwca_labeling(with_print=False, with_logging=False)
# exit(0)
