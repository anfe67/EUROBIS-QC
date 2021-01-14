""" Demonstrates QC processing of a DwCA archive  """
import dwca_example_pipeline
from eurobisqc.test.util import file_chooser


with_logging = False
with_print = True

filename = file_chooser.get_archive_chooser()

if filename is None:
    exit(0)

dwca_example_pipeline.dwca_file_labeling(filename, with_print, with_logging)
