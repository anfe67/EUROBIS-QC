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
   with the event area. I have not yet looked at this aspect. # DONE, look at obis-qc

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
- **DONE: Get even more DwCA files** 

--- 

## 29/12/2020 

- Received email from Bart, link to DB and basic explainations / Data field mappings 
- Install MS SQL to local machine (Linux) Issues with install procedure, resolved. (Dev license is free of charge)
  - Note: For Ubuntu 20.04 needed to download and install by hand a 18.04 package called **multiarch-support_2.27-3ubuntu1.4_amd64.deb**
- Connected to Server with DBeaver, checked basic functionality
- Create DB and built Python code for basic access 
- Demonstrated querying DB and outputting Python dictionary (ready for QCs)
- Downloaded DB, investigating import 

- **DONE: Import DB from BAK file**
- **DONE: Read article: https://stackoverflow.com/questions/34646655/populating-row-number-on-new-column-for-table-without-primary-key**
- This is related to speed ups in SQL, Creating indexes from non indexed data on the fly  

---

## 30/12/2020 
- Import DB with command:
``` 
RESTORE DATABASE eurobis_dat FROM DISK = '/mnt/opt/VLIZ/eurobis_backup_2020_12_27_212114_3196520.bak' WITH MOVE 'eurobis_dat' TO '/var/opt/mssql/data/eurobis.mdf', MOVE 'eurobis_log' TO '/var/opt/mssql/data/eurobis.log', REPLACE
```
- (I run inside DBeaver, using it a as a sort of SSMS under Linux)
- **DONE: Study DB*** 
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
In this respect, what is the mapping between sex (here 'M','F','H','I','U','T','B')
   what we discussed before was different , see also this result, obtained from measurement of facts)
```
FROM EUROBIS_MEASUREMENTORFACT

"measurementValue","count"
"1 Male & 1 Female",                1
"1 male & 2 female",                1
"1 male, 1 female",                 6
"1 male, 3 female",                 1
"10Male 7Female",                   1
"11Male 5Female",                   1
"11Male 9Female",                   1
"12Male 14Female",                  1
"12Male 9Female",                   1
"15Male 13Female",                  1
"19Male 17Female",                  1
"1Female",                          1
"1Male 1Female",                    1
"1Male 2Female",                    4
"1Male 3Female",                    2
"1Male 4Female",                    1
"1Male, 1Female",                   4
"2 female",                         1
"2 male & 1 female",                1
"2 male & 3 female",                1
"2 males",                          1
"24Male 18Female",                  1
"2Male 1Female",                    2
"2Male 2Female",                    1
"2MaleMale, 3FemaleFemale",         1
"3 male, 7 female",                 1
"3 males",                          1
"3Male",                            1
"3Male 10Female",                   1
"3Male 4Female",                    1
"3Male 7Female",                    1
"3Male 8Female",                    1
"3Male, 3Female",                   1
"4 male, 2 female",                 1
"4Male 6Female",                    1
"5 male, 6 female",                 1
"5 males, 3 females",               2
"52Male 46Female",                  1
"5Male2Female",                     1
"8 males",                          1
"8Male 3Female",                    1
"9 Males and 1 female",             1
"9Male 6Female",                    1
"Adult, 2 Female",                  1
F,                                  10263
Female,                             44714
Female  zoea,                       3
female & male,                      1
Female & zoea,                      1
Female and male,                    1
Female juvenile,                    2
Female Ova,                         38
Female Ova Larv.,                   1
female/immature male,               17
Immature female,                    1
indeterminate,                      40857
Juv,                                1
Juvenile,                           10 
Juvenile female,                    1
M,                                  6253
male,                               51817
Male & female,                      137
Male & female adults  juveniles,    1
Male & female ova,                  10
Male & female with ova,             2
Male and female,                    10
Male and female adults and a juvenile of indeterminate gender,1
Male immature,                      1
Male Juv,                           1
Male juvenile,                      1
"Male, Female",                     3
MaleFemale,                         251
MaleFemale Juv,                     2
MaleFemale Ova,                     23
MaleMale,                           1
mixed,                              219
non applicable,                     37
Not Specified,                      736808
not stated,                         17
U,                                  31160
undefined,                          47114
unknown,                            65314

FROM EUROBIS (SEx)
"sex","count"
[NULL],                 0
"1 Male 1 Female",      1
"1 Male 2 Female",      1
"1 Male 3 Female",      1
B,                      44695
Both,                   284
F,                      558634
female,                 58448
female & male,          1
Female (1),             94
Female (2),             17
Female (3),             8
Female (4),             1
Female (5),             3
Female (8),             1
Female (9),             1
Female;Male,            25
Female;Male;Unknown,    6
Female;Unknown,         12
H,                      93
Hermaphrodite,          6
I,                      21073
Immature,               9441
IND,                    382226
indeterminate,          3600
Juveniles,              1
Larvae,                 1
M,                      479674
male,                   60374
Male (1),               47
"Male (1), female (1)", 2
"Male (1), female (16)",1
"Male (1), female (2)", 7
"Male (1), female (3)", 7
"Male (1), female (4)", 4
"Male (1), female (7)", 1
"Male (1),Female (1)",  26
"Male (1),Female (2)",  1
"Male (1),Female (4)",  2
"Male (12), female (2)",1
Male (2),               13
"Male (2), female (1)", 15
"Male (2), female (2)", 3
"Male (2), female (3)", 6
"Male (2), female (5)", 1
"Male (2), female (7)", 1
"Male (2),female (1)",  1
"Male (3), female (10)",1
"Male (3), female (2)", 2
"Male (3), female (3)", 1
"Male (3), female (4)", 1
"Male (3),Female (2)",  1
Male (4),               1
"Male (4), female (1)", 2
"Male (4), Female (2)", 2
"male (4), female (3)", 1
"Male (4), female (8)", 1
"Male (5), female (2)", 1
"Male (6), female (4)", 1
"Male (8), female (5)", 1
Male;Unknown,           10
Mixed,                  1225
non applicable,         37
Not specified,          7966
not stated,             17
NULL,                   1833
p,                      1
U,                      5925629
undefined,              46103
Undetermined,           52590
UNK,                    1400
unknown,                66000
x,                      1

```   

