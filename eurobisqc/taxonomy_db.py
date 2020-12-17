""" Replacing the taxonomy checks with verifications performed directly on
    the lookup-db database (in SQLLite format in a first attempt)
    """
from lookupdb import db_functions
from .util import qc_flags, misc

# Masks used to build the return value when the quality check fails
error_mask_1 = qc_flags.QCFlag.TAXONOMY_APHIAID_MISS.bitmask  # Is the AphiaID Completed
error_mask_2 = qc_flags.QCFlag.TAXONOMY_RANK_LOW.bitmask  # Is the Taxon Level lower than the family
# error_mask_8 = qc_flags.QCFlag.TAXON_APHIAID_NOT_EXISTING. bitmask # Unclear how to do this one

taxon_fields = []
speciesprofile_fields = []


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
    taxon_fields.extend(taxons)
    cur = db_functions.conn.execute(f"SELECT * from speciesprofile where taxonID='{sample_taxon}'")
    speciesprofiles = [description[0] for description in cur.description]
    speciesprofile_fields.extend(speciesprofiles)


# Rework
def check_record(record):
    # error mask
    qc = 0
    sn_id = 0  # To mark whether the scientificNameID is valid

    # Can we retrieve the aphiaID with scientificNameID?
    if "scientificNameID" in record and record["scientificNameID"] is not None:

        # Have something to query
        if db_functions.conn is None:
            db_functions.open_db()

        if len(taxon_fields) == 0:
            populate_fields()

        # Can query DB with sientificNameID
        aphiaid = misc.parse_lsid(record["scientificNameID"])

        if aphiaid is not None:  # Verify that the aphiaid retrieved is valid
            worms_record = db_functions.get_record('taxon', 'scientificNameID',
                                                   record['scientificNameID'], taxon_fields)

            # Have we got a record
            if worms_record is not None:
                if worms_record['genus'] is None:
                    qc |= error_mask_2
            else:
                sn_id |= error_mask_1  # Got some info but not found in DB. so scientificNameID is not OK
        else:
            sn_id |= error_mask_1
    else:
        sn_id |= error_mask_1

    if sn_id:  # We still have a chance to verify by scientificName

        # No Aphiaid Attempt to query by scientificName
        if "scientificName" in record and record["scientificName"] is not None:

            # Have something to query upon
            if db_functions.conn is None:
                db_functions.open_db()

            worms_record = db_functions.get_record('taxon', 'scientificName',
                                                   record['scientificName'], taxon_fields)
            # Have we got a record
            if worms_record is not None:
                if worms_record['genus'] is None:
                    qc |= error_mask_2
            else:
                qc |= error_mask_1  # both fields are wrong...
        else:
            qc |= error_mask_1  # None of the scientificName fields are filled or valid

    return qc


def check(records):
    """ Checks a list of records for taxonomy """
    if db_functions.conn is None:
        db_functions.open_db()
    results = [check_record(record) for record in records]
    db_functions.close_db()
    return results
