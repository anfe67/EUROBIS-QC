# Importing WORMS to SQLLITE 

## Import tools tested  

* Libreoffice (cuts the file 4/5 into the reading, so the import is **not satisfactory**)
* sqllitebrowser (worked for the smaller tables, **not for taxon**) **not satisfactory**  
* csvkit, which worked **fully** with the command:  
```  
  * **csvsql --tabs --quoting=3 --db sqlite:///Wdatabase/EUROBIS_QC_LOOKUP_DB.db --no-constraints --insert taxon.txt**
```

This file name needs to be the same as specified in ./resources/config.ini    

* The same type of command was repeated for the other two tables in the WORMS DwCA file provided

The entire table was imported, resulting in the expected number of records. 