9. Same thing for BasisOfRecord ('O','L','S','G','P','D')
``` 
"BasisOfRecord","count"
[NULL],                 0
A,                      462
D,                      176936
HumanObservation,       3860996
L,                      364
literatureObservation,  12
MachineObservation,     193684
materialSample,         5014769
O,                      14481255
observation,            1228517
Occurrence,             37945
Preserved Specimen,     10373
PreservedSpecimen,      2411524
S,                      162088
StillImage,             6481
T,                      9454

```
---

## 31/12/2021

- QC logic is all inverse, QC bits are 1 if the QC is "passed" meaning they are quality stamps, not error flags.

---

## 03/01/2021

- Recommended fields in OBIS, what to do in EUROBIS? Options to look for. 
- Continuing adapting to QMask logic instead of Error mask logic (Location, Taxonomy and Required fields OK, tests to be 
  corrected, time and measurements too)
- Corrected tests for location QCs, noticed that DB has fields MinimumDepth and MaximumDepth while DwCA 
  records have minimumDepthInMeters and maximumDepthinMeters. Need to map to a SQL table to SQL view in the 
  QC pipeline with "proper names" OR make names dynamic (such as lower case check for smaller field name)? 
  Look at the mapping provided by Bart.

---

## 04/01/2021

- Resuming corrections : Tests for measurement checks - improved code as well
- Completed review of test cases, with corrections to use the QC as a quality label  
- Exploring Data 

  
- **Question** Where are the DynamicProperties in the database (or are there any in the DB)?
- Answered - they may have been removed 

``` 
-- How to create an ID column on a table without one

;WITH cte AS
(
    SELECT Id, ROW_NUMBER() OVER (ORDER BY NEWID()) AS RowId
    FROM   #test
)

UPDATE cte
    SET Id = RowId
    
```
---

## 05/01/2021

- started working on dataset extraction 

- **question** on dates: according to the mapping eventDate is derived from the start and end fields and the timezone,
however there is not enough of them filled to get the event date. For example all records for dataset with providerID=5480 
  have all their temporal data set to NULL. The correspondant DwCA file has the event date set to 1982-09 for the events and 
  nothing for the occurrences. This can be derived only from an external source, like the EML (which contains 1982-09-02 to 1982-09-02). Is this a correct way of deriving 
  the eventDate ? Should I do that? In general the DwCA files have this field filled most of the time. Asked to Bart
  
