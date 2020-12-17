import sys
import time
from dwcaprocessor import DwCAProcessor
from eurobisqc import location
from eurobisqc import required_fields
from eurobisqc import old_taxonomy
from eurobisqc import taxonomy
from eurobisqc import time_qc
from eurobisqc import measurements

from eurobisqc.util import extract_area
from lookupdb import db_functions
import file_chooser

# Adding a simple file chooser...
filename = file_chooser.get_archive_chooser()

if filename is None:
    exit(0)

archive = DwCAProcessor(filename)

geo_area = extract_area.find_area(archive.eml)

# All net processing
time_start = time.time()

# Taxonomy needs to call the lookup-db service
check_taxonomy = False
check_taxonomy_db = True

record_count = 0
with_print = False

for coreRecord in archive.core_records():
    record_count += 1
    if with_print:
        print("+++ core: " + archive.core.type)
    # Attempt check for lat/lon in full record
    full_core = coreRecord["full"]

    # Core Record
    # Check location

    qc = location.check_basic_record(full_core)
    if "QC" in full_core:
        full_core["QC"] = full_core["QC"] | qc
    else:
        full_core["QC"] = qc

    # There are archives without Event records...
    if archive.core.type == "Event":
        # Check location in area
        if geo_area is not None:
            qc = location.check_record_in_area(full_core, geo_area)
            full_core["QC"] = full_core["QC"] | qc

        # Check dates (This is a repeat)
        qc = time_qc.check_record(full_core, 0)
        full_core["QC"] = full_core["QC"] | qc

    elif archive.core.type == "Occurrence":

        # QC 9 (basis of records)
        qc = required_fields.check_record_obis_format(full_core)
        if "QC" in full_core:
            full_core["QC"] = full_core["QC"] | qc
        else:
            full_core["QC"] = qc

        # QC 1 (required fields)
        qc = required_fields.check_record_required(full_core)
        full_core["QC"] = full_core["QC"] | qc

        # Check location
        qc = location.check_basic_record(full_core)
        full_core["QC"] = full_core["QC"] | qc

        # Check taxonomy (This shall be removed)
        if check_taxonomy:
            qc = old_taxonomy.check(full_core)
            full_core["QC"] = full_core["QC"] | qc

        if check_taxonomy_db:
            qc = taxonomy.check_record(full_core)
            full_core["QC"] = full_core["QC"] | qc

        # Check dates (This is a repeat)
        qc = time_qc.check_record(full_core, 0)
        full_core["QC"] = full_core["QC"] | qc

    elif archive.core.type == "ExtendedMeasurementOrFact":
        # Check measurements
        qc = measurements.check_record(full_core)
        if "QC" in full_core:
            full_core["QC"] = full_core["QC"] | qc
        else:
            full_core["QC"] = qc
    if with_print:
        print(full_core)

    for e in archive.extensions:
        record_count += 1
        if with_print:
            print("--- extension: " + e.type)
        for extensionRecord in archive.extension_records(e):
            if e.type == "Occurrence":
                full_extension = extensionRecord["full"]

                # QC 9 (basis of records)
                qc = required_fields.check_record_obis_format(full_extension)
                if "QC" in full_extension:
                    full_extension["QC"] = full_extension["QC"] | qc
                else:
                    full_extension["QC"] = qc

                # QC 1 (required fields)
                qc = required_fields.check_record_required(full_extension)
                full_extension["QC"] = full_extension["QC"] | qc

                # Check location
                qc = location.check_basic_record(full_extension)
                full_extension["QC"] = full_extension["QC"] | qc

                # Check taxonomy (This shall be removed)
                if check_taxonomy:
                    qc = old_taxonomy.check(full_extension)
                    full_extension["QC"] = full_extension["QC"] | qc

                if check_taxonomy_db:
                    qc = taxonomy.check_record(full_extension)
                    full_extension["QC"] = full_extension["QC"] | qc

                # Check dates (This is a repeat)
                qc = time_qc.check_record(full_extension, 0)
                full_extension["QC"] = full_extension["QC"] | qc
                if with_print:
                    print(full_extension)

            if e.type == "ExtendedMeasurementOrFact":
                full_extension = extensionRecord["full"]
                # Check measurements
                qc = measurements.check_record(full_extension)
                if "QC" in full_extension:
                    full_extension["QC"] = full_extension["QC"] | qc
                else:
                    full_extension["QC"] = qc
                if with_print:
                    print(full_extension)

print(f"Record count: {record_count}")
print(f"Total time: {time.time() - time_start}")

sys.exit()
