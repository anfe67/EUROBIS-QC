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

# Adding a simple file chooser...
filename = file_chooser.get_archive_chooser()

if filename is None:
    exit(0)

logger = logging.getLogger(__name__)

archive = DwCAProcessor(filename)

# Do this once and forall
geo_area = extract_area.find_area(archive.eml)

# The core records are checked for lat lon in any case
coord_in_occur = None

# Determine whether occurrence records have LON LAT
for ext_record in archive.extensions:
    if ext_record.type == "Occurrence":
        if "decimalLatitude" in ext_record["fields"] and "decimalLongitude" in ext_record["fields"]:
            coord_in_occur = True
        else:
            coord_in_occur = False

record_count = 0
with_print = False
with_logging = True

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
    if archive.core.type == "Event":
        # Check location in area
        if geo_area is not None:
            qc_mask = location.check_record_in_area(full_core, geo_area)
            full_core["QC"] = full_core["QC"] | qc_mask

        # Check dates (This is a repeat)
        qc_mask = time_qc.check_record(full_core, 0)
        full_core["QC"] = full_core["QC"] | qc_mask

    elif archive.core.type == "Occurrence":

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
        if geo_area is not None:
            qc_mask = location.check_record_in_area(full_core, geo_area)
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

    elif archive.core.type == "MeasurementOrFact" or archive.core.type == "ExtendedMeasurementOrFact":
        # Check measurements (this cannot be, this record type cannot ever be "Core",
        # so it is will never be called, looking for confirmation)
        qc_mask = measurements.check_record(full_core)
        if "QC" in full_core:
            full_core["QC"] = full_core["QC"] | qc_mask
        else:
            full_core["QC"] = qc_mask

    else :
        # Skip taxons and other record types
        full_core["QC"] = 0

    if with_logging and full_core["QC"] > 0:
        logger.error(f"Errors processing record {qc_flags.QCFlag.decode_mask(full_core['QC'])} "
                     f"record: : {full_core}" )

    if with_print:
        print(full_core)

    for e in archive.extensions:
        if with_print:
            print("--- extension: " + e.type)
        for extensionRecord in archive.extension_records(e):
            record_count += 1
            qc_mask = 0
            if e.type == "Occurrence":
                full_extension = extensionRecord["full"]

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

            elif e.type == "MeasurementOrFact" or e.type == "ExtendedMeasurementOrFact":
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
                logger.error(f"Errors processing record {qc_flags.QCFlag.decode_mask(full_extension['QC'])} "
                             f"record: {full_extension}")

# do I need a last lookup ?
if len(records_for_lookup) >= 0:
    # The records already contain the QC flags so we do not care about the results
    outputs = location.check_xy(records_for_lookup)
    count_lookups += 1
    # Empty the list
    print(f"Records looked up: {1000 * (count_lookups - 1) + len(records_for_lookup)}")
    records_for_lookup = []

print(f"Filename processed: {filename}")
print(f"XY lookups: {count_lookups}")
print(f"Records processed: {record_count}")
print(f"Total time: {time.time() - time_start}")

exit()