- Designing the dataset class, and writing the extraction code, initial ideas, tested extraction of dates from EML 
- Must design API call to retrieve EML from data service 
- started implementation of retrieval of provider data from SQL 
- Must complete by adding other SQL for records, call to EML service and extraction of dates and areas from EML

---

## 06/01/2021 

- Received answer from Bart, incorporating feedback. Looked at SQL function to get ISO_8601 dates  
- Designing query/routines for dataset extraction - would there be a convenience in using Pandas? Use SQL in any case
- Extracted dataset records from DB based on dataproviders.id. Also implemented API to get the EML and extract areas from it  
- DONE: Verify query returns all necessary fields for QC runs.
- DONE: Verify the hypothesis of not really needing an ID for the eurobis table
- DONE: Start implementing an update query for the eurobis table 
- DONE: Start implementing a test pipeline for xyz number of files. 

---

## 07/01/2021

- Looking at the area extraction. This is not solid, and the API is inconsistent. Looking at the JSON output, which would 
  be easier to parse, it is even more inconsistent, as the areas are reported as nulls, while in the eml sometimes (Mostly) 
  are wrong.
- First version of dataset.py, containing a class that represents a eurobis dataset ready to be labeled for quality 
- Fields are mapped as per DwCA names, extraction follows the view in the DB to preserve consistency. Only the necessary
  fields used by the QC and the fields useful to retrieve the records in the DB are retrieved. 
- Corrected data extraction to retrieve scientificNameId in the Obis format (to preserve pipeline consistency between DB 
  and DwCA files. Note, the DwCA pipeline is only a DEMO, while the MS SQL shall change the records) 
- Built easy access index map between EV_OCC to EMOF in dataset 
- Built Dataset chooser gui for easy demo of dataset loading. Loads all sorts, good example: 795, shark_bacterioplancton
- Correcting tests, verifications. 
- Working at the processing pipeline: 
   - event records, cumulate for pyxy calls in batches of 1000, do basics, then emof 
   - occurrence records, cumulate for pyxy calls in batches of 1000, then emof 
   - update events in DB table (strategy to be figured out)
   - update occurrences in DB table (strategy to be figured out)

---

## 08/01/2021

- Re-building QC pipeline for datasets: Preparing batches for pyxylookups - per event type (as they are now split) - or find 
  other way. 
- Improve required_fields by replacing lookup lists with sets (which are hashed) and eliminating conversions during the QC
- Testing extraction and evaluation pipeline on dataset 
- Evaluating profiling to spot time hogs - MAJOR RESULT by correctly indexing taxon and reducing output/reqest size to "genus"
  - Rebuilt two search indexes for taxon on scientificNameID and scientificName
  - Built function to return only sought fields from lokup (not entire record)  
  - Used sets for presence checks, they are faster as they are hashed  
  - time improved by a factor of 1000 on occurrences, improved also events 
- VC with Bart, Proposed course of action: Parallelization, Verification, Write to DB (look at way to get key with ROW_NUMBER, may be 
  already during dataset load)
- Discussed way to feed back QC to the event records when CORE Type is Event (other look-up like in emof) and maybe not write the 
  QC to the occurrence records. 
- **ONGOING**: Generate new version of lookupDB and publish to github
- **DONE**: Fix example pipeline for DwCA files 
- **DONE**: Consider implementing lookups also for QC 10 for better flexibility (question on the recommended fields)

---

## 11/01/2021
- Database study: Which understand how to process the records with no Event ID and no Occurrence ID. 
- Attempted solution at : https://www.mssqltips.com/sqlservertip/1467/populate-a-sql-server-column-with-a-sequential-number-not-using-an-identity/
  to create an ID with an integer column updated. This should be much faster than creating an autoincrement. The solution in memory 
  should not work because you are not guaranteed that the row_id will always be the same as we do not know what can be used to 
  distinguish the rows (order by clause) calculating the time.  
- Error in update: Stored procedures and triggers refer to [eurobis].[dbo].[eurobis]. In the imported MSSQL the database name is þeurobis_dat]. 
  Therefore, update queries do not work (dataset records - modification dates - in dataprovider are updated upon update/insertion etc).
