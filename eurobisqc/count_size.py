""" To check for missing fields in occurrence records as per error masks """
from .util import qc_flags
from .util import misc

error_mask_14 = qc_flags.QCFlag.OBSERVED_COUNT_MISSING.bitmask
error_mask_15 = qc_flags.QCFlag.OBSERVED_WEIGTH_MISSING.bitmask
error_mask_16 = qc_flags.QCFlag.SAMPLE_SIZE_MISSING.bitmask
error_mask_17 = qc_flags.QCFlag.SEX_MISSING.bitmask

def check_record(record):
    """ Applies the sampling verifications """

    qc = 0

    if "individualCount" in record and record["individualCount"] is not None:
        if misc.is_number(record["individualCount"]):
            if "sampleSizeValue" in record and record["sampleSizeValue"] is not None :
                if not misc.is_number(record["sampleSizeValue"]):
                    qc |= error_mask_16
            else:
                qc|= error_mask_16
        else:
            qc |= error_mask_14
    else:
        qc |= error_mask_14

    if not ("sex" in record and record["sex"] is not None):
        qc|= error_mask_17

    # TODO: In what field is weight ? For check OBSERVED_WEIGTH_MISSING

    return qc
