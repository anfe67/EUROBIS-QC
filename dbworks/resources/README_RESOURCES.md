# Database Lookup Tables

The text files in this directory are used to feed database tables that are used during the QC for looking up values.
Each of the files shall originate a DB table, named after the file (except the lookup) with a single field called value.
Empty Lines or lines starting with a # shall not be processed.

For instance the file measurementTypeWeightLookup, containing 1 line "weight", shall originate the table
measurementTypeWeight, containing a single column "Value", with one single record "weight".

tables shall be destroyed and re-created by the commands, run from a python shell:

```python
import os 
os.chdir("<the directory of dbworks>") 
from dbworks.create_lookup_tables import import_files
import_files()
```
This shall not affect the WORMS tables which are stored in the same DB.  

## Important:

- File names are fixed, they are:
  
    - countMeasurementTypeIDLookup
    - countMeasurementTypeIDLookup
    - sampleSizeMeasurementTypeIDLookup
    - sampleSizeMeasurementTypeLookup
    - weightMeasurementTypeIDLookup
    - weightMeasurementTypeLookup
    - deviceMeasurementTypeIDLookup
    - deviceMeasurementTypeLookup
    - sexMeasurementTypeIDLookup
    - sexMeasurementTypeLookup
    - sexValuesLookup
    - basisOfRecordValuesLookup
    - requiredFieldsLookUP **NOTE EXTENSION DIFFERENCE** 
    - recommendedFieldsLookUP **NOTE EXTENSION DIFFERENCE**

- The database tables have the same name without the "Lookup" suffix, or when case sensitivity is important, the 
  suffix becomes LookUP

To reload the DB tables, call **create_lookup_tables.import_files()**

