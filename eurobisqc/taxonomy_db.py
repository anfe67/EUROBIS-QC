""" Replacing the taxonomy checks with verifications performed directly on
    the worms-db database (in SQLLite format in a first attempt)
    """
import re
import sys
import logging
from wormsdb import db_functions

from .util import qc_flags

# Masks used to build the return value when the quality check fails
error_mask_1 = qc_flags.QCFlag.TAXONOMY_APHIAID_MISS.bitmask  # Is the AphiaID Completed
error_mask_2 = qc_flags.QCFlag.TAXONOMY_RANK_LOW.bitmask  # Is the Taxon Level lower than the family

taxon_fields = []
speciesprofile_fields = []


# Move to utils - misc
def parse_lsid(s):
    m = re.search("^urn:lsid:marinespecies.org:taxname:([0-9]+)$", s)
    if m:
        return m.group(1)
    else:
        return None


# Retrieve fields from worms-db
def populate_fields(con):

    if db_functions.con is None :
        db_functions.con = db_functions.open_db()

    """ Populate the taxon_fields and speciesprofile_fields - only once
        from the worms database assumes con is an active connection to
        the database """

    sample_taxon = 'urn:lsid:marinespecies.org:taxname:519212'
    cur = db_functions.con.execute(f"SELECT * from taxon where scientificNameID='{sample_taxon}'")
    taxon_fields = [description[0] for description in cur.description]

    cur = db_functions.con.execute(f"SELECT * from speciesprofile where taxonID='{sample_taxon}'")
    speciesprofile_fields = [description[0] for description in cur.description]

    return taxon_fields, speciesprofile_fields


def check_record(record):

    # error mask
    qc = 0
    aphiaid = None
    query_possible = 0
    global taxon_fields, speciesprofile_fields

    # This is not applicable here
    key = (record["scientificName"] if "scientificName" in record else "") + "::" + (
        record["scientificNameID"] if "scientificNameID" in record else "")

    # Can we retrieve the aphiaID ? Should we do a consistency check ?
    if "scientificName" in record and record["scientificName"] is not None:
        query_possible +=1

    if "scientificNameID" in record and record["scientificNameID"] is not None:
        aphiaid = parse_lsid(record["scientificNameID"])
        query_possible +=1

    # We cannot query the DB, we stop here (no aphia, no name)
    if query_possible == 0:
        qc = error_mask_1
        return qc

    if "scientificNameID" in record and record["scientificNameID"] is not None:
        aphiaid = parse_lsid(record["scientificNameID"])

        # Have something to query
        if db_functions.con is None:
            db_functions.con = db_functions.open_db()

        if len(taxon_fields) == 0:
            taxon_fields, speciesprofile_fields = populate_fields(db_functions.con)

        # Verify that this is valid, then proceed for the other check verification
        if aphiaid is not None:
            # Can query DB with sientificNameID
            worms_record = db_functions.get_record(db_functions.con, 'taxon', 'scientificNameID',
                                                   record['scientificNameID'], taxon_fields)
            # Have we got a record
            if worms_record is not None:
                if worms_record['genus'] is None:
                    qc|=error_mask_2
            else:
                qc|=error_mask_1
        else:
            # Do not have aphia or correct scientificNameID
            qc |= error_mask_1
            # No Aphiaid Attempt to query by scientificName
            worms_record = db_functions.get_record(db_functions.con, 'taxon', 'scientificName',
                                                   record['scientificName'], taxon_fields)
            # Have we got a record
            if worms_record is not None:
                if worms_record['genus'] is None:
                    qc|=error_mask_2

    return qc



