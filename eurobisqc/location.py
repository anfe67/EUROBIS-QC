import logging

from obisqc import location
from obisqc.util import flags
from .util import qc_flags

logger = logging.getLogger(__name__)

error_mask_1 = qc_flags.QCFlag.GEO_LAT_LON_MISSING.encode()
error_mask_2 = qc_flags.QCFlag.GEO_LAT_LON_INVALID.encode()


def check_record(record):
    """ A wrapper to obis-qc equivalent function, to assign bitmask """

    qc_mask = 0

    result = location.check_record(record)

    # Are decimal latitude or decimal longitude missing ?
    if 'decimalLongitude' in result['missing'] or 'decimalLongitude' in result['missing']:
        qc_mask |= error_mask_1

    # Are they valid ?
    if flags.Flag.LON_OUT_OF_RANGE.value in result['flags'] or flags.Flag.LAT_OUT_OF_RANGE.value in result['flags']:
        qc_mask |= error_mask_2

    return qc_mask


def check(records, xylookup=False):
    """ following the footstep of obis-qc, with rewrite for the xylookups portion """
    results = [location.check_record(record) for record in records]

    ## TODO XY LOOKUP TO BE DONE, using the same footprint of obis-qc
    """
    if xylookup:
        xy = util.misc.do_xylookup(results)
        assert(len(xy) == len(results))
        for i in range(len(results)):
            if xy[i] is not None:
                
                # check_xy(results[i], xy[i])  Needs to build an equivalent 
                pass 
            else:
                logger.warning("No xylookup result for %s" % results[i]["id"])
    """
    return results
