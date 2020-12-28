import os
import sys
import time
import logging
from dwcaprocessor import DwCAProcessor

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
# print('__file__={0:<35} | __name__={1:<20} | __package__={2:<20}'.format(__file__,__name__,str(__package__)))

from eurobisqc import location
from eurobisqc import required_fields
from eurobisqc import taxonomy
from eurobisqc import time_qc
from eurobisqc import measurements

from eurobisqc.util import extract_area
from eurobisqc.test import file_chooser
from eurobisqc.util import qc_flags
from eurobisqc.util import misc

# Use "this" trick
this = sys.modules[__name__]
this.logger = logging.getLogger(__name__)


def dwca_file_labeling(filename, with_print=False, with_logging=True):
    """ Processes a DwCA archive if it is passed as a filename,
        shall popup a file chooser dialog if this is None
        :param filename (The DwCA zip file name)
        :param with_print (Extensive printing of the records)
        :param with_logging (every QC failed is printed) """

    if filename is None:
        # Adding a simple file chooser...
        filename = file_chooser.get_archive_chooser()

        if filename is None:
            exit(0)

    archive = DwCAProcessor(filename)

    # Do this once and forall
    geo_areas = extract_area.find_areas(archive.eml)

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

    # Stock in this list records for lookup (to execute QCs 6 and 19)
    records_for_lookup = []

    # Batch lookup size (should verify)
    lookup_batch_size = 1000
    count_lookups = 0

    # All net processing
    time_start = time.time()

    for coreRecord in archive.core_records():
        record_count += 1
        if with_print:
            print(f"---> core: {archive.core.type}")
        # Attempt check for lat/lon in full record
        full_core = coreRecord["full"]

        # Core Record (any type)
        # Check location

        qc_mask = location.check_basic_record(full_core)
        if "QC" in full_core:
            full_core["QC"] = full_core["QC"] | qc_mask
        else:
            full_core["QC"] = qc_mask
        if not qc_mask:
            records_for_lookup.append(full_core)
            if len(records_for_lookup) >= lookup_batch_size:
                location.check_xy(records_for_lookup)
                count_lookups += 1
                # Empty the list
                records_for_lookup = []

        # There are archives without Event records...
        if archive.core.type.lower() == "event":
            # Check location in area
            if geo_areas is not None:
                qc_mask = location.check_record_in_areas(full_core, geo_areas)
                full_core["QC"] = full_core["QC"] | qc_mask

            # Check dates (This is a repeat)
            qc_mask = time_qc.check_record(full_core, 0)
            full_core["QC"] = full_core["QC"] | qc_mask

        elif archive.core.type.lower() == "occurrence":

            # QC 9 (basis of records)
            qc_mask = required_fields.check_record_obis_format(full_core)
            if "QC" in full_core:
                full_core["QC"] = full_core["QC"] | qc_mask
            else:
                full_core["QC"] = qc_mask

            # QC 1 (required fields)
            qc_mask = required_fields.check_record_required(full_core)
            full_core["QC"] = full_core["QC"] | qc_mask

            # QC 4 and 5 (Check location)
            qc_mask = location.check_basic_record(full_core)
            full_core["QC"] = full_core["QC"] | qc_mask

            # QC 9 (Area Check)
            if geo_areas is not None:
                qc_mask = location.check_record_in_areas(full_core, geo_areas)
                full_core["QC"] = full_core["QC"] | qc_mask

            # QC 2 and 3 (Taxonomy)
            qc_mask = taxonomy.check_record(full_core)
            full_core["QC"] = full_core["QC"] | qc_mask

            # QC 7, 11, 12 13 (Dates - times)
            qc_mask = time_qc.check_record(full_core, 0)
            full_core["QC"] = full_core["QC"] | qc_mask

            # Sex
            qc_mask = measurements.check_sex_record(full_core)
            full_core["QC"] = full_core["QC"] | qc_mask

            # Dynamic properties
            qc_mask = measurements.check_dyn_prop_record(full_core)
            full_core["QC"] = full_core["QC"] | qc_mask

        # CANNOT BE
        # elif archive.core.type == "MeasurementOrFact" or archive.core.type == "ExtendedMeasurementOrFact":
        #     # Check measurements (this cannot be, this record type cannot ever be "Core",
        #     # so it is will never be called, looking for confirmation)
        #     qc_mask = measurements.check_record(full_core)
        #     if "QC" in full_core:
        #         full_core["QC"] = full_core["QC"] | qc_mask
        #     else:
        #         full_core["QC"] = qc_mask

        else:
            # Skip taxons and other record types
            full_core["QC"] = 0

        if with_logging and full_core["QC"] > 0:
            this.logger.error(f"Errors processing record {qc_flags.QCFlag.decode_mask(full_core['QC'])} "
                              f"record: : {full_core}")

        if with_print:
            print(full_core)

        for e in archive.extensions:
            if with_print:
                print("--- extension: " + e.type)
            if e.type.lower() in ["occurrence", "measurementorfact", "extendedmeasurementorfact" ]:
                for extensionRecord in archive.extension_records(e):
                    record_count += 1
                    full_extension = extensionRecord["full"]

                    if e.type.lower() == "occurrence":

                        # QC 9 (basis of records)
                        qc_mask = required_fields.check_record_obis_format(full_extension)
                        if "QC" in full_extension:
                            full_extension["QC"] = full_extension["QC"] | qc_mask
                        else:
                            full_extension["QC"] = qc_mask

                        # QC 1 (required fields)
                        qc_mask = required_fields.check_record_required(full_extension)
                        full_extension["QC"] = full_extension["QC"] | qc_mask

                        # Check location if necessary
                        if coord_in_occur:
                            qc_mask = location.check_basic_record(full_extension)
                            full_extension["QC"] = full_extension["QC"] | qc_mask
                            # Also add it for the lookup if OK
                            if not qc_mask:
                                records_for_lookup.append(full_extension)
                                if len(records_for_lookup) >= lookup_batch_size:
                                    location.check_xy(records_for_lookup)
                                    count_lookups += 1
                                    records_for_lookup = []

                        # Check taxonomy
                        qc_mask = taxonomy.check_record(full_extension)
                        full_extension["QC"] = full_extension["QC"] | qc_mask

                        # Check dates (This is a repeat)
                        qc_mask = time_qc.check_record(full_extension, 0)
                        full_extension["QC"] = full_extension["QC"] | qc_mask

                        # Check sex
                        qc_mask = measurements.check_sex_record(full_extension)
                        full_extension["QC"] = full_extension["QC"] | qc_mask

                        # Check dynamic properties
                        qc_mask = measurements.check_dyn_prop_record(full_extension)
                        full_extension["QC"] = full_extension["QC"] | qc_mask

                    elif e.type.lower() in ["measurementorfact", "extendedmeasurementorfact"]:
                        full_extension = extensionRecord["full"]
                        # Check measurements
                        qc_mask = measurements.check_record(full_extension)
                        if "QC" in full_extension:
                            full_extension["QC"] = full_extension["QC"] | qc_mask
                        else:
                            full_extension["QC"] = qc_mask

                    else:
                        # Skip taxons and other types
                        pass

                    if with_print:
                        print(full_extension)

                    if with_logging and full_extension["QC"] > 0:
                        this.logger.error(f"Errors processing record {qc_flags.QCFlag.decode_mask(full_extension['QC'])} "
                                          f"record: {full_extension}")

    # do I need a last lookup ?
    if len(records_for_lookup) >= 0:
        # The records will be modified with the correct QC flags so we do not care about the results
        location.check_xy(records_for_lookup)
        count_lookups += 1
        # Empty the list
        print(f"Records looked up: {1000 * (count_lookups - 1) + len(records_for_lookup)}")

    print(f"Filename processed: {filename}")
    print(f"XY lookups: {count_lookups}")
    print(f"Records processed: {record_count}")
    print(f"Total time: {time.time() - time_start}")


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
    result_pool=[]
    for i, dwca_file_list in enumerate(dwca_file_lists):
        result_pool.append(pool.apply_async(dwca_list_process, args=(i, dwca_file_list, False, False)))

    # We are interested in waiting, not getting the results...
    for r in result_pool:
        r.wait()

    # Should not harm
    pool.terminate()
    pool.join()


def dwca_list_process(pool_no, dwca_files, with_print=False, with_logging=False):
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


dwca_parallel_processing()
# dwca_file_labeling(None, with_print=False, with_logging=True)
# dwca_labeling(with_print=False, with_logging=False)
# exit(0)
