# EUROBIS-QC

Implementation of a seiries of Quality Control checks on EUROBIS DwC-A records (dictionaries). 

Based on: 

obistools: https://github.com/iobis/obistools
obis-qc: https://github.com/iobis/obis-qc
dwca-processor: https://github.com/iobis/dwca-processor

And other libraries, mostly from Pieter Provoost. 

Each individual QC take a record (dictionary) of the correct type and produce an integer result,
either 0 or the integer bitmask of the error code. 

As in iobis-qc it is the responsibility of the caller to pass the correct record to the QCs. 

This return value is then to be then OR-red to the QC mask of the record by the caller function.

The final QC value for the record is the result of the OR oof all the QC results. A perfect record 
has a QC value of 0. 

  

 


