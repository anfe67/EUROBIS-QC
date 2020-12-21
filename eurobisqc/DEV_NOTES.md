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
 
--- 

## 03/12/2020 - Taxonomy 
 
 Imported taxonomy from obis-qc, determined that if AphiaID is not filled then we fail the QC 2, verified
 and wrote test case. Need to verify that the taxon is lower than the family, still need to understand
 what does id mean exactly.  Question for 04/12/2020
 
 Also started looking at location 1 (QC 4 and 5 for the moment easily derived from obis-qc, can do more checks at once) 
 To start the test part as the writing proceeds. 

---
 
## 07/12/2020

Building a pipeline to start with a real DwCA file, it is based on dwcaprocessor, and calls the 
quality controls by category. It then creates a QC field for each record with the corresponding 
error bitmask. For the moment, one record at the time, calling the worms service for taxomony. 
The first experience looking at a full file is tat this is SLOW, must try with batches.

### Note: 

Changed taxonomy.py in obis-qc. This is to make use of the aphia-info eventually retrieved by 
pyworms and be able to set bitmask 4 (bit position 2) if the taxonomy is lower than the family. 
This information can be retrieved by the rank field aphia-info record. If this approach would 
not be accepted (pull request to obisqc) then the taxonomy would have to be rewritten in eurobisqc. 

---

## 08/12/2020 
Better read the specifications, clarified a few QC questions, completed the masks, modified the 
required fields. The QC_1 and QC_9 relate to missing fields, this still need to be fully 
understood and evaluated. 

Looked at the extracton of the geographical area from the package, always using dwca-processor, 
as the eml.xml file is stored in the archive.eml field. Processed with xmltodict, area extracted 
but tested with a single file only. The dev_pipeline can now 

---

## 09/12/2020 
This day shall not be accounted for the project, I worked on it only a couple of hours. Imported 
the WORMS db in SQLLite, to design a set of queries to speed up all taxonomy verifications. 
In practice, the new strategy for taxonomy QC shall diverge from OBIS-QC, relying only 
minimally on the pyworms (only for the necessary sanity checks) that shall be reproduced in EUROBIS-QC.  

## 10/12/2020 
Rewrote taxonomy checks based on DB queries on local copy of WORMS DB (file taxonomy_db.py), 
helper functions shall go to package wormsdb, module db_functions. 
Started also two new modules, one for measurement checks and the other for depth 
checks. They are not yet used in the sample pipeline. 

---

## Notes / questions for Bart: 
1) Is this sort of speed acceptable for taxonomy QC?
2) QC 8 needs clarifications. Is the taxon a marine taxon that does not exist in APHIA? If I know what 
to ask to the DB then we will have this one too, and with this taxonomy will be OK 
3) xylookup and bathymetry data for checks 6 and 18 (to see if a point is on land 
   and if the bathymetries are compatible with the event area. 
   I have not yet looked at this aspect. # TODO, look at obis-qc  
   
4) In what field should I dig to find Observed weight (QC # 15) - emailed to Bart

---

## 11/12/2020 
Starting with a code cleanup, then reading Bart response to QC 15 above. References: 

- **measurementType** Wet weight biomass
- **MeasurementtypeID** in  http://vocab.nerc.ac.uk/collection/S06/current/S0600088/
- **Refs:** http://vocab.nerc.ac.uk/collection/P01/current/SDBIOL05, http://vocab.nerc.ac.uk/

Other things :
- Guessed that a similar approach can be taken with the observed count, and sample size.
- Emailed Bart with questions 
- refactored db_functions. 

---
  
## 14/12/2020 
Questions to Bart, then looking at the whole process (following qc-component). 
These are the obis-qc checks by type of record:
- Event: location and time 
- Occurrence: taxonomy, location, time, fields, absence 
- eMoF: mof_fields (very basic) 

- Reference for the measurementTypeID field (NERC Vocabulary Server): http://vocab.nerc.ac.uk/collection/P01/current/SDBIOL05/ 

---

## 15/12/2020 
Implemented feedback, improved the dev_pipeline file that has the purpose of testing, integrated file chooser, 
verified with multiple files then corrected processing errors. Improved the check on the area, 
still some improvements possible. Also made the point of the status of the QC
Implemented lookup of field values as per discussion with Bart

VC with Bart and agreed to proceed as proposed: pyxylookup, speed, tests/coverage, then installable library. 

---

## 16/12/2020
- Looking at Numba as a speed improving measure (for loops) - Not successful 
- Integrated pyxylookup verifications for QC flags 6 (GEO_LAT_LON_NOT_SEA) and 19 (WRONG_DEPTH_MAP)
- Evaluated charge and speed of API, with loads of 100, 200, 500, 1000. The bigger the better, the 
  API did not fail on these. Also, going for bigger sizes does not seem a good idea.   
- API shall be called in batches as the call-response times seem to be the bigger time eaters. 
  It does not make sense to call all at once  
  
- Reference to download archives: http://ipt.vliz.be/eurobis/
- Bathymetry site to verify or get test points: https://maps.ngdc.noaa.gov/viewers/bathymetry/

---

## 17/12/2020 
-- Verify Measurements and test cases, OK (Separated check for dynamic properties from check on eMoF, because 
dynamic properties are in occurrence records). 
-- because of this, review the dev pipeline and start thinking about how to group the calls to the QCs, keeping in 
ming that calls to pyxylookup work much better if grouped in chunks. 
-- Verified nosetests from pycharm, need to verify all imports to make it clean from terminal

---

# 18/12/2020
- Resuming test/test coverage/imports review. Decent coverage and nosetest achieved. 
- Establishing precedence of QCs to optimize pipeline. 
  1) Required Fields (1, 10)
  2) Basic Location checks (4, 5, 9, 18) 
  3) Taxonomy Checks (2, 3)
  4) Date Time (7, 11, 12, 13)
  5) Measurements (14, 15, 16, 17)
  6) XY Lookup after all the processing above (6, 19)  

- Applied the above to 

While running points 1-5 will the **suitable** records shall be aggregated in lists with a max size to be established, 
to call for the xy-lookup service in batches of that max size. The call to **pyxylookup** shall be performed when 
either max size is reached (and results reaggregated) or the file is completely process 
Multiple QC processes can be run in parallel on different batches of files from an "orchestrator" process (one process 
shall treat one file at the time but N (10 for instance) processes can run independently. Logs shall report the status
of each file processed).

## 21/12/2020 

- Running against more files to evaluate processing times and find possible errors (at least two found, 
  so this is a good process, need to test more) 
- Corrections made, 
- Investigating possible ways to implement parallelism

---

- **QUESTION: An eMoF record can never be a core record, right or wrong?** 
- **Review pipeline to check the records in order and in chunks when possible** done, it seems not doable 
- **NOTE: Measurements check should be OK, DB was broken due to lambda - FIXED** 
- **TODO: Speed/Concept improvements (possible parallelism?)**
- **ONGOING: Complete tests and coverage**
- **ONGOING: Produce Installable library**

