import logging

from obisqc import location
from obisqc.util import flags
from .util import qc_flags
from .util import misc

logger = logging.getLogger(__name__)

error_mask_4 = qc_flags.QCFlag.GEO_LAT_LON_MISSING.bitmask
error_mask_5 = qc_flags.QCFlag.GEO_LAT_LON_INVALID.bitmask

# Need external call to xylookup
error_mask_6 = qc_flags.QCFlag.GEO_LAT_LON_NOT_SEA.bitmask

# Need to verify if lat, lon are in specific area (assume rectangle)
error_mask_9 = qc_flags.QCFlag.GEO_COORD_AREA.bitmask

error_mask_17 = qc_flags.QCFlag.MIN_MAX_DEPTH_ERROR.bitmask

# Need external call to xylookup or bathymetry service
error_mask_18 = qc_flags.QCFlag.WRONG_DEPTH_MAP.bitmask

# Possible to retrieve this info in aphia ? So this may be moved to taxonomy
error_mask_19 = qc_flags.QCFlag.WRONG_DEPTH_SPECIES.bitmask


def check_record(record):
    """ A wrapper to obis-qc equivalent function, to assign bitmask """

    qc_mask = 0

    result = location.check_record(record)

    # Are decimal latitude or decimal longitude missing ?
    if 'decimalLongitude' in result['missing'] or 'decimalLongitude' in result['missing']:
        qc_mask |= error_mask_4

    # Are they valid ?
    if flags.Flag.LON_OUT_OF_RANGE.value in result['flags'] or flags.Flag.LAT_OUT_OF_RANGE.value in result['flags']:
        qc_mask |= error_mask_5

    # Depths: Use results from obisqc if possible 

    return qc_mask


def check(records, xylookup=False):
    """ following the footstep of obis-qc, with rewrite for the xylookups portion """

    results = [location.check_record(record) for record in records]

    # TODO XY LOOKUP TO BE DONE, using the same footprint of obis-qc
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


def check_record_in_area(record, area):
    """ verifies that a geographical point is in a the rectangle area
        :param record: The event record
        :param area: The geographical area - 2 segments east west and north south
        as [(east,west), (north,south)]
        This QC makes sense AFTER Lon and Lat decimal have been verified present and valid
        Assumption: Area is rectangular """

    qc = 0

    # Region boundaries
    east = area[0][0]
    west = area[0][1]
    north = area[1][0]
    south = area[1][1]

    # extracting from record
    if 'decimalLongitude' in record and 'decimalLatitude' in record:
        if misc.is_number(record['decimalLongitude']) and misc.is_number(record['decimalLatitude']):

            point_x = float(record['decimalLongitude'])
            point_y = float(record['decimalLatitude'])

            if not (west <= point_x <= east) or not (south <= point_y <= north):
                qc |= error_mask_9

    return qc
