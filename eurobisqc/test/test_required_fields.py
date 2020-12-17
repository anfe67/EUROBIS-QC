from unittest import TestCase
from eurobisqc import required_fields
from eurobisqc.util.qc_flags import QCFlag


# TODO - Re-allign to the class being tested
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
        self.assertTrue(required_fields.check_record_required(self.records[0]) == QCFlag.REQUIRED_FIELDS_MISS.bitmask)
        self.assertTrue(required_fields.check_record_required(self.records[1]) == 0)
        self.assertTrue(required_fields.check_record_required(self.records[2]) == QCFlag.REQUIRED_FIELDS_MISS.bitmask)
        self.assertTrue(required_fields.check_record_required(self.records[3]) == QCFlag.REQUIRED_FIELDS_MISS.bitmask)
        self.assertTrue(required_fields.check_record_required(self.records[7]) == 0)

    def test_source_record(self):
        # Source Records
        self.assertTrue(required_fields.check_record_obis_format(self.records[4]) == 0)
        self.assertTrue(required_fields.check_record_obis_format(self.records[5]) == QCFlag.NO_OBIS_DATAFORMAT.bitmask)
        self.assertTrue(required_fields.check_record_obis_format(self.records[6]) == QCFlag.NO_OBIS_DATAFORMAT.bitmask)

    def test_check(self):
        # Comparison is OK as we want to see element by element
        self.assertTrue(required_fields.check_required(self.records[0:4]) == [QCFlag.REQUIRED_FIELDS_MISS.bitmask,
                                                                              0,
                                                                              QCFlag.REQUIRED_FIELDS_MISS.bitmask,
                                                                              QCFlag.REQUIRED_FIELDS_MISS.bitmask])
        self.assertTrue(required_fields.check_obis(self.records[0:4]) == [QCFlag.NO_OBIS_DATAFORMAT.bitmask,
                                                                          0,
                                                                          0,
                                                                          QCFlag.NO_OBIS_DATAFORMAT.bitmask])
