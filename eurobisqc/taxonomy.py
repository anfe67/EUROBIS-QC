""" Taxonomy is checked in obis-qc
    Trying to wrap around and reuse the QC """
import logging
from obisqc import taxonomy
from obisqc.util import flags
from .util import qc_flags

logger = logging.getLogger(__name__)

insufficient_detail = ['Kingdom', 'Subkingdom', 'Infrakingdom', 'Phylum', 'Subphylum', 'Infraphylum', 'Class', 'Order',
                       'Family']

# Return value when the quality check fails
error_mask_1 = qc_flags.QCFlag.TAXONOMY_APHIAID_MISS.bitmask  # Is the AphiaID Completed
error_mask_2 = qc_flags.QCFlag.TAXONOMY_RANK_LOW.bitmask  # Is the Taxon Level lower than the family

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
AF ---->    "aphia_info": taxon["aphia_info"]  # This is to verify that the Taxon is at least lower than the family             
        },
        "dropped": taxon["dropped"]
    }


"""

# Taxonomy depends on the worms service and it is a huge time eater. Cache should be used.

def check_taxa(records, Cache=None):
    """ Performs taxonomy verification on a list of record
        returns a list of qc bitmasks
        """

    taxa_results = taxonomy.check(records, Cache)
    results = []

    # This could be wrong...
    for record, taxa_check in zip(records, taxa_results):
        qc_value = 0

        # Sanity check, I may be wrong in assuming they run in parallel
        if taxa_check['id'] == record['id']:

            # Did we get a match to an AphiaID ?
            if flags.Flag.NO_MATCH.value in taxa_check['flags']:
                qc_value = error_mask_1

            if taxa_check[0]['annotations']['aphia_info'] is not None:
                aphia_info = taxa_check[0]['annotations']
                if aphia_info['record']['rank'] is not None:
                    if aphia_info['record']['rank'] in insufficient_detail:
                        qc_value |= error_mask_2

            results.append(qc_value)

    return results


def check(record):
    """ Taxonomy check for a single record, returns a bitmask """

    taxa_results = taxonomy.check([record])
    qc_value = 0
    # Did we get a match to an AphiaID ?
    if flags.Flag.NO_MATCH.value in taxa_results[0]['flags']:
        qc_value |= error_mask_1

    if taxa_results[0]['annotations']['aphia_info'] is not None:
        aphia_info = taxa_results[0]['annotations']['aphia_info']
        if aphia_info['record']['rank'] is not None:
            if aphia_info['record']['rank'] in insufficient_detail:
                qc_value |= error_mask_2
        # What do we do if it is None ?
    return qc_value
