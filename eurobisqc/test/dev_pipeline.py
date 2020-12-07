import sys
import os

from eurobisqc import location
from eurobisqc import required_fields
from eurobisqc import taxonomy

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from dwcaprocessor import DwCAProcessor

filename = "data/dwca-meso_meiofauna_knokke_1969-v1.7.zip"
archive = DwCAProcessor(filename)
print(archive)

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
                qc = taxonomy.check(full_extension)

                full_extension["QC"] = full_extension["QC"] | qc

                print(full_extension)

            else:  # Other record type, just print the full version of the record
                print(extensionRecord["full"])

sys.exit()
