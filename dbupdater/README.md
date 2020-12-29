# DBUPDATER - MS SQL Server connectivity 

## Purpose

The package shall be used to connect to the MS SQL server containing the EUROBIS data, query the DB to obtain datasets 
and after having run the QCs, push the bitmask back to the database. 

The package contains connectivity and helper functions. The database connection parameters are in a config.ini file 
under resources. 

## Test 

Testin is limited to demonstrating connectivity, querying a table and outputting all records in the form of a list of 
Python dictionaries.
