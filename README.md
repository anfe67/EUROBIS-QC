# EUROBIS-QC

## Background
This project consists in the implementation of a series of Quality Control checks on marine biodiversity records 
(implemented as Python dictionaries). The records are either stored in DwCA archives or in a MS SQL database. 

Based on:

```
obistools:       https://github.com/iobis/obistools
obis-qc:         https://github.com/iobis/obis-qc
dwca-processor:  https://github.com/iobis/dwca-processor
pyxylookup:      https://github.com/iobis/pyxylookup
isodateparser:   https://github.com/pieterprovoost/isodateparser
```
And other libraries, almost all from Iobis (https://github.com/iobis) and authored by Pieter Provoost. 

### Requirements 
A modern PC, 8G of RAM, better if OS is Linux because all the development has been performed under Ubuntu 20.04 using Pycharm. 
Pycharm is not needed in order to run the examples provided with system, and all the examples except the biggest 
dataset currently available run fine on an modest Atom based PC (2009, 4G RAM). 

## QC System architecture

The diagram below can help figure out at a glance the main architectural components of the EUROBIS-QC system.
![image](resources/Architecture.png)

The EUROBIS-QC system relies on: 

- Local Logic
- SQLITE Database Lookups   
- External REST API Calls

The bulk of the QC logic is in the **eurobisqc** package. The QCs rely on local logic (for instance to verify presence
and validity of latitude and longitude, min/max depth or validity of dates), or on calls to external 
REST APIs (for instance the pyxylookup API to verify that a point is at sea and which is the point's depth). 

A number of QCs are implemented by mean of lookup into a locally available SQLITE database. The lookup tables 
can be easily modified by acting on a set of configuration files and quickly regenerated, including index creation.  
This SQLITE database contains a copy of the WORMS database for the Taxonomy QCs, most noticeably to lookup 
the aphia ids and to establish the rank of the aphia ids.

All Database Logic is in the **dbworks** package. This includes the SQLITE for lookups and the MS SQL logic to access
the eurobis datasets on which to calculate the QC values. 

Furthermore, the verification of the record's Lat/Lon to ascertain that a point is at sea and that the reported 
depth is coherent with the depth map of the point is performed through calls to the pyxylookup service. 
These calls are performed for batches of 1000 (and leftovers) points for better network usage.

Another API which is called to obtain the geographical areas in which the dataset has been collected, is the IMIS 
database. The geographical retrieval of the area through IMIS is specific to the datasets and it has been implemented
in the EurobisDataset (eurobis_dataset.py). For the DwCA files, the same information is extracted from the file's 
eml, which is extracted by DWCAProcessor. 

External API calls are protected, they run within a "timeoutable" thread, which returns None in case of failure. In those
cases, the API calls are simply re-issued.

#### Examples provided   

The QCs works on Events/Occurrence records from DwCA files as well as on records stored in a MSSQL database. 
A set of small DwCA archives are provided under eurobisqc/test/data. 

The examples provided, all found under /eurobisqc/examples, can be used to process:

- a single DwCA file (QCs are not stored) (run_dwca_pipeline.py)
- a set of DwCA files contained in a directory using multiprocessing (run_dwca_multiprocess.py)
- one or more datasets contained in the eurobis database (run_mssql_pipeline.py) - **UPDATES** the database
- a random number of datasets (2% selected among those with less than 2500 records) from the database **UPDATES** the
  database
- the calculation of a random record from a random data set, having less than 10000 records, 
  printing all explanatory info: (mssql_random_record.py)  

#### QC applied to records 
QC is calculated on Event Records and Occurrence records, as follows: 
![image](resources/EurobisQC.png)
  
The class at the core of the system is the Enum QFlag, in eurobisqc.util.qc_flags. It contains all the defined QCs, 
and utilities to combine/encode/decode QC flags:

```python
REQUIRED_FIELDS_PRESENT = ("All the required fields are present", 1)  # In required_fields
TAXONOMY_APHIAID_PRESENT = ("AphiaID found", 2)  # In taxonomy_db
TAXONOMY_RANK_OK = ("Taxon level more detailed than Genus", 3)  # In taxonomy_db
GEO_LAT_LON_PRESENT = ("Lat and Lon present and not equal to None", 4)  # In location
GEO_LAT_LON_VALID = ("Lat or Lon present and valid (-90 to 90 and -180 to 180)", 5)  # In location
GEO_LAT_LON_ON_SEA = ("Lat - Lon on sea / coastline", 6)  # In location
DATE_TIME_OK = ("Year or Start Year or End Year complete and valid", 7)  # In time_qc
TAXON_APHIAID_NOT_EXISTING = ("Marine Taxon not existing in APHIA", 8)  # FLAG - NOT IMPLEMENTED
GEO_COORD_AREA = ("Coordinates in one of the specified areas", 9)  # In location
OBIS_DATAFORMAT_OK = ("Valid codes found in basisOfRecord", 10)  # in required_fields
VALID_DATE_1 = ("Valid sampling date", 11)  # In time_qc
VALID_DATE_2 = ("Start sampling date before End date - dates consistent", 12)  # In time_qc
VALID_DATE_3 = ("Sampling time valid / timezone completed", 13)  # In time_qc
OBSERVED_COUNT_PRESENT = ("Observed individual count found", 14)  # In measurements
OBSERVED_WEIGTH_PRESENT = ("Observed weigth found", 15)  # In measurements
SAMPLE_SIZE_PRESENT = ("Observed individual count > 0 sample size present", 16)  # In measurements
SEX_PRESENT = ("Sex observation found", 17)  # In measurements
MIN_MAX_DEPTH_VERIFIED = ("Depths consistent", 18)  # in location
DEPTH_MAP_VERIFIED = ("Depth coherent with depth map", 19)  # In location
DEPTH_FOR_SPECIES_OK = ("Depth coherent with species depth range", 20)  # FLAG - NOT IMPLEMENTED

```
As a reference, this article can be used: https://academic.oup.com/database/article-pdf/doi/10.1093/database/bau125/16975803/bau125.pdf 

It has been agreed to not implement QCs 8 and 20 for the moment, so there is no QC procedure that deals with these two.
Also Outliers analysis is not part of this implementation. 

### QC Procedures description: 

All QCs are performed on a record (Python dictionary) or a set of, responding to the specifications provided in the 
three references below.

- **Occurrence**: https://rs.gbif.org/core/dwc_occurrence_2020-07-15.xml
- **Event**: https://rs.gbif.org/core/dwc_event_2016_06_21.xml
- **eMoF**: https://rs.gbif.org/extension/obis/extended_measurement_or_fact.xml

Such records can come directly from  DwCA archives or from an object of class EurobisDataset, which has been built to 
mirror the functionality of DWCAProcessor but reading from the MSSQL Database EUROBIS instead of DwCA files. 
The EurobisDataset class contains a method called 
load_dataset(dataprovider_id) which loads all the records of a dataset in memory, provides to the fields 
"reconciliation" so that records from DWCAProcessor and EurobisDataset will look exactly the same to the QC procedures
and builds also the necessary indexes, in one pass. The EUROBIS database contains a single table for both event type 
records and occurrence type records. 
It is important to notice that this **is not** a generator, all the dataset records are actually loaded in memory. 
Different strategies may be implemented, but this has not been part of the effort, as PCs with 8 G of RAM can deal 
with aany of the datasets currenly present in the database, and a PC with 4G or RAM has been successfully tested with a 
dataset of 1M records. 

QC Procedures are located in the files:
```
- eurobisqc/required_fields.py:    QC 1, 10
- eurobisqc/location.py:           QC 4, 5, 6, 9, 18, 19
- eurobisqc/time_qc.py:            QC 7, 11, 12, 13
- eurobisqc/taxonomy.py:           QC 2, 3 
- eurobisqc/measurements.py:       QC 14, 15, 16, 17
```

These are used in a slightly different way in examples/dwca_pipeline.py and examples/mssql_pipeline.py, because of the 
way in which the records are read. 

There are two types of datasets, those with the data hyerarchy starting at "Event" records (DarwinCoreType = 2) and 
those starting at "Occurrence" records (DarwinCoreType = 1). Record QCs is calculated as follows : 

#### From the image, for datasets with core record type = occurrence:

1. The Occurrence records are checked for all the implemented QC and also for Sex (as a specific field Sex is present 
in the eurobis table which may be populated for an occurrence record).  
These are QCs from 1 to 19 except 8 (not implemented), 14, 15 and 16. Basically all QCs except those for eMoF records.

2. The QC calculated on the **set** of eMoF records which are related to the occurrence record being examined. These 
QCs are related to the possible measurements: Sample Size, Count, Weight, Sex (QCs 14, 15, 16, 17). The calculated 
values are then OR-red to the occurence records' own QC. These values are **not** stored in the eMoF records.  

#### From the image, for datasets with core record type = event:

1. QCs performed on Event records are: Location (4, 5, 6, 9, 18, 19), Dates/Times (7, 11, 12, 13), Required 
fields (1).  
   
2. eMoF records for **Event** Records are NOT considered for QC calculations. They relate to instruments, conditions 
and are not related to biological observations. 

3. The Occurrence records are checked for all the implemented QC and also for Sex (as a specific field Sex may be 
populated for an occurrence record).  These are QCs from 1 to 19 except 8 (not implemented), 14, 15 and 16. Basically
all QCs except those for eMoF records. 

4. The QCs are calculated on the **set** of eMoF records which are related to the occurrence record being examined. These 
QCs are related to the possible measurements: Sample Size, Count, Weight, Sex (QCs 14, 15, 16, 17). The calculated 
values are then OR-red to the occurence records' own QC. These values are **not** stored in the eMoF records. 
   
5. The QC calculated for event records is normally pushed down to all Occurrence Records. This is because often the 
position, dates of the occurrences are all derived from the event, and they are not present on the occurrences. 
   
6. **SPECIAL NOTE** for the required fields check. Here, after having processed each occurrence record, 
occurrence record and "father" event records are looked at together to verify that all required fields are present in 
the (set) combination of the two records. A QC procedure located in eurobisqc/required_fields.py is applied to the two
records, if it passes, then QC 1 is assigned to the **occurrence record**. 


## Installation (sdist)

### Ubuntu Linux 20.04 

#### Starting from scratch - creating the basis
The basic requirements are to have Python3 installed (default) and as a minimum the modules pip and venv, which 
can anyway be installed following the procedure : 

```commandline
sudo apt install python3-pip python3-venv
```
Then git needs to be installed: 
```
sudo apt install git 
```
Furthermore, you need to have odbc installed if you want to use the pyodbc driver for MS SQL or freetds for the pymssql 
driver. For installation of both options:

```commandline
sudo apt install unixodbc-dev freetds-bin freetds-dev  
```
On ubuntu, you also need tk (there are some basic graphic elements in the demo programs). 
```commandline
sudo apt install python3-tk 
```

#### Clone the repository: 
```
git clone https://github.com/anfe67/eurobis-qc.git  
```

#### Create the virtual environment
Create a directory where you want to install the project and make a virtual environment, this could (eventually) be 
inside the cloned repository. Then activate it : 
```commandline
mkdir EUROBISQC
python3 -m venv eurobis-qc-venv 
source ./eurobis-qc-venv/bin/activate 
```

#### Customize the configuration 
Edit the config.ini file contained in dbworks/resources/config.ini, by filling the following fields as in the 
example below:

```editorconfig
[SQLSERVERDB]
driver        = ODBC Driver 17 for SQL Server
drivermodule  = pymssql
# drivermodule can be pymssql or pyodbc (needs to be specified).
server        = 127.0.0.1
server_local  = True
# server local will determine the number of processes spawned. MSSQL needs two cores to work OK
port          = 1433
database      = eurobis_dat
username      = <Your MS SQL User>
password      = <Your Password>

```

Please notice that server_local must be True if the database is running on the same machine, False otherwise. 
The configuration of the lookup DB does not change and a sample, which has been used during the development has 
been provided. Instructions to modify the lookup database can be found in the specific documentation. 

#### Local Installation
Once all the configuration is performed, the project can be installing by running the setup file, in the eurobis-qc
directory: 

```commandline
python setup.py install 
```

#### Verification 

To verify that the installation is working, you can run the command: 

```commandline
python eurobisqc/examples/run_dwca_pipeline.py from 
```
a terminal, on the command line. This will launch a dialog box, from which you can select the directory under test/data. 
The list of selected dwca archives shall be loaded and you can select one and click OK to process it : 

![image](resources/screenshot_example1.png)

These files are small but provide a good example of the QC processing involved.  

### Windows 10 

####
Disclaimer: 
The entire project has been developed under Linux, and the only time it has been launched in Windows is to write these 
notes. The installation procedure as described in Linux fails, for several reasons. However, it is possible to create 
a virtual environment containing all the required packages and run the examples contained in the project from 
within Pycharm (for instance). 

We start from a system connected to the internet, with the following installed and continue from there: 

- Python 3.6 or above 
- pip 
- git 

The first things do are to upgrade pip, then to install is the virtual environment support. From a command line: 

```commandline
python -m pip install --upgrade pip
python -m pip install --upgrade virtualenv 
```

Then clone the project repository: 
```commandline
git clone https://github.com/anfe67/eurobis-qc.git
```

Create a virtual environment (better inside eurobis-qc if using Pycharm):
```commandline
python -m venv eurobis-qc-venv
```
Install OS dependencies 
Download and install ODBC Drivers from MS Site: 
https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver15

Install also the pymssql alternative library: 
```commandline
python -m pip install --upgrade pymssql 
```

Open the project in Pycharm, in the terminal view activate the virtual environment if it is not yet activated: 
```
.\eurobis-qc-venv\Scripts\activate.bat (use single backslashes)
```
install the requirements in requirements.txt.    

```commandline
pip install -r requirements.txt
```

On Windows, failures have been experienced while installing the github repositories. In that case, 
the github repositories shall be cloned and 

```commandline
python setup.py install 
```

shall be run for each of them to install the libraries in the virtual environment. The repositories that can 
give troubles and can be installed from the cloned repository are follows : 

```commandline
git clone https://github.com/pieterprovoost/csvreader.git
git clone https://github.com/iobis/dwca-processor.git
git clone https://github.com/iobis/pyxylookup.git
got clone https://github.com/iobis/pyworms.git     **NOTE: Should not be necessary** 
```

#### Configuration 
Configuration of the databases is the same as per Linux, in the same configuration file. 
As in Windows the default decompression settings for the libraries are not the same as per Linux, 
the Lookup database provided in double compressed form under 
```
...\eurobis-qc\dbworks\database
```
Must be decompressed with a tool of choice until the file  EUROBIS_QC_LOOKUP_DB.db is present in the same directory. 

The main difference between the Linux install and the Windows install is that the Linux configuration files are **in the 
virtual environments, where the packages are installed**, while in Windows they are in the **git clone** directory


#### Verification 

To verify that the installation is working, you can open the project from Pycharm and run the 
example file run_dwca_pipeline.py as described above. 

















