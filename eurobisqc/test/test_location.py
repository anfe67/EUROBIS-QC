from unittest import TestCase
from eurobisqc import location


class Test(TestCase):
    records = [
        {"id": 0, "decimalLongitude": 2.5, "decimalLatitude": 52.2},  # OK Record
        {"id": 1},  # Missing Fields
        {"id": 2, "decimalLongitude": None, "decimalLatitude": 52.2},  # None Field (Out of Range)
        {"id": 3, "decimalLongitude": 182.5, "decimalLatitude": -92.2},  # Out of range
        # Second part, verification on land and bathymetry with lookup
        {"id": 4, "decimalLongitude": -0.09954419929143138, "decimalLatitude": 51.4986459027971,
         "minimumDepthInMeters": 0},  # London
        {"id": 5, "decimalLongitude": 86.92441717157921, "decimalLatitude": 27.98811987288357,
         "maximumDepthInMeters": -8000},  # Everest
        {"id": 6, "decimalLongitude": -148.19503790420853, "decimalLatitude": -18.023063397360637,
         "maximumDepthInMeters": 3538},  # Near Tahiti - OK
        {"id": 7, "decimalLongitude": 14.187487915909733, "decimalLatitude": 40.532233845242864,
         "maximumDepthInMeters": 3538},  # Near Capri - Depth exceeds
        {"id": 8, "decimalLongitude": 14.187487915909733, "decimalLatitude": 40.532233845242864,
         "maximumDepthInMeters": 600},  # Near Capri - Depth ok
    ]

    def test_check_record(self):
        """ tests regular lat lon verifications """

        results = []

        for record in self.records:
            results.append(location.check_basic_record(record))

        assert (results == [0, 8, 16, 16, 0, 0, 0, 0, 0])

    def test_check_xy(self):
        """ tests calls to the lookup service through pyxylookup """

        # first get the QC done
        for record in self.records:
            record["QC"] = location.check_basic_record(record)

        # This should call the pyxylookup and change the records, also assessing the
        results = location.check_xy(self.records)
        print(results)

        assert (results == [0, 0, 0, 0, 32, 262176, 0, 262144, 0])

    def test_api_call(self):
        """ Generates a number of valid/plausible geographical points and calls the pyxylookup API
            purpose is to verify capacity limit and to evaluate a viable chunck size
            note: if the values are invalid the API shall not be called, so we are forced
            to run basic lat lon checks before this one. """

        from random import uniform
        from time import time

        # Modify this to pass a different number of records to the API
        load = 1000

        rand_records = []

        for i in range(load):
            # Random points on Earth's surface at random depths
            lat = uniform(-90, 90)
            lon = uniform(-180, 180)
            depth = uniform(-300, 3000)

            rand_records.append({"id": i,
                                 "decimalLongitude": lon,
                                 "decimalLatitude": lat,
                                 "maximumDepthInMeters": depth,
                                 "QC": 0})

        # timing and calling the service
        start = time()
        results = location.check_xy(rand_records)
        print(f"Time elapsed: {time() - start}")
        print(results)
