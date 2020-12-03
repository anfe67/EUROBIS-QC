from unittest import TestCase
from .. import required_fields


class Test(TestCase):
    records = [
        {"id": 0},  # No fields
        {"id": 1, "eventDate": "1969-06-11", "decimalLongitude": 32.4, "decimalLatitude": 1.0, "scientificName":
            "Zooplankton", "scientificNameID": "urn:lsid:marinespecies.org:taxname:1",
         "occurrenceStatus": "present", "basisOfRecord": "MaterialSample"},  # All fields
        {"id": 2, "eventDate": "1969-06-11", "decimalLongitude": 32.4, "decimalLatitude": 1.0, "scientificName":
            "Zooplankton", "occurrenceStatus": "present", "basisOfRecord": "MaterialSample"},  # Some fields
        {"id": 3, "basisOfRecord": "human observation"},  # Another with not so many fields
        {"id": "Het Zwin (Knokke)_9_9_5", "basisOfRecord": "MaterialSample",
         "occurrenceID": "Het Zwin (Knokke)_9_9_5_6_absent", "occurrenceStatus": "absent",
         "eventID": "Het Zwin (Knokke)_9_9_5", "scientificName": None},  # Scientific Name is None
        {"id": "Het Zwin (Knokke)_9_9_5", "basisOfRecord": "Materample",
         "occurrenceID": "Het Zwin (Knokke)_9_9_5_5_absent", "occurrenceStatus": "absent",
         "eventID": "Het Zwin (Knokke)_9_9_5", "scientificName": "Syrphu balteatu"
         },  # Source record wrong basisOfRecord
        {"id": "Het Zwin (Knokke)_9_9_5", "occurrenceID": "Het Zwin (Knokke)_9_9_5_5_absent",
         "occurrenceStatus": "absent", "eventID": "Het Zwin (Knokke)_9_9_5", "scientificName": "Syrphu balteatu"
         },  # Source record no basisOfRecord
        {"id": 4, "eventDate": "1969-06-11", "decimalLongitude": 32.4, "decimalLatitude": 1.0, "scientificName":
            "Zooplankton", "scientificNameID": "urn:lsid:marinespecies.org:taxname:1",
         "occurrenceStatus": "present", "basisOfRecord": "materialsample"},
        # All fields with lowercase value for BasisOfRecord
    ]

    def test_check_record(self):
        self.assertTrue(required_fields.check_record(self.records[0]) == 1)
        self.assertTrue(required_fields.check_record(self.records[1]) == 0)
        self.assertTrue(required_fields.check_record(self.records[2]) == 1)
        self.assertTrue(required_fields.check_record(self.records[3]) == 1)
        self.assertTrue(required_fields.check_record(self.records[7]) == 0)

    def test_source_record(self):
        # Source Records
        self.assertTrue(required_fields.check_source_record(self.records[4]) == 0)
        self.assertTrue(required_fields.check_source_record(self.records[5]) == 1)
        self.assertTrue(required_fields.check_source_record(self.records[6]) == 1)

    def test_check_source_records(self):
        self.assertTrue(required_fields.check_source_records(self.records[4:]) == [0, 1, 1, 0])

    def test_check(self):
        # Comparison is OK as we want to see element by element
        self.assertTrue(required_fields.check(self.records[0:4]) == [1, 0, 1, 1])
