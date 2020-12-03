from unittest import TestCase
from .. import taxonomy


class Test(TestCase):
    records = [
        {"id": 0, "scientificNameID": "urn:lsid:itis.gov:itis_tsn:28726"},
        {"id": 1, "scientificName": "Orca gladiator"},
        {"id": 2, "scientificName": "**non-current code** ??"},
        {"id": 3, "scientificNameID": "urn:lsid:marinespecies.org:taxname:136980"}
    ]

    def test_check_taxa(self):
        results = taxonomy.check_taxa(self.records)
        assert (results == [2, 0, 2, 0])
