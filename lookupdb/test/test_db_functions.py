import time
from unittest import TestCase
from lookupdb import db_functions


class Test(TestCase):
    taxon_fields = []
    speciesprofile_fields = []

    sample_sn_ids = ['urn:lsid:marinespecies.org:taxname:519212', 'urn:lsid:marinespecies.org:taxname:399249',
                     'urn:lsid:marinespecies.org:taxname:170605', '????????']
    semple_sns = ['Polymastia littoralis', 'Scorpaena cocosensis', 'Neoscopelarchoides', 'Pippo Pippo']

    def test_get_fields(self):
        # Open db connection
        con = db_functions.conn
        self.assertIsNotNone(con)

        sample_taxon = 'urn:lsid:marinespecies.org:taxname:519212'
        cur = con.execute(f"SELECT * from taxon where scientificNameID='{sample_taxon}'")
        self.taxon_fields = [description[0] for description in cur.description]

        self.assertTrue("scientificName" in self.taxon_fields)

        cur = con.execute(f"SELECT * from speciesprofile where taxonID='{sample_taxon}'")
        self.speciesprofile_fields = [description[0] for description in cur.description]

        self.assertTrue("isMarine" in self.speciesprofile_fields)


    def test_verify_querying(self):

        """ Verification of speed gain and querying / reconstructing the record structure
            of lookup-db """

        # Querying for scientificNameID
        start = time.time()
        for sn_id in self.sample_sn_ids:
            cur = db_functions.conn.execute(f"SELECT * from taxon where scientificNameID='{sn_id}'")

            taxon = cur.fetchone()
            fields = [description[0] for description in cur.description]

            record = None
            if taxon is not None:
                record = dict(zip(fields, taxon))
            print(record)
        print("************ WITH INDEX ************")
        print(f" ----> {time.time() - start}")
        print("************************************")

        # Just querying, no zipping
        start = time.time()
        for sn_id in self.sample_sn_ids:
            cur = db_functions.conn.execute(f"SELECT * from taxon where scientificNameID='{sn_id}'")
            taxon = cur.fetchone()
            print(taxon)
        print("************ WITHOUT ZIPPING ************")
        print(f" ----> {time.time() - start}")
        print("*****************************************")

        # Querying for scientificName
        start = time.time()
        for sn in self.semple_sns:
            cur = db_functions.conn.execute(f"SELECT * from taxon where scientificName='{sn}'")
            taxon = cur.fetchone()
            fields = [description[0] for description in cur.description]

            record = None
            if taxon is not None:
                record = dict(zip(fields, taxon))
            print(record)

        print("************ WITHOUT INDEX ************")
        print(f" ----> {time.time() - start}")
        print("***************************************")

        # Querying for speciesprofile
        for sn_id in self.sample_sn_ids:
            cur = db_functions.conn.execute(f"SELECT * from speciesprofile where taxonID='{sn_id}'")
            speciesprofile = cur.fetchone()
            fields = [description[0] for description in cur.description]
            record = None
            if speciesprofile is not None:
                record = dict(zip(fields, speciesprofile))
            print(record)

    def test_get_record(self):

        sample_taxon = 'urn:lsid:marinespecies.org:taxname:519212'
        cur = db_functions.conn.execute(f"SELECT * from taxon where scientificNameID='{sample_taxon}'")
        self.taxon_fields = [description[0] for description in cur.description]

        self.assertTrue("scientificName" in self.taxon_fields)

        cur = db_functions.conn.execute(f"SELECT * from speciesprofile where taxonID='{sample_taxon}'")
        self.speciesprofile_fields = [description[0] for description in cur.description]

        self.assertTrue("isMarine" in self.speciesprofile_fields)
        sn_id = self.sample_sn_ids[0]
        taxon = db_functions.get_record('taxon', 'scientificNameID', sn_id, self.taxon_fields)
        self.assertTrue(taxon['scientificNameID'] == sn_id)
        species_profile = db_functions.get_record('speciesprofile', 'taxonID', sn_id, self.speciesprofile_fields)
        self.assertTrue(species_profile['taxonID'] == sn_id)
