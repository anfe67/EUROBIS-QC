from unittest import TestCase
from eurobisqc import taxonomy
from eurobisqc.util.qc_flags import QCFlag


class Test(TestCase):
    records = [
        {"id": 0, "scientificNameID": "urn:lsid:itis.gov:itis_tsn:28726"},  # Not in WORMS
        {"id": 1, "scientificName": "Orca gladiator"},  # No Scientific name but in DB there is at least Genus
        {"id": 2, "scientificName": "**non-current code** ??"},  # No scientific name
        {"id": 3, "scientificNameID": "urn:lsid:marinespecies.org:taxname:136980"},  # No Genus
        {"id": 4, "scientificNameID": "urn:lsid:marinespecies.org:taxname:136980"}, # No Genus repeat
    ]

    def test_check_taxa(self):
        results = taxonomy.check(self.records)
        print(results)
        check = [QCFlag.TAXONOMY_APHIAID_MISS.bitmask,
                 0,
                 QCFlag.TAXONOMY_APHIAID_MISS.bitmask,
                 QCFlag.TAXONOMY_RANK_LOW.bitmask,
                 QCFlag.TAXONOMY_RANK_LOW.bitmask,
                 ]
        self.assertTrue(results == check)
