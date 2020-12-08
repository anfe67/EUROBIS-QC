import sys
import os

from eurobisqc import location
from eurobisqc import required_fields
from eurobisqc import taxonomy
from eurobisqc.util import extract_area

from dwcaprocessor import DwCAProcessor

filename = "data/dwca-meso_meiofauna_knokke_1969-v1.7.zip"
archive = DwCAProcessor(filename)
geo_area = extract_area.find_area(archive.eml)

print(archive)

# Taxonomy needs to call the WORMS service
check_taxonomy = False

############### Explore structure

for coreRecord in archive.core_records():
    print("+++ core: " + archive.core.type)
    # Attempt check for lat/lon in full record
    full_core = coreRecord["full"]

    # Core Record
    qc = location.check_record(full_core)
    if "QC" in full_core:
        full_core["QC"] = full_core["QC"] | qc
    else:
        full_core["QC"] = qc

    qc = location.check_record_in_area(full_core, geo_area)
    full_core["QC"] = full_core["QC"] | qc


    print(full_core)

    for e in archive.extensions:
        print("--- extension: " + e.type)
        for extensionRecord in archive.extension_records(e):
            if e.type == "Occurrence":
                full_extension = extensionRecord["full"]

                # Check required fields
                qc = required_fields.check_record(full_extension)
                if "QC" in full_extension:
                    full_extension["QC"] = full_extension["QC"] | qc
                else:
                    full_extension["QC"] = qc

                # Check location
                qc = location.check_record(full_extension)
                full_extension["QC"] = full_extension["QC"] | qc

                # Check taxonomy
                if check_taxonomy:
                    qc = taxonomy.check(full_extension)
                    full_extension["QC"] = full_extension["QC"] | qc

                print(full_extension)

            else:  # Other record type, just print the full version of the record
                print(extensionRecord["full"])

sys.exit()
