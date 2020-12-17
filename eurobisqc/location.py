""" The module contains several functions to implement the QCs for various types of
    records. The order in which they are called has to make sense, as it makes sense
    to perform basic checks (lat lon presence for instance) before calling the pxylookup
    to verify if the point is on land.
    """
import logging

from .util import qc_flags
from .util import misc

logger = logging.getLogger(__name__)

error_mask_4 = qc_flags.QCFlag.GEO_LAT_LON_MISSING.bitmask
error_mask_5 = qc_flags.QCFlag.GEO_LAT_LON_INVALID.bitmask

# Need external call to xylookup
error_mask_6 = qc_flags.QCFlag.GEO_LAT_LON_NOT_SEA.bitmask  # TODO

# Need to verify if lat, lon are in specific area (assume rectangle)
error_mask_9 = qc_flags.QCFlag.GEO_COORD_AREA.bitmask

# are the dephts coherent
error_mask_18 = qc_flags.QCFlag.MIN_MAX_DEPTH_ERROR.bitmask

# Need external call to xylookup or bathymetry service
error_mask_19 = qc_flags.QCFlag.WRONG_DEPTH_MAP.bitmask  # TODO

# Possible to retrieve this info in aphia ? So this may be moved to taxonomy
error_mask_20 = qc_flags.QCFlag.WRONG_DEPTH_SPECIES.bitmask  # TODO


def check_basic_record(record):
    """ obis-qc equivalent function, to assign bitmask
        for basic lat/lon validity / presence and
        also to check that the depth is consistent """

    qc_mask = 0

    # Are decimal latitude or decimal longitude missing ?
    if 'decimalLongitude' not in record or 'decimalLongitude' not in record:
        qc_mask |= error_mask_4
    else:
        # Are they valid ?
        result = misc.check_float(record['decimalLongitude'], [-180, 180])
        result2 = misc.check_float(record['decimalLatitude'], [-90, 90])
        if not result["valid"] or not result2["valid"]:
            qc_mask |= error_mask_5

    # Depths - consistency
    qc_mask |= check_depth_consistent(record)
    return qc_mask

def check_basic(records):
    return [check_basic_record(record) for record in records]

def check_record_in_area(record, area):
    """ verifies that a geographical point is in a the rectangle area
        :param record: The event record
        :param area: The geographical area - 2 segments east west and north south
        as [(east,west), (north,south)]
        This QC makes sense AFTER Lon and Lat decimal have been verified present and valid
        Assumption: Area is rectangular """

    qc = 0

    # Region boundaries
    if area is not None:
        east = area[0][0]
        west = area[0][1]
        north = area[1][0]
        south = area[1][1]
    else:
        return qc

    # extracting from record
    if 'decimalLongitude' in record and 'decimalLatitude' in record:
        if misc.is_number(record['decimalLongitude']) and misc.is_number(record['decimalLatitude']):

            point_x = float(record['decimalLongitude'])
            point_y = float(record['decimalLatitude'])

            if not (west <= point_x <= east) or not (south <= point_y <= north):
                qc |= error_mask_9

    return qc

def check_in_area(records, area):
    """ verifies that a geographical point is in a the rectangle area
        :param records: The records to check
        :param area: The geographical area - 2 segments east west and north south
        as [(east,west), (north,south)]
        NOTE: This QC makes sense AFTER Lon and Lat decimal have been verified present and valid
        Assumption: Area is rectangular """

    results = []

    # Region boundaries
    if area is not None:
        east = area[0][0]
        west = area[0][1]
        north = area[1][0]
        south = area[1][1]
    else:
        return [0 for record in records]

    # extracting from record
    for record in records:
        qc =0
        if 'decimalLongitude' in record and 'decimalLatitude' in record:
            if misc.is_number(record['decimalLongitude']) and misc.is_number(record['decimalLatitude']):

                point_x = float(record['decimalLongitude'])
                point_y = float(record['decimalLatitude'])

                if not (west <= point_x <= east) or not (south <= point_y <= north):
                    qc |= error_mask_9
        results.append(qc)

    return results


def check_depth_consistent(record):
    """ depth checks, in this case they must be numbers (representing meters)
        it is used as part of the basic checks """

    qc = 0
    min_depth = 0
    max_depth = 0

    if "minimumDepthInMeters" in record and record["minimumDepthInMeters"] is not None:
        if misc.is_number(record["minimumDepthInMeters"]):
            min_depth = float(record["minimumDepthInMeters"])
        else:
            qc |= error_mask_18
    else:
        # No point checking, minimum depth is not there
        return qc

    if "maximumDepthInMeters" in record and record["maximumDepthInMeters"] is not None:
        if misc.is_number(record["maximumDepthInMeters"]):
            max_depth = float(record["maximumDepthInMeters"])
        else:
            qc |= error_mask_18
    else:
        # No point checking, minimum depth is not there
        return qc

    if min_depth > max_depth:
        qc |= error_mask_18

    return qc


def check_xy(records):
    """ :param records, already QC for location
        :returns qc values, but QC is already inserted in records bitmasks
        however, the records shall be augmented with the QC for 2 flags:
        GEO_LAT_LON_NOT_SEA and WRONG_DEPTH_MAP """

    xy_res = misc.do_xylookup(records)

    intercept = 50
    slope = 1.1

    results = []

    # Ensuring about the size of the results
    # To verofy, we would not like to crash anyway
    assert (len(xy_res) == len(records))

    for i in range(len(records)):

        qc = 0

        if xy_res[i] is not None:
            # verify that records[i] does comply: point not on land and bathymetry is correct.
            # We MUST have checked already for depth validity
            xy = xy_res[i]
            record = records[i]
            # Check bathymetry
            if "QC" in record and not (record["QC"] & error_mask_18):
                for depth_field in ["minimumDepthInMeters", "maximumDepthInMeters"]:
                    if depth_field in record and "bathymetry" in xy["grids"]:
                        if xy["grids"]["bathymetry"] < 0:
                            # We can do this because error mask is not set (FLAG: THIS NEEDS TO BE VERIFIED!!)
                            if float(record[depth_field]) > intercept + xy["grids"]["bathymetry"]:
                                qc |= error_mask_19
                        else:
                            if record[depth_field] > intercept + xy["grids"]["bathymetry"] * slope:
                                qc |= error_mask_19

            # Check point on land
            if "QC" in record and not (record["QC"] & error_mask_5) and not (record["QC"] & error_mask_4):
                if xy["shoredistance"] < 0:
                    qc |= error_mask_6

            # Note: the qc_flag is already added to the record
            if "QC" in record:
                record["QC"] |= qc
            else:
                record["QC"] = qc
            results.append(qc)
        else:
            if "QC" not in records[i]:
                records[i]["QC"] = 0

            results.append(0)
            logger.warning("No xylookup result for %s" % records[i]["id"])

    return results
