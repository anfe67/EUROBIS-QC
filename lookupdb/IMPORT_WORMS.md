# Importing WORMS to SQLLITE 

## Import tools tested  

* Libreoffice (cuts the file 4/5 into the reading, so the import is **not satisfactory**)
* sqllitebrowser (worked for the smaller tables, **not for taxon**) **not satisfactory**  
* csvkit, which worked **fully** with the command:  
```  
  csvsql --tabs --quoting=3 --db sqlite:///database/EUROBIS_QC_LOOKUP_DB.db --no-constraints --insert taxon.txt
```
The entire table was imported, resulting in the expected number of records. 

- The same type of command was repeated for the other two tables in the WORMS DwCA file provided 
- The file name (database/EUROBIS_QC_LOOKUP_DB.db=, in order to be used a lookup DB, needs to be specified in ./resources/config.ini    

**NOTE:**
SQLite is a file based DB, which is efficient for small databases that can be stored in memory. 
This is the case for the WORMS db. SQLite is supported natively in Python by means of the **sqlite3** library. 