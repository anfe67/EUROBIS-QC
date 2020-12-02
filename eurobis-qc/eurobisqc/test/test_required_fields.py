from unittest import TestCase
from .. import required_fields


class Test(TestCase):
    records = [
        {"id": 0}, # No fields
        {"id": 1, "eventDate": "1969-06-11", "decimalLongitude": 32.4, "decimalLatitude": 1.0, "scientificName":
            "Zooplankton", "scientificNameID": "urn:lsid:marinespecies.org:taxname:1",
            "occurrenceStatus": "present","basisOfRecord": "MaterialSample"}, # All fields
        {"id": 2, "eventDate": "1969-06-11", "decimalLongitude": 32.4, "decimalLatitude": 1.0, "scientificName":
            "Zooplankton", "occurrenceStatus": "present","basisOfRecord": "MaterialSample"}, # Some fields
        {"id": 3, "basisOfRecord": "human observation"} # Another with not so many fields
    ]
    def test_check_record(self):
        self.assertTrue(required_fields.check_record(self.records[0]) == 1)
        self.assertTrue(required_fields.check_record(self.records[1]) == 0)
        self.assertTrue(required_fields.check_record(self.records[2]) == 1)
        self.assertTrue(required_fields.check_record(self.records[3]) == 1)


    def test_check(self):
        # Comparison is OK as we want to see element by element
        self.assertTrue(required_fields.check(self.records) == [1,0,1,1])


