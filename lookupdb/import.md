# Importing WORMS to SQLLITE 

## Import tools tested 

* Libreoffice (cuts the file 4/5 into the reading, so the import is not satisfactory)
* sqllitebrowser (worked for the smaller tables, not for taxon) 
* csvkit, worked with the command:  
  
  * **csvsql --tabs --quoting=3 --db sqlite:///WORMS.db --no-constraints --insert taxon.txt**
    
* The same type of command was repeated for the other two tables in the WORMS DwCA

The latter imported the entire table, resulting in the expected number of records