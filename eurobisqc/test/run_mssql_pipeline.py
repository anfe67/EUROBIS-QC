""" Demonstrates QC processing of a DwCA archive  """
import mssql_example_pipeline
from eurobisqc.test.util import dataset_chooser


with_logging = False
with_print = True

dataset_id = dataset_chooser.get_dataset_chooser()

if dataset_id is None:
    exit(0)

mssql_example_pipeline.dataset_qc_labeling(dataset_id, with_print, with_logging)
