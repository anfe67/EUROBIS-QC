# EUROBIS-QC

Implementation of a seiries of Quality Control checks on EUROBIS DwC-A records (dictionaries). 

Based on: 

obistools: https://github.com/iobis/obistools
obis-qc: https://github.com/iobis/obis-qc
dwca-processor: https://github.com/iobis/dwca-processor

And other libraries, almost all from Pieter Provoost. 

Each individual QC take a record (dictionary) of the correct type (or flat) and produce an integer result,
either 0 or the integer bitmask of the error code. The QC does not determine the type of record that it gets, 

as in iobis-qc it is the responsibility of the caller to pass the correct record to the QCs. 

This return value is then to be then OR-red to the QC mask of the record by the caller function.

The final QC value for the record is the result of the OR oof all the QC results. A perfect record 
has a QC value of 0. 

## Email exchange with VLIZ 03/12/2020 

The requirements for the fields are to be found in the following references
 
- **Occurrence**: https://rs.gbif.org/core/dwc_occurrence_2020-07-15.xml   
- **Event**: https://rs.gbif.org/core/dwc_event_2016_06_21.xml
- **eMoF**: https://rs.gbif.org/core/dwc_event_2016_06_21.xml
 
In these three documents the only required field for the three record types is BasisOfRecord in 
Occurrence. This contraddicts obistools, and it is in agreement with obis-qc. To discuss further. 
 
 ## 03/12/2020 - Taxonomy 
 
 Imported taxonomy from obis-qc, determined that if AphiaID is not filled then we fail the QC 2, verified
 and wrote test case. Need to verify that the taxon is lower than the family, still need to understand
 what does id mean exactly.  Question for 04/12/2020
 
 Looking at location 1 (QC 4 and 5 for the moment easily derived from obis-qc, can do more checks at once) 
 To start the test part as the writing proceeds. 
 
 

