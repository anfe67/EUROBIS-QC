import sys
import os
import logging
from eurobisqc.examples.dwca_pipeline import dwca_process_filelist
from eurobisqc.test.util import file_chooser
from eurobisqc.util import misc

# Use "this" trick
this = sys.modules[__name__]
this.logger = logging.getLogger(__name__)
this.logger.setLevel(logging.DEBUG)
this.logger.addHandler(logging.StreamHandler())


def dwca_parallel_processing(with_logging=False):
    """ Example of processing multiple files at the same time in
        order to exploit the computing resources of the machine """
    import multiprocessing as mp

    # we dedicate to the task the total number of processors - 2 or 1 if we only have 2 cores or less
    if mp.cpu_count() > 2:
        n_cpus = mp.cpu_count() - 2
    else:
        n_cpus = 1

    pool = mp.Pool(n_cpus)

    # Get the list of files in a directory, containing ONLY DwCA zip files...
    folder = file_chooser.browse_for_folder()

    if folder is None or folder.strip() == "":
        this.logger.error("Invalid Directory selection")
        exit(0)

    dwca_files = os.listdir(folder)

    if dwca_files is None or len(dwca_files) == 0:
        this.logger.error("No files to process")

    # Adding path info to file names in temp list...
    fnames = [os.path.join(folder, f) for f in dwca_files
              if os.path.isfile(os.path.join(folder, f))
              and f.lower().endswith(".zip")
              ]

    dwca_files = fnames

    if dwca_files is None:
        this.logger.warning("WARNING: Call to dwca_parallel_processing with no filename list")
        exit(0)

    dwca_file_lists = misc.split_list(dwca_files, n_cpus)
    this.logger.info(dwca_file_lists)

    # Each one of the CPUs shall get a similar load...
    result_pool = []
    for i, dwca_file_list in enumerate(dwca_file_lists):
        result_pool.append(pool.apply_async(dwca_process_filelist,
                                            args=(i, dwca_file_list, with_logging)))

    # We are interested in waiting, not getting the results...
    for r in result_pool:
        r.wait()

    # Should not harm
    pool.terminate()
    pool.join()


do_logging = False
dwca_parallel_processing(do_logging)
