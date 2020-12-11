""" Depth QCs """

from .util import qc_flags
from .util import misc

error_mask_18 = qc_flags.QCFlag.MIN_MAX_DEPTH_ERROR.bitmask
error_mask_19 = qc_flags.QCFlag.WRONG_DEPTH_MAP.bitmask  # TODO
error_mask_20 = qc_flags.QCFlag.WRONG_DEPTH_SPECIES.bitmask  # TODO


def check_record(record):
    """ depth checks """

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
