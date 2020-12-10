# Development Notes 

## Initial remarks 
 
Each individual QC take a record (dictionary) of the correct type (or flat) and produce an integer result,
either 0 or the integer bitmask of the error code. The QC does not determine the type of record that it gets, 

as in iobis-qc it is the responsibility of the caller to pass the correct record to the QCs. 

This return value is then to be then OR-red to the QC mask of the record by the caller function.

The final QC value for the record is the result of the OR oof all the QC results. A perfect record 
has a QC value of 0. 

## References 
### Required fields of the OBIS Schema 

**obistools project, obis-qc ** and the three references below. 

- **Occurrence**: https://rs.gbif.org/core/dwc_occurrence_2020-07-15.xml   
- **Event**: https://rs.gbif.org/core/dwc_event_2016_06_21.xml
- **eMoF**: https://rs.gbif.org/extension/obis/extended_measurement_or_fact.xml
 
 
In these three documents the only required field for the three record types is BasisOfRecord in 
Occurrence. This is in agreement with the checks found in obis-qc. 
Obistools, in turn checks more fields.  To discuss further.
 
 
 ## 03/12/2020 - Taxonomy 
 
 Imported taxonomy from obis-qc, determined that if AphiaID is not filled then we fail the QC 2, verified
 and wrote test case. Need to verify that the taxon is lower than the family, still need to understand
 what does id mean exactly.  Question for 04/12/2020
 
 Also started looking at location 1 (QC 4 and 5 for the moment easily derived from obis-qc, can do more checks at once) 
 To start the test part as the writing proceeds. 
 
 ## 07/12/2020

Building a pipeline to start with a real DwCA file, it is based on dwcaprocessor, and calls the 
quality controls by category. It then creates a QC field for each record with the corresponding 
error bitmask. For the moment, one record at the time, calling the worms service for taxomony. 
The first experience looking at a full file is tat this is SLOW, must try with batches.

## Note: 

Changed taxonomy.py in obis-qc. This is to make use of the aphia-info eventually retrieved by 
pyworms and be able to set bitmask 4 (bit position 2) if the taxonomy is lower than the family. 
This information can be retrieved by the rank field aphia-info record. If this approach would 
not be accepted (pull request to obisqc) then the taxonomy would have to be rewritten in eurobisqc. 



# 08/12/2020 
Better read the specifications, clarified a few QC questions, completed the masks, modified the 
required fields. The QC_1 and QC_9 relate to missing fields, this still need to be fully 
understood and evaluated. 

Looked at the extracton of the geographical area from the package, always using dwca-processor, 
as the eml.xml file is stored in the archive.eml field. Processed with xmltodict, area extracted 
but tested with a single file only. The dev_pipeline can now 

# 09/12/2020 
This day shall not be accounted for the project, I worked on it only a couple of hours. Imported 
the WORMS db in SQLLite, to design a set of queries to speed up all taxonomy verifications. 
In practice, the new strategy for taxonomy QC shall diverge from OBIS-QC, relying only 
minimally on the pyworms (only for the necessary sanity checks) that shall be reproduced in EUROBIS-QC.  

# 10/12/2020 
Rewrote taxonomy checks based on DB queries on local copy of WORMS DB (file taxonomy_db.py), 
helper functions shall go to package wormsdb, module db_functions. 
Started also two new modules, one for measurement checks and the other for depth 
checks. They are not yet used in the sample pipeline. 

## Notes / questions for Bart: 
1) Is this sort of speed acceptable for taxonomy QC?
2) QC 8 needs clarifications. Is the taxon a marine taxon that does not exist in APHIA? If I know what 
to ask to the DB then we will have this one too, and with this taxonomy will be OK 
3) xylookup and bathymetry data for checks 6 and 18 (to see if a point is on land 
   and if the bathymetries are compatible with the event area. 
   I have not yet looked at this aspect. # TODO, look at obis-qc  
   
4) In what field should I dig to find Observed weight (QC # 15) - emailed to Bart 


### TODO: Clean the code, write test cases and write more tests. Also must think at way to improve the 
project structure and rationalise imports (create proper requirement.txt).


