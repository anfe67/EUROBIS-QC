# lookupdb (also contains worms tables)

## Worms
To imported the WORMS database in SQLite follow the instructions in **IMPORT_WORMS.md** file. 

## lookup tables
To create/recreate the lookup tables, the following text files (all names ending in Lookup) need to be in resources: 

- countMeasurementTypeIDLookup      - Contains appropriate entries from the The NERC Vocabulary Server (NVS)
- weightMeasurementTypeIDLookup     - Contains appropriate entries from the The NERC Vocabulary Server (NVS)
- sampleSizeMeasurementTypeIDLookup - Contains appropriate entries from the The NERC Vocabulary Server (NVS)
- countMeasurementTypeLookup        - Contains appropriate text entries to search for in the records (like "count")
- sampleSizeMeasurementTypeLookup   - Contains appropriate text entries to search for in the records (like "abundance")
- weightMeasurementTypeLookup       - Contains appropriate text entries to search for in the records (like "wet weight biomass")

These tables shall be refreshed by running, from a python console: 
```python
import os 
os.chdir("<the directory of lookupdb>") 
from create_lookup_tables import import_files
import_files()
```