- Should : 1) Remove triggers, 2) re-create triggers after temp key creation. Tested on DB - OK, not yet in python.
- Pipeline for DB (avoid lookups at all costs): 
  - If dataset core type is occurrence: 
    - Process eMof For that occurrence (if any) 
    - process occurrence and OR all QC together on the occurrence
  - if core type is event: 
    - Process emof for event (hold it)
    - For each occurrence: 
      - Process eMoF for that occurrence (if any) 
      - process occurrence and OR al QC together on the occurrence - Hold QC 
    - process event and OR all QC together on the event, including the eMoF
  
---

## 12/01/2020 
- Database Study as a consequence of the feedback from Bart: Attempt to use the **%%physloc%%** column. This is undocumented,
  and risky as it could not work in future releases of MS SQL. However, as it will only be used to update existing rows, 
  it should remain consistent at least for the time necessary to perform the QCs (on a dataset or multiple at the same time). 
- Implemented record update, uses dataset, lat and lon (when available) that are indexed to speed it up, while the %%physloc%% 
  is not. Updates are done by record, Commits are done in batches, tried 100 and 500, seems OK. May look for other tricks if 
  needed. 
- Next : Look at parallel processing: Build a Pool for parallel pipeline for num_cpu -2 (at least 2 are needed for mssql), passing 
  a slice of the datasets (would limit in the beginning). 
- DONE : Correct pipeline for DwCA, to be consistent with Database processing 
- ONGOING : Tests and Document, install on other PC and try to run in parallel on MSSQL

---

## 13/01/2021 
- Update query optimization, attempted to use fields that are not null and involved in indexes to speed up the 
  record update process. Fields ALWAYS used for update query are : dataprovider_id and %%physloc%%. Fields used for update 
  when not null are Latitude, Longitude, EventID and scientificName. 
- Checking correctness, found a miss in the checks of eMoF, due that the eventID is often filled in datasets where 
  the DarwinCoreType = 1. Used for something else. So, the keying mechanism for eMoF need to be adapted.
- Also looked at sex check for occurrence records - found error and corrected, need more automated tests.   
  
- DONE: Implement lookup also for basic fields reqirements (whenever there is a lookup to do really). This will bring consistency 
  and flexibility. 
  
- Looking at parallelization, start with a limited number of datasets, found formula to get x percent of a table at random. 
  Same approach as for files does not seem to work, probably due to mssql or some wrong assumption. To review.

- Looking at changing the example pipeline for DwCA, finding strategy to compare the results ... 

---

## 14/01/2021 

- Cleaned DwCA pipeline, made external call to extract the small user interface, created structure to avoid loops
- Checked completion time, checked also parallelism - OK 
- Implemented lookups also for QC 1 and 10 (required fields and basis of records)  
- DONE: Implement and check parallelism of MSSQL version - attempt is failing, (due to ODBC?) - redesign MSSQL 
  connectivity to return a different connection per call, as in https://stackoverflow.com/questions/25851011/using-pyodbc-in-multi-processing-code
- DONE: Test different approach than pyodbc: pymssql. 

---

# 15/01/2021 
- Installed PC for test install/verification/documentation (ubuntu 20.04) 
- Do performance evaluation using pymssql vs pyodbc 
- Results : 
```
FILE/TASK                   PYODBC            PYMSSQL    DIFF %        
------------------------------------------------------------------
Connect Test                 0.014s            0.011s    21%
Assoc. Cetacea               0.99s             0.74s     25.25%
Shark bacterioplankton     157.42s           151.54s      3.73%
gbif_9186 (Zoological...)  217.86s           207.59s      4.71% 
```

On these small - medium sized files the pymysql provides a consistent performance advantage over pyodbc. The 
last file consists of only occurrence records, meaning that there is less time spent on retrieving the results 
from SELECT queries and more time in proportion spent in UPDATE queries. It is still an advantage, albeit small. 
The driver has been made configurable from the configuration options, and for the follow-up of the development, 
the pymssql shall be used. 

- Multiprocessing for mssql: Not safe, noticed hang on call to pyxylookup (not the first time). Should make it 
  depending on a response time (10 secs) if it does not return, then detect if it is hanging, it yes kill and relaunch. 
  (DONE) - Notice, this is a speculation!
