from unittest import TestCase

import sys
import os
import time
import logging

from eurobisqc.util import extract_dates
from dwcaprocessor import DwCAProcessor

this = sys.modules[__name__]
this.logger = logging.getLogger(__name__)
this.logger.setLevel(logging.DEBUG)
this.logger.addHandler(logging.StreamHandler())

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))


# TODO: Test with more datasets
class Test(TestCase):

    def test_find_times(self):
        # Need to make sure that this is correct...
        filename = os.path.join(os.path.dirname(__file__),
                                "../data/dwca-gelatinous_macrozoo_in_deepw_sevastopol-v1.1.zip")

        archive = DwCAProcessor(filename)

        xml_input = archive.eml
        date_string = None
        start = time.time()

        # Repeat some times to get timing
        for i in range(100):
            date_string = extract_dates.find_dates(xml_input)
        end = time.time()

        this.logger.info(f"Duration with xmltodict: {end - start}")
        self.assertIsNotNone(date_string)
