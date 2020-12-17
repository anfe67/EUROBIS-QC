from unittest import TestCase

import sys
import os
import time
from eurobisqc.util import extract_area

from dwcaprocessor import DwCAProcessor

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))


class Test(TestCase):

    def test_find_area(self):
        # Need to make sure that this is correct...

        filename = os.path.join(os.path.dirname(__file__), "../data/dwca-meso_meiofauna_knokke_1969-v1.7.zip")
        archive = DwCAProcessor(filename)

        xml_input = archive.eml
        area = None
        start = time.time()

        for i in range(100):
            area = extract_area.find_area(xml_input)
        end = time.time()

        print(f"Duration with xmltodict: {end - start}")
        # Not complete, should verify area content

        self.assertIsNotNone(area)
        print(area)