```
Pool 0 started
Pool 0 completed in 196.1453251838684

Pool 1 started
Pool 1 completed in 94.53070735931396

Pool 2 started
Pool 2 completed in 409.71728348731995

Pool 3 started
Pool 3 completed in 183.79612970352173

Pool 4 started
----- MISSING! No feedback, only case observed when pyxylookup call was hanging -----  

Processed dataset 830 in  3.203357458114624
Processed dataset 916 in  32.88600730895996
Processed dataset 63 in  82.72491765022278
Processed dataset 695 in  87.85252141952515
Processed dataset 730 in  6.66422963142395
Processed dataset 145 in  21.06403613090515
Processed dataset 806 in  117.63000011444092
Processed dataset 852 in  180.58823657035828
Processed dataset 241 in  92.34957456588745
Processed dataset 808 in  292.08416628837585

```
  
- DONE: Also must try the parallel processing with the pyodbc and make the pipeline parametric with respect to the dataset
  list (can be called on a fixed dataset list, if not, use the percent, if percent not specified, then 1% (0.01))
- DONE: Parallel processing using PYMSSQL seems to hang (may be it is pyxylookup but cannot say) - TEST & PROTECT - 
  in fact this may be to a non-return of REST API pyxylookup. Should wrap it in something like (stopit)
- DONE: Make uniform and consistent logging across all files  

---

## 18/01/2021 

- Cleaning and uniforming all printing and logging (using only logging on all tests - all files). DONE
- Note - Logging may have some troubles with multiprocessing (does not really seem to affect us)
- Possible improvements (for future): Optimization of Database update queries (using batches updates or temp queries) 
- **ONGOING:** Looking at deployment on a different PC (still Linux). Do I have everything sorted out? 
- **TODO**: Take care of the testing / coverage / package properties -- Check for as much completeness as possible
- **ONGOING**: Write install procedure and user instructions 
  
- With the ONGOING task found many error in the deployment/setup script, correcting. 

---

## 19/01/2021
- First run from a different PC, in parallel with run from dev PC. 
- Starting the installation notes.  
- Added the configuration parameter to specify whether the MS SQL server is local, 
  used to decide the number of CPUs to allocate to the multiprocessing examples 
- Testing 

## 20/01/2021
- Build a "pipeline" that allows easily to select a set of datasets from the database and perform QC -
  using multiprocessing. Once done, run it on the entire DB, using two PCs (4 atom cores, 5 i7 cores)
  - DONE - ready to run on the entire DB. 

---

## 21/01/2021
- Worked at the pipeline, testing. DB performances decrease over time, need to find a better way (however it does not fail)
- Reorganizing examples, looking for opportunities for optimization. 

--- 

## 22/01/2021
- Testing 
- DONE: Request from Bart: 
  "Demo" test: Select a random record from a random dataset, all subrecords and perform QC on it 
  (Show all intermediate steps/dependent records)
- For EVENT based datasets, redesign the concept of required fields (must be the COMBINATION of all dependent fields that 
  satisfies the REQUIRED FIELDS criteria). 

- From discussing with Bart: In case of datasets with core record type = EVENT, 
  attempt to make the aggregation of measurements from the occurrence records to the event record 
  depending upon a parameter: OR, AND or PERCENTAGE. 
  
- Attempt to run on the biggest datasets - completed 

# 23-24/02/2021
- Attempting optimization and running on big datasets 

# 25/02/2021 
- Technique to disable/rebuild index on QC - implemented, results are inconsistent. 
- Tested on Dataset ID 1062 
``` 
--------------------------------------------------
Loaded dataset pohjedatabase, id = 1062 
Number of event records: 31012
Number of occurrence records: 91121
Number of emof records: 269799
Interesting areas: None
Imis dataset ID: 5725
Type of core records: Event
--------------------------------------------------
Index Disabled: 

Total net processing time for 1062 : pohjedatabase in: 494.4684865474701 

Index Enabled: 

Total net processing time for 1062 : pohjedatabase in: 435.1352186203003 

New Query for Occurrence, including aphia_id Index Disabled: 

 - Dreadful (stopped)! 

New Query include only dataprovider id and physloc, Index Enabled:
Total net processing time for 1062 : pohjedatabase in: 442.73728132247925 

New Query, include only dataprovider id and physloc, Index Disabled:

 - Dreadful (stopped)!

```
- Re-introduced old queries and made the index disabling optional, only left it in the 
  multiple dataset processing / multiprocessing (parameter).
- Code cleanup and rationalization
- Single record tests   
- Email to Bart 








  
