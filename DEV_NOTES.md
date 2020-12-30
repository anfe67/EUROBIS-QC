# Development Notes

## Initial remarks

Each individual QC take a record (dictionary) of the correct type (or flat) and produce an integer result, either 0 or
the integer bitmask of the error code. The QC does not determine the type of record that it gets,

as in iobis-qc it is the responsibility of the caller to pass the correct record to the QCs.

This return value is then to be then OR-red to the QC mask of the record by the caller function.

The final QC value for the record is the result of the OR oof all the QC results. A perfect record has a QC value of 0.

## References

### Required fields of the OBIS Schema

**obistools project, obis-qc ** and the three references below.

- **Occurrence**: https://rs.gbif.org/core/dwc_occurrence_2020-07-15.xml
- **Event**: https://rs.gbif.org/core/dwc_event_2016_06_21.xml
- **eMoF**: https://rs.gbif.org/extension/obis/extended_measurement_or_fact.xml

In these three documents the only required field for the three record types is BasisOfRecord in Occurrence. This is in
agreement with the checks found in obis-qc. Obistools, in turn checks more fields. To discuss further.
 
--- 

## 03/12/2020 - Taxonomy

Imported taxonomy from obis-qc, determined that if AphiaID is not filled then we fail the QC 2, verified and wrote test
case. Need to verify that the taxon is lower than the family, still need to understand what does id mean exactly.
Question for 04/12/2020

Also started looking at location 1 (QC 4 and 5 for the moment easily derived from obis-qc, can do more checks at once)
To start the test part as the writing proceeds.

---

## 07/12/2020

Building a pipeline to start with a real DwCA file, it is based on dwcaprocessor, and calls the quality controls by
category. It then creates a QC field for each record with the corresponding error bitmask. For the moment, one record at
the time, calling the worms service for taxomony. The first experience looking at a full file is tat this is SLOW, must
try with batches.

### Note:

Changed taxonomy.py in obis-qc. This is to make use of the aphia-info eventually retrieved by pyworms and be able to set
bitmask 4 (bit position 2) if the taxonomy is lower than the family. This information can be retrieved by the rank field
aphia-info record. If this approach would not be accepted (pull request to obisqc) then the taxonomy would have to be
rewritten in eurobisqc.

---

## 08/12/2020

Better read the specifications, clarified a few QC questions, completed the masks, modified the required fields. The
QC_1 and QC_9 relate to missing fields, this still need to be fully understood and evaluated.

Looked at the extracton of the geographical area from the package, always using dwca-processor, as the eml.xml file is
stored in the archive.eml field. Processed with xmltodict, area extracted but tested with a single file only. The
dev_pipeline can now

---

## 09/12/2020

This day shall not be accounted for the project, I worked on it only a couple of hours. Imported the WORMS db in
SQLLite, to design a set of queries to speed up all taxonomy verifications. In practice, the new strategy for taxonomy
QC shall diverge from OBIS-QC, relying only minimally on the pyworms (only for the necessary sanity checks) that shall
be reproduced in EUROBIS-QC.

## 10/12/2020

Rewrote taxonomy checks based on DB queries on local copy of WORMS DB (file taxonomy_db.py), helper functions shall go
to package wormsdb, module db_functions. Started also two new modules, one for measurement checks and the other for
depth checks. They are not yet used in the sample pipeline.

---

## Notes / questions for Bart:

1) Is this sort of speed acceptable for taxonomy QC?
2) QC 8 needs clarifications. Is the taxon a marine taxon that does not exist in APHIA? If I know what to ask to the DB
   then we will have this one too, and with this taxonomy will be OK
