# Database Lookup Tables

The text files in this directory are used to feed database tables that are used during the QC for looking up values. 
Each of the files shall originate a DB table, named after the file (except the lookup) with a single field called value.
Empty Lines or lines starting with a # shall not be processed. 

For instance the file measurementTypeWeightLookup, containing 1 line "weight", shall originate the table 
measurementTypeWeight, containing a single column "Value", with one single record "weight". 

tables shall be destroyed and re-created by launching the command. 

## Important: 
- File names are fixed, they are:
    - countMeasurementTypeIDLookup
    - countMeasurementTypeIDLookup
    - sampleSizeMeasurementTypeIDLookup
    - sampleSizeMeasurementTypeLookup
    - weightMeasurementTypeIDLookup
    - weightMeasurementTypeLookup
    
- The database tables have the same name without the "Lookup" suffix 

To reload the DB tables, call **create_lookup_tables.import_files()**