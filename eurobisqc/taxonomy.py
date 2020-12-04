""" Taxonomy is checked in obis-qc
    Trying to wrap around and reuse the QC """
import logging
from obisqc import taxonomy
from obisqc.util import flags
from .util import qc_flags

logger = logging.getLogger(__name__)

# Return value when the quality check fails
error_mask_1 = qc_flags.QCFlag.TAXONOMY_APHIAID.encode()  # Is the AphiaID Completed
error_mask_2 = qc_flags.QCFlag.TAXONOMY_NOT_ENOUGH.encode()  # Is the Taxon Level lower than the family

""" Idea : Call the obis-qc taxonomy, get the taxa records and parse them to assign the QC field to the input records
    Shall process all the taxonomy QC in this one, shall take one or more records in a list of records.
    
    Record structure in results  

    {
        "id": record_id,
        "missing": taxon["missing"],        # MISSING FIELDS (TAXONOMY_1)
        "invalid": taxon["invalid"],         
        "flags": taxon["flags"],            # If Flag.NO_MATCH.value present, no APHIA could be retrieved. 
        "annotations": {
            "aphia": taxon["aphia"],
            "unaccepted": taxon["unaccepted"],
            "marine": taxon["marine"],
            "brackish": taxon["brackish"]
        },
        "dropped": taxon["dropped"]
    }


"""


def check_taxa(records, Cache=None):
    taxa_results = taxonomy.check(records, Cache)
    results = []

    # This could be wrong...
    for record, taxa_check in zip(records, taxa_results):
        qc_value = 0

        # Sanity check, I may be dead wrong in assuming they run in parallel
        if taxa_check['id'] == record['id']:

            # Did we get a match to an AphiaID ?
            if (flags.Flag.NO_MATCH.value in taxa_check['flags']):
                qc_value = error_mask_1

            # TODO: Determine if the Taxon level is lower than the family  (QC 3, bit 2)

            # Returns an array of QC values
            results.append(qc_value)

    return results
