# dbworks 

## Purpose 1: Lookup DB for WORMS
### Worms

To imported the WORMS database in SQLite follow the instructions in **IMPORT_WORMS.md** file.

### lookup tables

Two type of tables can be created: If the file name ends with Lookup, the lookup elements shall be case insensitive
If the file name ends with LookUP, (like for the QC1, required fields) then the values shall be case sensitive


Thus, to create/recreate the lookup tables, the following text files (all names ending in Lookup) need to be in the **
resources** folder, with file names ending in Lookup or LookUP

- countMeasurementTypeIDLookup - Contains appropriate entries from the The NERC Vocabulary Server (NVS)
- weightMeasurementTypeIDLookup - Contains appropriate entries from the The NERC Vocabulary Server (NVS)
- sampleSizeMeasurementTypeIDLookup - Contains appropriate entries from the The NERC Vocabulary Server (NVS)
- countMeasurementTypeLookup - Contains appropriate text entries to search for in the records (like "count")
- sampleSizeMeasurementTypeLookup - Contains appropriate text entries to search for in the records (like "abundance")
- weightMeasurementTypeLookup - Contains appropriate text entries to search for in the records (like "wet weight
  biomass")
- sexMeasurementTypeIDLookup 
- sexMeasurementTypeIDLookup
- sexValuesLookup - The possible valid values  

The tables above are used in QCs 14, 15, 16 and 17 
 
- requiredFieldsLookUP - Contains the required fields for QC1 
- recommendedFieldsLookUP - Contains the recommended fields for QC1 
- basisOfRecordValuesLookup - Contains the values admitted in the basisOfRecord field for QC 10 to pass

These tables can be refreshed by running from a python console: 

```python
import os 
os.chdir("<the directory of dbworks>") 
from dbworks.create_lookup_tables import import_files
import_files()
```

## Purpose 2: MSSQL Connectivity to perform data update 

### MS SQL Server connectivity 

This package shall be used to connect to the MS SQL server containing the EUROBIS data, query the DB to obtain datasets 
and after having run the QCs, push the computed bitmask back to the database records (update the qc field in table eurobis). 

The package contains connectivity and helper functions. The database connection parameters are in a config.ini file 
under resources.

### Test 

Testing is limited to demonstrating connectivity, querying a table and outputting all records in the form of a list of 
Python dictionaries.

## Parameters: 
The parameters for both DB connections are stored in the config.ini file under resources. sections are SQLITEDB for the lookup DB
and SQLSERVERDB for MSSQL. For MSSQL there is the option to select between two pyhton driver libraries. 
Installation instructions for the ODBC drivers for the ubuntu os, that are 
necessary to use the pyodbc module can be found here: 
https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver15

Installation instruction to install the pymssql pre-requisite package FreeTDS on ubuntu can be found here: 
https://pymssql.readthedocs.io/en/dev/intro.html

This is an example of a configuration file for this project, where all variables have been enclosed in "<>": 
```
[SQLITEDB]
databaseFile = database/EUROBIS_QC_LOOKUP_DB.db

[SQLSERVERDB]
driver        = ODBC Driver 17 for SQL Server
drivermodule  = pymssql
# drivermodule can be pymysql or pyodbc (needs to be specified).
server        = <MyServerIP>
port          = <MyServerPort>
database      = eurobis_dat
username      = <MyUser>
password      = <MyPassword>

```
