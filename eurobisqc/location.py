""" The module contains several functions to implement the QCs for various types of
    records. The order in which they are called has to make sense, as it makes sense
    to perform basic checks (lat lon presence for instance) before calling the pxylookup
    to verify if the point is on land.
    """
from eurobisqc.util import qc_flags
from eurobisqc.util import misc

qc_mask_4 = qc_flags.QCFlag.GEO_LAT_LON_PRESENT.bitmask
qc_mask_5 = qc_flags.QCFlag.GEO_LAT_LON_VALID.bitmask

# Call to xylookup
qc_mask_6 = qc_flags.QCFlag.GEO_LAT_LON_ON_SEA.bitmask

# Need to verify if lat, lon are in specific area (assume areas are rectangles)
qc_mask_9 = qc_flags.QCFlag.GEO_COORD_AREA.bitmask

# are the dephts coherent
qc_mask_18 = qc_flags.QCFlag.MIN_MAX_DEPTH_VERIFIED.bitmask

# Within the call to xylookup
qc_mask_19 = qc_flags.QCFlag.DEPTH_MAP_VERIFIED.bitmask


# NOTE - Changed after moving from "error mask to quality mask concept"
def check_basic_record(record):
    """ obis-qc equivalent function, to assign bitmask
        for basic lat/lon validity / presence and
        also to check that the depth is consistent """

    qc_mask = 0

    # Are decimal latitude or decimal longitude missing ?
    if 'decimalLongitude' not in record or 'decimalLongitude' not in record:
        return 0
    else:
        # They are present
        qc_mask |= qc_mask_4

        # Are they valid ?
        result = misc.check_float(record['decimalLongitude'], [-180, 180])
        result2 = misc.check_float(record['decimalLatitude'], [-90, 90])
        if result["valid"] and result2["valid"]:
            qc_mask |= qc_mask_5
        else:
            return 0

    # Depths - consistency
    qc_mask |= check_depth_consistent(record)

    return qc_mask


def check_basic(records):
    """ performs the basic lat/lon presence and validity checks
        on a list of records
        :param records """
    return [check_basic_record(record) for record in records]


# NOTE - Changed after moving from "error mask to quality mask concept"
def check_record_in_areas(record, areas):
    """ verifies that a geographical point is in one of the rectangle areas
        :param record: The event record
        :param areas: The geographical areas - list of dicts - 2 segments east west and north south
        as [(east,west), (north,south)]
        This QC makes sense AFTER Lon and Lat decimal have been verified present and valid
        Assumption: Areas are rectangular
        """

    qc_mask = 0

    # In case the call is nonsensical
    if areas is None:
        return qc_mask

    # extracting from record
    if 'decimalLongitude' in record and 'decimalLatitude' in record:
        if misc.is_number(record['decimalLongitude']) and misc.is_number(record['decimalLatitude']):

            point_x = float(record['decimalLongitude'])
            point_y = float(record['decimalLatitude'])

            for area in areas:
                if (area["west"] <= point_x <= area["east"]) and (area["south"] <= point_y <= area["north"]):
                    qc_mask |= qc_mask_9

    # At least one of the areas passed "checks"
    return qc_mask


def check_in_areas(records, areas):
    """ verifies that the records are located in one of the rectangle areas
        :param records: The records to check
        :param areas: The geographical areas -Each  2 segments east west and north south
        as [(east,west), (north,south)]
        NOTE: This QC makes sense AFTER Lon and Lat decimal have been verified present and valid  """

    qc_masks = []
    for idx, record in enumerate(records):
        qc_masks.append(check_record_in_areas(record, areas))

    return qc_masks


# Modified to Quality mask instead of error mask
def check_depth_consistent(record):
    """ depth checks, in this case they must be numbers (representing meters)
        it is used as part of the basic checks """

    if "minimumDepthInMeters" in record and record["minimumDepthInMeters"] is not None:
        if misc.is_number(record["minimumDepthInMeters"]):
            min_depth = float(record["minimumDepthInMeters"])
        else:
            return 0
    else:
        # No point checking, minimum depth is not there
        return 0

    if "maximumDepthInMeters" in record and record["maximumDepthInMeters"] is not None:
        if misc.is_number(record["maximumDepthInMeters"]):
            max_depth = float(record["maximumDepthInMeters"])
        else:
            return 0
    else:
        # No point checking, minimum depth is not there
        return 0

    # If depths are present, they are numbers and they are consistent...
    if min_depth <= max_depth:
        return qc_mask_18

    else:
        return 0


def extract_depths(record):
    """ Depths are to be ckecked against the map
        Helper function to get a list of depths from a record
        :param: record
        :returns tuple of valid (numerical) depths """

    res = []
    if "minimumDepthInMeters" in record and record["minimumDepthInMeters"] is not None:
        depth = misc.check_float(record["minimumDepthInMeters"])
        if depth["valid"]:
            res.append(depth["float"])

    if "maximumDepthInMeters" in record and record["maximumDepthInMeters"] is not None:
        depth = misc.check_float(record["maximumDepthInMeters"])
        if depth["valid"]:
            res.append(depth["float"])
    return res

# Modified to Quality mask instead of error mask - TO VERIFY
def check_xy(records):
    """ :param records, already QC for location
        :returns qc_mask values, but QC is already inserted in records bitmasks
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

        qc_mask = 0

        if xy_res[i] is not None:
            # verify that records[i] does comply: point not on land and bathymetry is correct.
            # We MUST have checked already for depth validity
            xy = xy_res[i]
            record = records[i]

            # Check point on land
            if "QC" in record and (record["QC"] & qc_mask_5) and (record["QC"] & qc_mask_4):
                if xy["shoredistance"] >= 0:
                    qc_mask |= qc_mask_6

            # Check bathymetry - need to check that the reported depths are OK - if point not on land
            if qc_mask & qc_mask_6:
                depths = extract_depths(record)
                for depth in depths:
                    if  "bathymetry" in xy["grids"]:
                        if xy["grids"]["bathymetry"] < 0:
                            # We can do this because quality mask is set
                            if depth is not None and depth <= intercept + xy["grids"]["bathymetry"]:
                                qc_mask |= qc_mask_19
                        else:
                            if depth is not None and depth <= intercept + xy["grids"]["bathymetry"] * slope:
                                qc_mask |= qc_mask_19

            # Note: the qc_flag is already added to the record
            if "QC" in record:
                record["QC"] |= qc_mask
            else:
                record["QC"] = qc_mask
            results.append(qc_mask)
        else:
            if "QC" not in records[i]:
                records[i]["QC"] = 0
            results.append(0)

            # logger.warning("No xylookup result for %s" % records[i]["id"])

    return results

# TODO - MAKE IT COMPUTE AND ASSIGN QCs
def check_all_location_params(records, areas):
    """ Given a list of records it shall perform all
        location verifications for a batch of records
        including lookups. The records are modified, and it
        does not return any value
        :param records
        :param areas
        """
    # LON, LAT presence and validity, depth consistency
    qc_masks = check_basic(records)

    # Check if the points are within the areas...
    if areas is not None and len(areas):
        for idx, record in enumerate(records):
            if not qc_masks[idx]:  # Should not be "positive" to basic checks
                qc_masks[idx] |= check_record_in_areas(record, areas)

    # If the points are good, do the lookups...
    recs_for_lookup = []
    for idx, record in enumerate(records):
        record["QC"] = qc_masks[idx]
        if not qc_masks[idx]:
            recs_for_lookup.append(record)

    # pyxylookup
    check_xy(recs_for_lookup)
    return None
