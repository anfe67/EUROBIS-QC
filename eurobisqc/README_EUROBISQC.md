# Quality Checks for the EUROBIS database 

The Quality Checks (QC) have been developed incrementally. The key class in which they are modeled is 
QCFlag in qc_flags.py. It is an augmented Enumeration class, Every QC represents a bit, and the records 
are labeled with an integer QC value which represents a bitmask of all the QCs passed by the record. 
The class is mapped to the project definition document, which derives from the article 
https://academic.oup.com/database/article-pdf/doi/10.1093/database/bau125/16975803/bau125.pdf 
The class provides helper methods to decode a mask in both numeric form or textual form. 

## Phase 1: Developing QC procedures and processing DwCA Files 

### Approach - Steps

- Understand the QC problem: Quality masks vs Error masks, how to group them  
- Understand the file format: DwCA archives   
- Choice of library to read DwCA files : DWCAProcessor
- Analysis of the data : Different types of archives 
- Other data necessary to run some of the QCs: Areas and geography. Use EML from DwCA and pyxylookup 
- Order of the QCs and aggregation
- Multiprocessing (1 process per core updating a list of files)  
- Testing and verification 

## Phase 2: Apply QC to datasets in EUROBIS DB
- Understanding the EUROBIS database 
- Differences with DwCA and reconciliation to be able to treat records from both sources identically 
- Specific queries to extract data: Analysis of query execution plans to optimize index usage 
- Order of QCs and aggregation of results  
- Multiprocessing applied to datasets   
- Update: How to refer to unique index (no keys are defined on the main database table)
- Testing and verification 

## Phase 3: Optimization
- Analysis of performances of update query. Rebuilding of indexes, how does it affect the speed
- Analysis and review of code to improve style and verify correctness 
