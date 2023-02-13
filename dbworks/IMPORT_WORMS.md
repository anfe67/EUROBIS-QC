# Importing WORMS to SQLLITE

## Choice of import tool

To quickly import the WORMS database dump provided in CSV format (field separator is TAB), 
the following tools have been evaluated. 
All of them import successfully the smaller tables, while the taxon table 
leads to make a choice, because not all tools can deal with it: 

* Libreoffice (cuts the file 4/5 into the reading, so the import is **not satisfactory**)
* sqllitebrowser (worked for the smaller tables, **not for taxon**) **not satisfactory**
* csvkit, which worked **fully** with the command:

```  
  csvsql --tabs --quoting=3 --db sqlite:///database/EUROBIS_QC_LOOKUP_DB.db --no-constraints --insert taxon.txt
```

The entire table was imported, resulting in the expected number of records.

- The same type of command was repeated for the other two tables in the WORMS DwCA file provided
- The file name (database/EUROBIS_QC_LOOKUP_DB.db=, in order to be used a lookup DB, needs to be specified in
  ./resources/config.ini

## To improve the performance :
SQLite is a file based DB, which is efficient for small databases that can be stored in memory. This is the case for the
WORMS db. SQLite is supported natively in Python by means of the **sqlite3** library. 

To improve efficiency of the lookup queries, only the necessary fields should be extracted from the DB. Furthermore, as the 
fields sought are scientificNameID and scientificName, the following indexes should be created: 

```
CREATE INDEX "taxon_scientific_name" ON "taxon" (
	"scientificName"	ASC
)

CREATE INDEX "taxon_scientific_name_id" ON "taxon" (
	"scientificNameID"	ASC
)
```

## Extra tables to add :
```
CREATE TABLE abundanceMeasurementTypeID ('Value' TEXT);
CREATE TABLE abundanceMeasurementType ('Value' TEXT);
CREATE TABLE abioticMeasurementTypeID ('Value' TEXT);
CREATE TABLE abioticMeasurementType ('Value' TEXT);
```

**NOTE:** This is extremely important for performance, as it helps improve lookup 
times on taxon (and therefore efficiency of the taxonomy QC) by a factor of 1000. 

