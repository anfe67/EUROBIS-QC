import sys
import time
import logging

from dbworks import mssql_db_functions as mssql
from eurobisqc.util import misc
from eurobisqc.test.mssql_example_pipeline import process_dataset_list

this = sys.modules[__name__]
this.logger = logging.getLogger(__name__)
this.logger.level = logging.DEBUG
this.logger.addHandler(logging.StreamHandler())


def do_dataset_parallel_processing(percent):
    """ Example of processing multiple datasets at the same time in
            order to exploit the computing resources available """

    start_time = time.time()

    # Now set to a percent of datasets...
    # sql_random_percent_of_datasets = f"SELECT id FROM dataproviders WHERE {percent} >= CAST(CHECKSUM(NEWID(), id) " \
    #                                  "& 0x7fffffff AS float) / CAST (0x7fffffff AS int)"

    # This selects percent from SMALL datasets (less than 4000 events/occurrences)
    sql_random_percent_of_datasets =f"select a.id, a.displayname, a.rec_count from " \
                                    f"(select d.id, d.displayname, rec_count from dataproviders d " \
                                    f"inner join eurobis e on e.dataprovider_id = d.id " \
                                    f"where rec_count <= 4000 group by d.id, d.displayname, rec_count) a " \
                                    f"where {percent} >= CAST(CHECKSUM(NEWID(), id) & 0x7fffffff AS float) " \
                                    f"/ CAST (0x7fffffff AS int) order by id "


    dataset_ids = []
    dataset_names = []

    import multiprocessing as mp
    # we dedicate to the task the total number of processors - 3 or 1 if we only have 2 cores or less.
    # Knowing that mssql needs 2 cores at least.
    if mp.cpu_count() > 3:
        n_cpus = mp.cpu_count() - 3
    else:
        n_cpus = 1

    pool = mp.Pool(n_cpus)

    # Connect to the database to get dataset list
    if not mssql.conn:
        mssql.open_db()

    if mssql.conn is None:
        # Should find a way to exit and advice
        this.logger.error("No connection to DB, nothing can be done! ")
        exit(0)
    else:
        # Fetch a random set of datasets
        cur = mssql.conn.cursor()
        cur.execute(sql_random_percent_of_datasets)
        for row in cur:
            dataset_ids.append(row[0])
            # tuples names - size
            dataset_names.append((row[0], row[1], row[2]))

    mssql.close_db()

    # Retrieved list, now need to split
    dataset_id_lists = misc.split_list(dataset_ids, n_cpus)  # We are OK until here.
    dataset_names_lists = misc.split_list(dataset_names, n_cpus)

    result_pool = []
    for i, dataset_id_list in enumerate(dataset_id_lists):
        this.logger.info(f"Pool {i} will process {dataset_names_lists[i]} - (#, name, records)")
        result_pool.append(pool.apply_async(process_dataset_list, args=(i, dataset_id_list, True)))

    for r in result_pool:
        r.wait()

    pool.terminate()
    pool.join()

    this.logger.info(f"All processes have completed after {time.time()- start_time}")

# Parallel processing of random 2% of the (SMALL) datasets
do_dataset_parallel_processing(0.02)