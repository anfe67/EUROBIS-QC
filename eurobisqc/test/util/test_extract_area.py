from unittest import TestCase

import sys
import os
import time
import logging

from eurobisqc.util import extract_area
from dwcaprocessor import DwCAProcessor

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

this = sys.modules[__name__]
this.logger = logging.getLogger(__name__)
this.logger.setLevel(logging.DEBUG)
this.logger.addHandler(logging.StreamHandler())


class Test(TestCase):

    def test_find_areas(self):
        # Need to make sure that this is correct...
        filename = os.path.join(os.path.dirname(__file__),
                                "../data/dwca-gelatinous_macrozoo_in_deepw_sevastopol-v1.1.zip")
        archive = DwCAProcessor(filename)

        xml_input = archive.eml
        areas = None
        start = time.time()

        for i in range(100):
            areas = extract_area.find_areas(xml_input)
        end = time.time()

        this.logger.info(f"Duration with xmltodict: {end - start}")
        # Not complete, should verify areas content

        self.assertIsNotNone(areas)
        # [{"east": east, "west": west, "north": north, "south": south}]

        self.assertTrue(len(areas) == 1)
        self.assertTrue(areas[0]["west"] == 28.63)
        self.assertTrue(areas[0]["east"] == 36.45)
        self.assertTrue(areas[0]["south"] == 41.624)
        self.assertTrue(areas[0]["north"] == 46.218)

        this.logger.info(areas)
