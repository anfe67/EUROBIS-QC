import sys
import logging

import time
from unittest import TestCase
from dbworks import sqlite_db_functions

this = sys.modules[__name__]
this.logger = logging.getLogger(__name__)
this.logger.setLevel(logging.DEBUG)
this.logger.addHandler(logging.StreamHandler())

class Test(TestCase):
    taxon_fields = []
    speciesprofile_fields = []

    sample_sn_ids = ['urn:lsid:marinespecies.org:taxname:519212', 'urn:lsid:marinespecies.org:taxname:399249',
                     'urn:lsid:marinespecies.org:taxname:170605', '????????']
    semple_sns = ['Polymastia littoralis', 'Scorpaena cocosensis', 'Neoscopelarchoides', 'Pippo Pippo']

    conn = sqlite_db_functions.open_db()

    def test_get_fields(self):

        # Open db connection
        self.assertIsNotNone(self.conn)

        sample_taxon = 'urn:lsid:marinespecies.org:taxname:519212'
        cur = self.conn.execute(f"SELECT * from taxon where scientificNameID='{sample_taxon}'")
        self.taxon_fields = [description[0] for description in cur.description]

        self.assertTrue("scientificName" in self.taxon_fields)

        cur = self.conn.execute(f"SELECT * from speciesprofile where taxonID='{sample_taxon}'")
        self.speciesprofile_fields = [description[0] for description in cur.description]

        self.assertTrue("isMarine" in self.speciesprofile_fields)

    def test_verify_querying(self):

        """ Verification of speed gain and querying / reconstructing the record structure
            of lookup-db """

        # Querying for scientificNameID
        start = time.time()
        for sn_id in self.sample_sn_ids:
            cur = self.conn.execute(f"SELECT * from taxon where scientificNameID='{sn_id}'")

            taxon = cur.fetchone()
            fields = [description[0] for description in cur.description]

            record = None
            if taxon is not None:
                record = dict(zip(fields, taxon))
            this.logger.info(record)
        this.logger.info("************ WITH INDEX ************")
        this.logger.info(f" ----> {time.time() - start}")
        this.logger.info("************************************")

        # Just querying, no zipping
        start = time.time()
        for sn_id in self.sample_sn_ids:
            cur = self.conn.execute(f"SELECT * from taxon where scientificNameID='{sn_id}'")
            taxon = cur.fetchone()
            this.logger.info(taxon)
        this.logger.info("************ WITHOUT ZIPPING ************")
        this.logger.info(f" ----> {time.time() - start}")
        this.logger.info("*****************************************")

        # Querying for scientificName
        start = time.time()
        for sn in self.semple_sns:
            cur = self.conn.execute(f"SELECT * from taxon where scientificName='{sn}'")
            taxon = cur.fetchone()
            fields = [description[0] for description in cur.description]

            record = None
            if taxon is not None:
                record = dict(zip(fields, taxon))
            this.logger.info(record)

        this.logger.info("************ WITHOUT INDEX ************")
        this.logger.info(f" ----> {time.time() - start}")
        this.logger.info("***************************************")

        # Querying for speciesprofile
        for sn_id in self.sample_sn_ids:
            cur = self.conn.execute(f"SELECT * from speciesprofile where taxonID='{sn_id}'")
            speciesprofile = cur.fetchone()
            fields = [description[0] for description in cur.description]
            record = None
            if speciesprofile is not None:
                record = dict(zip(fields, speciesprofile))
            this.logger.info(record)

    def test_get_record(self):

        sample_taxon = 'urn:lsid:marinespecies.org:taxname:519212'
        cur = self.conn.execute(f"SELECT * from taxon where scientificNameID='{sample_taxon}'")
        self.taxon_fields = [description[0] for description in cur.description]

        self.assertTrue("scientificName" in self.taxon_fields)

        cur = self.conn.execute(f"SELECT * from speciesprofile where taxonID='{sample_taxon}'")
        self.speciesprofile_fields = [description[0] for description in cur.description]

        self.assertTrue("isMarine" in self.speciesprofile_fields)
        sn_id = self.sample_sn_ids[0]
        taxon = sqlite_db_functions.get_record('taxon', 'scientificNameID', sn_id, self.taxon_fields)
        self.assertTrue(taxon['scientificNameID'] == sn_id)
        species_profile = sqlite_db_functions.get_record('speciesprofile', 'taxonID', sn_id, self.speciesprofile_fields)
        self.assertTrue(species_profile['taxonID'] == sn_id)
