# Verifications 

## Sample DwCA file : "data/dwca-meso_meiofauna_knokke_1969-v1.7.zip"

The QC pipeline verifications are performed using dev_pipeline in the test directory. 

* The DwCA archive is parsed using dwca-processor and the records are browsed. The Core full records 
  (the records in the Event table - or if these are absent the Occurrence) are checked for the 
  location checks.
  
* The Occurrence records (full) are used to apply the taxonomy checks. All verifications return a number 
  which is a combination of the bit checks per record. 

* The file contains: 24 Event records, 342 Occurrence records and 165 ExtendedMeasurementOfFacts records.

