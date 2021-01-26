# EUROBIS-QC

## Background
Implementation of a seiries of Quality Control checks on EUROBIS DwC-A records (dictionaries).

Based on:

obistools: https://github.com/iobis/obistools
obis-qc: https://github.com/iobis/obis-qc
dwca-processor: https://github.com/iobis/dwca-processor

And other libraries, almost all from Pieter Provoost. 

## QC System architecture

The QC for the the eMoF/MoF records are exclusively based on lookups from a locally available SQLITE database. 
This also contains a copy of the WORMS database for lookup of the aphia ids. 

Furthermore, the verification of the record's Lat/Lon to ascertain that a point is at sea and that the reported 
depth is coherent with the depth map of the point is performed through calls to the pyxylookup service. 
These calls are performed for batches of 1000 (and leftovers) points for better network usage.  

#### Main system components   

The diagram below can help figure out at a glance the main architectural components of the EUROBIS-QC concept.
![image](resources/Architecture.png)


The QCs works on Events/Occurrence records from DwCA files as well as on records stored in a MSSQL database. 
The examples provided, all found under /eurobisqc/test, are explicatory of the ways to process:

- a single DwCA file (QCs are not stored) (run_dwca_pipeline.py)
- a set of DwCA files contained in a directory using multiprocessing (run_dwca_multiprocess.py)
- a dataset contained in the eurobis database (run_mssql_pipeline.py) - **UPDATING** the database
- a random number of datasets (2% selected among those with less than 2500 records) from the database **UPDATING** the
  database

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

It has been agreed to not implement QCs 8 and 20 for the moment, so there is no QC procedure that deals with these two.  


## Installation

### Ubuntu Linux 20.04 

#### Starting from scratch - creating the basis
You need to have Python3 installed (default) and as a minimum the modules pip and venv : 

```commandline
sudo apt install python3-pip python3-venv
```
You need to have git installed: 
```
sudo apt install git 
```
Futehrmore, you need to have odbc installed if you want to use the pyodbc driver for MS SQL or freetds for the pymssql 
driver:

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
username      = <Your User>
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

















