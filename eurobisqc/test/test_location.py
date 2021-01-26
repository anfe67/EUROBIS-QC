import sys
import logging
from unittest import TestCase

from eurobisqc.util import qc_flags
from eurobisqc import location
from eurobisqc.util.qc_flags import QCFlag

this = sys.modules[__name__]
this.logger = logging.getLogger(__name__)
this.logger.setLevel(logging.DEBUG)
this.logger.addHandler(logging.StreamHandler())


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

    # Dictionary area
    single_area = [{"east": 10.0, "west": 2.0, "north": 54.0, "south": 52.0}]

    # list of areas
    more_areas = [{"east": 10.0, "west": 2.0, "north": 54.0, "south": 52.0},
                  {"east": 16.0, "west": 10.0, "north": 54.0, "south": 34.0},
                  {"east": 100, "west": -150, "north": 0.5, "south": -20.0}]

    def test_check_record(self):
        """ tests regular lat lon verifications """

        results = []

        for record in self.records:
            results.append(location.check_basic_record(record))

        assert (results == [QCFlag.GEO_LAT_LON_PRESENT.bitmask | QCFlag.GEO_LAT_LON_VALID.bitmask,
                            0,
                            0,
                            0,
                            QCFlag.GEO_LAT_LON_PRESENT.bitmask | QCFlag.GEO_LAT_LON_VALID.bitmask,
                            QCFlag.GEO_LAT_LON_PRESENT.bitmask | QCFlag.GEO_LAT_LON_VALID.bitmask,
                            QCFlag.GEO_LAT_LON_PRESENT.bitmask | QCFlag.GEO_LAT_LON_VALID.bitmask,
                            QCFlag.GEO_LAT_LON_PRESENT.bitmask | QCFlag.GEO_LAT_LON_VALID.bitmask,
                            QCFlag.GEO_LAT_LON_PRESENT.bitmask | QCFlag.GEO_LAT_LON_VALID.bitmask, ])

    def test_check_xy(self):
        """ tests calls to the lookup service through pyxylookup """

        # first get the QC done
        for record in self.records:
            record["QC"] = location.check_basic_record(record)

        # This should call the pyxylookup and change the records, also assessing the
        results = location.check_xy(self.records)
        this.logger.info(results)

        assert (results == [QCFlag.GEO_LAT_LON_ON_SEA.bitmask,
                            0,
                            0,
                            0,
                            0,
                            0,
                            QCFlag.GEO_LAT_LON_ON_SEA.bitmask | QCFlag.DEPTH_MAP_VERIFIED.bitmask,
                            QCFlag.GEO_LAT_LON_ON_SEA.bitmask,
                            QCFlag.GEO_LAT_LON_ON_SEA.bitmask | QCFlag.DEPTH_MAP_VERIFIED.bitmask,
                            ])

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
        this.logger.info(f"Time elapsed: {time() - start}")
        this.logger.info(results)

    def test_areas(self):
        """ Tests to verify LAT/LON in areas """

        res_1 = location.check_record_in_areas(self.records[0], self.single_area)

        area_check_records = []
        for record in self.records:
            if location.check_basic_record(record):
                area_check_records.append(record)

        res_2 = location.check_in_areas(area_check_records, self.more_areas)

        assert (res_1 == QCFlag.GEO_COORD_AREA.bitmask)
        assert (res_2 == [QCFlag.GEO_COORD_AREA.bitmask,
                          0,
                          0,
                          QCFlag.GEO_COORD_AREA.bitmask,
                          QCFlag.GEO_COORD_AREA.bitmask,
                          QCFlag.GEO_COORD_AREA.bitmask])

    def test_all_params(self):
        qc_res = location.check_all_location_params(self.records, self.more_areas)

        for idx, record in enumerate(self.records):
            if "QC" in record:
                if qc_res[idx] is not None:
                    record["QC"] |= qc_res[idx]
            else:
                record["QC"] = qc_res[idx]

        assert (qc_res == [qc_flags.QCFlag.GEO_LAT_LON_VALID.bitmask |
                           qc_flags.QCFlag.GEO_LAT_LON_PRESENT.bitmask |
                           qc_flags.QCFlag.GEO_LAT_LON_ON_SEA.bitmask |
                           qc_flags.QCFlag.GEO_COORD_AREA.bitmask,
                           0,
                           0,
                           0,
                           qc_flags.QCFlag.GEO_LAT_LON_VALID.bitmask |
                           qc_flags.QCFlag.GEO_LAT_LON_PRESENT.bitmask,
                           qc_flags.QCFlag.GEO_LAT_LON_VALID.bitmask |
                           qc_flags.QCFlag.GEO_LAT_LON_PRESENT.bitmask,
                           qc_flags.QCFlag.GEO_LAT_LON_VALID.bitmask |
                           qc_flags.QCFlag.GEO_LAT_LON_PRESENT.bitmask |
                           qc_flags.QCFlag.GEO_LAT_LON_ON_SEA.bitmask |
                           qc_flags.QCFlag.GEO_COORD_AREA.bitmask |
                           qc_flags.QCFlag.DEPTH_MAP_VERIFIED.bitmask,
                           qc_flags.QCFlag.GEO_LAT_LON_VALID.bitmask |
                           qc_flags.QCFlag.GEO_LAT_LON_PRESENT.bitmask |
                           qc_flags.QCFlag.GEO_LAT_LON_ON_SEA.bitmask |
                           qc_flags.QCFlag.GEO_COORD_AREA.bitmask,
                           qc_flags.QCFlag.GEO_LAT_LON_VALID.bitmask |
                           qc_flags.QCFlag.GEO_LAT_LON_PRESENT.bitmask |
                           qc_flags.QCFlag.GEO_LAT_LON_ON_SEA.bitmask |
                           qc_flags.QCFlag.GEO_COORD_AREA.bitmask |
                           qc_flags.QCFlag.DEPTH_MAP_VERIFIED.bitmask,
                           ])
