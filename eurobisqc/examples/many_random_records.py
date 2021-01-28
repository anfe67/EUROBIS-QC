import logging
import sys

from eurobisqc.examples import mssql_random_record

this = sys.modules[__name__]
this.logger = logging.getLogger(__name__)
this.logger.level = logging.DEBUG
this.logger.addHandler(logging.StreamHandler())


def many_randoms(num=None):
    if num is None:
        num = 1000
    for i in range(num):
        mssql_random_record.process_random_record(True)
