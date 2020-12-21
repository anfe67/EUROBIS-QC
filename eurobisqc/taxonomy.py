""" Replacing the taxonomy checks with verifications performed directly on
    the lookup-db database (in SQLLite format in a first attempt)
    """
import sys
from lookupdb import db_functions

from eurobisqc.util import qc_flags
from eurobisqc.util import misc

this = sys.modules[__name__]

# Masks used to build the return value when the quality check fails
error_mask_2 = qc_flags.QCFlag.TAXONOMY_APHIAID_MISS.bitmask  # Is the AphiaID Completed
error_mask_3 = qc_flags.QCFlag.TAXONOMY_RANK_LOW.bitmask  # Is the Taxon Level lower than the family

# error_mask_8 = qc_flags.QCFlag.TAXON_APHIAID_NOT_EXISTING. bitmask # Unclear how to do this one

this.taxon_fields = []
this.speciesprofile_fields = []


# Retrieve fields from lookup-db, call it only once, open the DB in advance
def populate_fields():
    """ Populate the taxon_fields and speciesprofile_fields - only once
        from the worms database assumes con is an active connection to
        the database """

    if db_functions.conn is None:
        return

    # Used for populating the field names
    sample_taxon = 'urn:lsid:marinespecies.org:taxname:519212'
    cur = db_functions.conn.execute(f"SELECT * from taxon where scientificNameID='{sample_taxon}'")
    taxons = [description[0] for description in cur.description]
    this.taxon_fields.extend(taxons)
    cur = db_functions.conn.execute(f"SELECT * from speciesprofile where taxonID='{sample_taxon}'")
    speciesprofiles = [description[0] for description in cur.description]
    this.speciesprofile_fields.extend(speciesprofiles)


# Rework
def check_record(record):
    # error mask
    qc = 0
    sn_id = 0  # To mark whether the scientificNameID is valid

    # Can we retrieve the aphiaID with scientificNameID?
    if "scientificNameID" in record and record["scientificNameID"] is not None:

        # Have something to query
        if len(this.taxon_fields) == 0:
            populate_fields()

        # Can query DB with sientificNameID
        aphiaid = misc.parse_lsid(record["scientificNameID"])

        if aphiaid is not None:  # Verify that the aphiaid retrieved is valid
            taxon_record = db_functions.get_record('taxon', 'scientificNameID',
                                                   record['scientificNameID'], this.taxon_fields)

            # Have we got a record
            if taxon_record is not None:
                if taxon_record['genus'] is None:
                    qc |= error_mask_3
            else:
                sn_id |= error_mask_2  # Got some info but not found in DB. so scientificNameID is not OK
        else:
            sn_id |= error_mask_2
    else:
        sn_id |= error_mask_2

    if sn_id:  # We still have a chance to verify by scientificName

        # No Aphiaid Attempt to query by scientificName
        if "scientificName" in record and record["scientificName"] is not None:

            # Have something to query
            if len(this.taxon_fields) == 0:
                populate_fields()

            # Have something to query upon
            taxon_record = db_functions.get_record('taxon', 'scientificName',
                                                   record['scientificName'], this.taxon_fields)
            # Have we got a record
            if taxon_record is not None:
                if taxon_record['genus'] is None:
                    # We would not be here if scientificNameID was able to resolve
                    qc |= error_mask_3
            else:
                qc |= error_mask_2  # both fields are wrong...
        else:
            qc |= error_mask_2  # None of the scientificName fields are filled or valid

    else:
        pass  # We have already an aphiaid from the scientificNameId

    return qc


def check(records):
    """ Checks a list of records for taxonomy """

    # Ensure DB is available
    if db_functions.conn is None:
        db_functions.open_db()  # It shall be closed on exit

    results = [check_record(record) for record in records]
    return results
