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
- **eMoF**: https://rs.gbif.org/core/dwc_event_2016_06_21.xml
 
 
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


### TODO: Clean the code, write test cases and write more tests. Also must think at way to optimize.

# 08/12/2020 
Better read the specifications, clarified a few QC questions, completed the masks, modified the 
required fields. The QC_1 and QC_9 relate to missing fields, this still need to be fully 
understood and evaluated. 

Looked at the extracton of the geographical area from the package, always using dwca-processor, 
as the eml.xml file is stored in the archive.eml field. Processed with xmltodict, area extracted 
but tested with a single file only. The dev_pipeline can now 





