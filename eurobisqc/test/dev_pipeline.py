import sys

from dwcaprocessor import DwCAProcessor
from eurobisqc import location
from eurobisqc import required_fields
from eurobisqc import old_taxonomy
from eurobisqc import taxonomy_db
from eurobisqc import time_qc
from eurobisqc import measurements

from eurobisqc.util import extract_area
from lookupdb import db_functions

filename = "data/dwca-meso_meiofauna_knokke_1969-v1.7.zip"
archive = DwCAProcessor(filename)
geo_area = extract_area.find_area(archive.eml)

print(archive)

# Taxonomy needs to call the worms-db service
check_taxonomy = False
check_taxonomy_db = True


for coreRecord in archive.core_records():
    print("+++ core: " + archive.core.type)
    # Attempt check for lat/lon in full record
    full_core = coreRecord["full"]

    # Core Record
    # Check location
    qc = location.check_record(full_core)
    if "QC" in full_core:
        full_core["QC"] = full_core["QC"] | qc
    else:
        full_core["QC"] = qc

    # Check location in area
    qc = location.check_record_in_area(full_core, geo_area)
    full_core["QC"] = full_core["QC"] | qc

    # Check dates (This is a repeat)
    qc = time_qc.check_record(full_core, 0)
    full_core["QC"] = full_core["QC"] | qc

    print(full_core)

    for e in archive.extensions:
        print("--- extension: " + e.type)
        for extensionRecord in archive.extension_records(e):
            if e.type == "Occurrence":
                full_extension = extensionRecord["full"]

                # Check required fields
                qc = required_fields.check_record_obis_format(full_extension)
                if "QC" in full_extension:
                    full_extension["QC"] = full_extension["QC"] | qc
                else:
                    full_extension["QC"] = qc

                # Check location
                qc = location.check_record(full_extension)
                full_extension["QC"] = full_extension["QC"] | qc

                # Check taxonomy (This shall be removed)
                if check_taxonomy:
                    qc = old_taxonomy.check(full_extension)
                    full_extension["QC"] = full_extension["QC"] | qc

                if check_taxonomy_db:
                    if db_functions.conn is None:
                        db_functions.open_db()
                    qc = taxonomy_db.check_record(full_extension)
                    full_extension["QC"] = full_extension["QC"] | qc

                # Check dates (This is a repeat)
                qc = time_qc.check_record(full_extension, 0)
                full_extension["QC"] = full_extension["QC"] | qc

                print(full_extension)

            if e.type == "ExtendedMeasurementOrFact":
                full_extension = extensionRecord["full"]
                # Check measurements
                qc = measurements.check_record(full_extension)
                if "QC" in full_extension:
                    full_extension["QC"] = full_extension["QC"] | qc
                else:
                    full_extension["QC"] = qc
                print(full_extension)

if db_functions.conn is not None:
    db_functions.close_db()

sys.exit()
