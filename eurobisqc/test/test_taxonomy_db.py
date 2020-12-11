from unittest import TestCase
from eurobisqc import taxonomy_db


class Test(TestCase):
    records = [
        {"id": 0, "scientificNameID": "urn:lsid:itis.gov:itis_tsn:28726"},  # Not in WORMS
        {"id": 1, "scientificName": "Orca gladiator"},  # No Scientific name but in DB there is at least Genus
        {"id": 2, "scientificName": "**non-current code** ??"},  # No scientific name
        {"id": 3, "scientificNameID": "urn:lsid:marinespecies.org:taxname:136980"}  # No Genus
    ]

    def test_check_taxa(self):
        results = taxonomy_db.check(self.records)
        assert (results == [2, 0, 2, 4])
