""" Demonstrates QC processing of one or multiple EUROBIS Datasets.
    If more than one is selected, then the multiprocessing pipeline
    is launched """
import mssql_pipeline
import mssql_multiprocess
from eurobisqc.test.util import dataset_chooser


with_logging = True

selection = dataset_chooser.get_dataset_chooser()

if selection is None:
    exit(0)

if isinstance(selection, tuple):
    dataset_ids = selection[0]
    dataset_names = selection[1]
    mssql_multiprocess.do_db_multi_selection(dataset_ids, dataset_names)
elif isinstance(selection, int):
    mssql_pipeline.dataset_qc_labeling(selection, True, with_logging)
