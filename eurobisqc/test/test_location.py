from unittest import TestCase
from eurobisqc import location


class Test(TestCase):
    records = [
        {"id": 0, "decimalLongitude": 2.5, "decimalLatitude": 52.2},  # OK Record
        {"id": 1},  # Missing Fields
        {"id": 2, "decimalLongitude": None, "decimalLatitude": 52.2},  # None Field (Out of Range)
        {"id": 3, "decimalLongitude": 182.5, "decimalLatitude": -92.2}  # Out of range
    ]

    def test_check_record(self):
        results = []

        for record in self.records:
            results.append(location.check_record(record))

        assert (results == [0, 8, 16, 16])
