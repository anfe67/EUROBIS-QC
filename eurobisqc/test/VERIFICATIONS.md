# Verifications

## Sample DwCA file : "data/dwca-meso_meiofauna_knokke_1969-v1.7.zip"

The QC pipeline verifications are performed using dev_pipeline in the test directory.

* The DwCA archive is parsed using dwca-processor and the records are browsed. The Core full records
  (the records in the Event table - or if these are absent the Occurrence) are checked for the location checks.

* The Occurrence records (full) are used to apply the taxonomy checks. All verifications return a number which is a
  combination of the bit checks per record.

* The file contains: 24 Event records, 342 Occurrence records and 165 ExtendedMeasurementOfFacts records.

## Parallel processes with pools of num_cpu - 2 if num_cpu > 2, 1 otherwise. 
### Results with a pool of 6 on a fileset lying in a specific folder :

**Pool 0: 2673.506s**
```
- 00270	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-tawitawi_reeffishes-v1.10.zip'
- 00851	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-bayofpuck-v1.1.zip'
- 00167	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-algae_zeebrugge_1977-1978-v1.1.zip'
- 22986	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-north_sea_hypbent_com-v1.9.zip'
- 03546	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-midex_chrome_jn-v1.1.zip'

***TOTAL: 27820***
```
```
**Pool 1: 1336s**

- 00528	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-meso_meiofauna_knokke_1969-v1.7.zip'
- 03095	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-est_grey_seals_00-16-v1.1.zip'
- 00848	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-abundance_density_biomass_harpacticoida_on_cystoseira_calvi_bay_1982-v1.1.zip'
- 00303	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-dasshdt00000394-v1.1.zip'

**TOTAL: 4774**
```

**Pool 2: FAILURE** 
```
- 13030	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-nematodesportuguesecanyons-v1.2.zip'
- 00170	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-manuela_c7f-v1.1.zip'
- 04267	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-zoobenthos_in_amvrakikos_wetlands-v1.4.zip'
- NO-RET	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-macrobenthos-v12.0.zip' 

**TOTAL : FAILURE - CORRECTED File contained other extensions and the extractor (dwca-processor) did not consider them worthy - got empty sets**  
```
**Pool 3: 3684**
```
- 02919	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-dasshdt00000410-v1.1.zip'
- 02356	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-macrobenthic_community_nieuwpoort_1970-1971-v1.1.zip'
- 00993	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-gelatinous_macrozoo_in_deepw_sevastopol-v1.1.zip'
- 40398	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-nsbs-v1.6.zip'

**TOTAL: 46666**
```
**Pool 4: 1929s**
```
- 000468	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-brachiopoda-v1.1.zip'
- 000094	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-deepsea_crinoidea-v1.1.zip'
- 001177	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-dasshdt00000405-v1.1.zip'
- 253608	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-nsbp_robertson-v1.1.zip' 

**TOTAL: 255347**
```
**Pool 5: 2882**
```
- 05115	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-dasshse00000055-v1.1.zip'
- 03546	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-midex_chrome_jn-v1.1 (1).zip'
- 27243	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-ibss_fish_guinea_2015-v8.0.zip'
- 00052	'<FOLDER>/eurobisqc/test/data/handpickedFiles/dwca-7_water_birds_delta_area_1979-1987-v1.1.zip'

**TOTAL: 35596**
```

<span style="color:red">**TOTAL ALL  : 378358**</span>

<span style="color:red">**TOTAL TIME : 3684 (time of last pool)**</span>

  
### Projected results on 25M records: 
The result does not consider load balancing and it is related to a random picked file set. However, timing measured implies 
that this type of processing on a similar PC is capable of processing about 100 records per second, or 360000 per hour, 
or 8640000 per day. It can then be concluded that a similar processing pipeline could process 25M records in about 3 days.

Furthermore: 
Multiple PCs could be started on the task in parallel. Lookup databases could be duplicated. 