3) xylookup and bathymetry data for checks 6 and 18 (to see if a point is on land and if the bathymetries are compatible
   with the event area. I have not yet looked at this aspect. # TODO, look at obis-qc

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

Questions to Bart, then looking at the whole process (following qc-component). These are the obis-qc checks by type of
record:

- Event: location and time
- Occurrence: taxonomy, location, time, fields, absence
- eMoF: mof_fields (very basic)

- Reference for the measurementTypeID field (NERC Vocabulary
  Server): http://vocab.nerc.ac.uk/collection/P01/current/SDBIOL05/

---

## 15/12/2020

Implemented feedback, improved the dev_pipeline file that has the purpose of testing, integrated file chooser, verified
with multiple files then corrected processing errors. Improved the check on the area, still some improvements possible.
Also made the point of the status of the QC Implemented lookup of field values as per discussion with Bart

VC with Bart and agreed to proceed as proposed: pyxylookup, speed, tests/coverage, then installable library.

---

## 16/12/2020

- Looking at Numba as a speed improving measure (for loops) - Not successful
- Integrated pyxylookup verifications for QC flags 6 (GEO_LAT_LON_NOT_SEA) and 19 (WRONG_DEPTH_MAP)
- Evaluated charge and speed of API, with loads of 100, 200, 500, 1000. The bigger the better, the API did not fail on
  these. Also, going for bigger sizes does not seem a good idea.
- API shall be called in batches as the call-response times seem to be the bigger time eaters. It does not make sense to
  call all at once

- Reference to download archives: http://ipt.vliz.be/eurobis/
- Bathymetry site to verify or get test points: https://maps.ngdc.noaa.gov/viewers/bathymetry/

---

## 17/12/2020

-- Verify Measurements and test cases, OK (Separated check for dynamic properties from check on eMoF, because dynamic
properties are in occurrence records). -- because of this, review the dev pipeline and start thinking about how to group
the calls to the QCs, keeping in ming that calls to pyxylookup work much better if grouped in chunks. -- Verified
nosetests from pycharm, need to verify all imports to make it clean from terminal

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
to call for the xy-lookup service in batches of that max size. The call to **pyxylookup** shall be performed when either
max size is reached (and results reaggregated) or the file is completely process Multiple QC processes can be run in
parallel on different batches of files from an "orchestrator" process (one process shall treat one file at the time but
N (10 for instance) processes can run independently. Logs shall report the status of each file processed).

---

## 21/12/2020

- Running against more files to evaluate processing times and find possible errors (at least two found, so this is a
  good process, need to test more)
- Corrections made,
- Investigating possible ways to implement parallelism

---

## 22/12/2020

- Checking more DwCA files...
- Corrected decode_mask in qc_flags, removing loggers and decided that the external callers shall do the logging
- Using loggers in dev_pipeline to understand better the data
- Tested the pipeline outside the IDE in the global environment (Installing all required packages beforehand)
- Required packages for the dev pipeline: dwca_processor, isodateparser and pyxylookup. Packages part of eurobis-qc:
  eurobisqc and lookupdb.

- **QUESTION: Is the WORMS DB that I have a full dump ( case of urn:lsid:marinespecies.org:taxname:144431 )? It is
  because some the classifications are not public. ANSWERED**
- **QUESTION: An eMoF or MoF record can never be a core record, right or wrong? Correct. ANSWERED**
- **QUESTION: Way ahead? Discussion on how to apply all the changes to the DB**
- **DONE: Review pipeline to check the records in order and in chunks when possible** Negative, not doable
- **ANSWER TO QUESTION about algorithm for verification of pyxylookup - it is like a "buffer"**

---

## 23/12/2020

- Reviewed area extraction from eml, and implemented the check with multiple areas as discussed yesterday
- **DONE: Area check needs to be an "or" between all the areas in the EML**
- Looking at area verification tests
- Looking at sdist procedures
- looking at parallelism, using multiprocessing and detecting # of CPUs
- Writing more tests for location / area QC


--- 

## 28/12/2020

- Continued looking at possible parallelisms, performances and tests. Got results, evaluated strategy, 
corrected error. 
- **DONE: Speed/Concept improvements (Used multiprocessing.Pool.apply_async)**
- **DONE: Verified that the pipeline works on all available files (currently downloaded)**

- **ONGOING: Complete tests and coverage**
- **ONGOING: Produce Installable library**
- **TODO: Get even more DwCA files** 

--- 
## 29/12/2020 

- Received email from Bart, link to DB and basic explainations / Data field mappings 
- Install MS SQL to local machine (Linux) Issues with install procedure, resolved. (Dev license is free of charge)
  - Note: For Ubuntu 20.04 needed to download and install by hand a 18.04 package called **multiarch-support_2.27-3ubuntu1.4_amd64.deb**
- Connected to Server with DBeaver, checked basic functionality
- Create DB and built Python code for basic access 
- Demonstrated querying DB and outputting Python dictionary (ready for QCs)
- Downloaded DB, investigating import 

- **ONGOING: Import DB from BAK file**
- **TODO: Read article: https://stackoverflow.com/questions/34646655/populating-row-number-on-new-column-for-table-without-primary-key**
- This is related to speed ups in SQL, Creating indexes from non indexed data on the fly  

---
## 30/12/2020 
- Import DB with command:
``` 
RESTORE DATABASE eurobis_dat FROM DISK = '/mnt/opt/VLIZ/eurobis_backup_2020_12_27_212114_3196520.bak' WITH MOVE 'eurobis_dat' TO '/var/opt/mssql/data/eurobis.mdf', MOVE 'eurobis_log' TO '/var/opt/mssql/data/eurobis.log', REPLACE
```
- (I run inside DBeaver, using it a as a sort of SSMS under Linux)
- **ONGOING: Study DB*** 
- Questions for Bart: 
1. Most of the records have a qc already set of 30, but what am I not getting, since:
```
LAT	   LON	 
44.26666   9.26666

QC = 30, meaning: "11110"

16 - GEO_LAT_LON_INVALID +  
8  - GEO_LAT_LON_MISSING +
4  - TAXONOMY_RANK_LOW +
2  - TAXONOMY_APHIAID_MISS... 

But point is in see (Mediterranean, near Genoa) and coordinates are valid, so even if the bits are slightly misaligned, these records do not compute ... 
```
2. What tables do we have to work on? How to associate data? Tables with the QC field are: 
   - dp_eurobis (25M records)
   - eurobis
   - eurobis_geo 
   - eurobis_eventcore_occrec
   - what about **eurobis_eventcore_eventrec** 
   - eurobis_harvest 
   - what about **eurobis_harvest_eventcore_eventrec**
   - what about **eurobis_harvest_measurementorfact** and all the MOF tables? 
   - eurobis_schelde
   - what about **ices, ices_eggs_occurrences and ices_eggs_emof**
  
3. How do I find the Areas to test for QC 9 ? (Saw a Bounding Box somewhere)
4. Measurement of Facts type tables do not have QC. I suppose we need to add it
5. Measurement of Facts have sometimes SEX (MeasurementTypeID=http://vocab.nerc.ac.uk/collection/P01/current/ENTSEX01/). 
Do we need to apply QC 17? I suppose so...
6. eurobis_measurementorfact_type can be used to fill the lookup database (true?)
7. what is ices (37 M records)
8. Mappings. In table QC there are queries for updating the QC fields on the DB. I believe at least one (17) is wrong.
In this respect, what is the mapping between sex (here 'M','F','H','I','U','T','B', 
   what we discussed before was different)
9. Same thing for BasisOfRecord ('O','L','S','G','P','D')