""" Develop script - test  """

import os
os.chdir("/var/www/vhosts/eurobis-qc.git/eurobisqc/")
from dbworks.create_lookup_tables import import_files
import_files()
#
from eurobisqc.examples import mssql_pipeline
mssql_pipeline.process_dataset_list(0, [1071], False, True)
#mssql_pipeline.process_dataset_list(0, [1450], False, True)
#mssql_pipeline.process_dataset_list(0, [1177], False, True)

# from eurobisqc.examples import run_mssql_whole_db
# run_mssql_whole_db.process_all_db(True, True)
