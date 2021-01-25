""" Demonstrates QC processing of a DwCA archive  """
import dwca_pipeline
from eurobisqc.test.util import file_chooser


with_logging = True

filename = file_chooser.get_archive_chooser()

if filename is None:
    exit(0)

dwca_pipeline.dwca_file_qc(filename, with_logging)
