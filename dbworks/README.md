# dbworks 

## Purpose 1: Lookup DB
### Worms

To imported the WORMS database in SQLite follow the instructions in **IMPORT_WORMS.md** file.

### lookup tables

To create/recreate the lookup tables, the following text files (all names ending in Lookup) need to be in the **
resources** folder:

- countMeasurementTypeIDLookup - Contains appropriate entries from the The NERC Vocabulary Server (NVS)
- weightMeasurementTypeIDLookup - Contains appropriate entries from the The NERC Vocabulary Server (NVS)
- sampleSizeMeasurementTypeIDLookup - Contains appropriate entries from the The NERC Vocabulary Server (NVS)
- countMeasurementTypeLookup - Contains appropriate text entries to search for in the records (like "count")
- sampleSizeMeasurementTypeLookup - Contains appropriate text entries to search for in the records (like "abundance")
- weightMeasurementTypeLookup - Contains appropriate text entries to search for in the records (like "wet weight
  biomass")

These tables shall be refreshed by running, from a python console:

```python
import os 
os.chdir("<the directory of dbworks>") 
from create_lookup_tables import import_files
import_files()
```

## Purpose 2: MSSQL Connectivity to perform data update 

## MS SQL Server connectivity 

The package shall be used to connect to the MS SQL server containing the EUROBIS data, query the DB to obtain datasets 
and after having run the QCs, push the bitmask back to the database. 

The package contains connectivity and helper functions. The database connection parameters are in a config.ini file 
under resources. 

## Test 

Testin is limited to demonstrating connectivity, querying a table and outputting all records in the form of a list of 
Python dictionaries.



