""" To check for missing fields in eMoF records as per error masks
    The
    """
from .util import qc_flags
from .util import misc

# TODO : Rewrite in accordance with email 12/12/2020

error_mask_14 = qc_flags.QCFlag.OBSERVED_COUNT_MISSING.bitmask
error_mask_15 = qc_flags.QCFlag.OBSERVED_WEIGTH_MISSING.bitmask
error_mask_16 = qc_flags.QCFlag.SAMPLE_SIZE_MISSING.bitmask
error_mask_17 = qc_flags.QCFlag.SEX_MISSING.bitmask

# For measurement:
# The measurement type must contain for weight verification (lowercase check)
weight_measure_type = "wet weight biomass"
# And the measurement type ID must be :
weight_measure_type_id = "http://vocab.nerc.ac.uk/collection/P01/current/SDBIOL05".lower()

# For count :
# The measurement type must contain for weight verification (lowercase check)
count_measure_type = "count"
count_measure_type_id = "http://vocab.nerc.ac.uk/collection/P01/current/OCOUNT01".lower()

# For sample size
sample_measure_type = "abundance"

# Same question for sex / gender

def check_record(record):
    """ Applies the sampling verifications, input should be a
        eMoF record or one containing the requested fields """

    qc = 0

    if "measurementType" in record and record["measurementType"] is not None:
        # We are looking at a wet biomass weight
        if weight_measure_type in record["measurementType"].lower():
            if "measurementValue" in record and record["measurementValue"] is not None:
                if not misc.is_number(record["measurementValue"]):
                    qc |= error_mask_15
            else:
                qc |= error_mask_15

        # We are looking at a count
        if count_measure_type in record["measurementType"].lower():
            if "measurementValue" in record and record["measurementValue"] is not None:
                if not misc.is_number(record["measurementValue"]):
                    qc |= error_mask_14
            else:
                qc |= error_mask_14

        # Looking at sample size
        if sample_measure_type in record["measurementType"].lower():
            if "measurementValue" in record and record["measurementValue"] is not None:
                if not misc.is_number(record["measurementValue"]):
                    qc |= error_mask_16
            else:
                qc |= error_mask_16

    else:
        if "measurementTypeID" in record and record["measurementTypeID"] is not None:
            # Is the measurement type id of a biomass weight
            if weight_measure_type_id in record["measurementTypeID"].lower():
                if "measurementValue" in record and record["measurementValue"] is not None:
                    if not misc.is_number(record["measurementValue"]):
                        qc |= error_mask_15
                else:
                    qc |= error_mask_15

            # Is the measurement type id of a count...
            if count_measure_type_id in record["measurementTypeID"].lower():
                if "measurementValue" in record and record["measurementValue"] is not None:
                    if not misc.is_number(record["measurementValue"]):
                        qc |= error_mask_14
                else:
                    qc |= error_mask_14

            # Looking at sample size: Do not know which measurementTypeIDs to verify, there are too many

    return qc


def check(records):
    """ runs the checks for multiple records """
    return [check_record(record) for record in records]
