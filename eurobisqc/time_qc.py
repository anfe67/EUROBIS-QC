""" Date/Time Quality Checks """

import datetime
import logging

from isodateparser import ISODateParser
from eurobisqc.util import qc_flags
from eurobisqc.util import misc

logger = logging.getLogger(__name__)

error_mask_7 = qc_flags.QCFlag.DATE_TIME_NOT_COMPLETE.bitmask
error_mask_11 = qc_flags.QCFlag.INVALID_DATE_1.bitmask
error_mask_12 = qc_flags.QCFlag.INVALID_DATE_2.bitmask
error_mask_13 = qc_flags.QCFlag.INVALID_DATE_3.bitmask


def check_record(record, min_year=0):
    """Check the event date """

    qc = 0

    if "eventDate" in record and record["eventDate"] is not None:
        try:
            parser = ISODateParser(record["eventDate"])
            if parser.dates["mid"].year < min_year:
                # year precedes minimum year in settings: Invalid
                qc |= error_mask_11

            ms_start = misc.date_to_millis(parser.dates["start"])
            ms_end = misc.date_to_millis(parser.dates["end"])

            if ms_start > misc.date_to_millis(datetime.date.today()):
                # date in the future
                qc |= error_mask_11

            if ms_start > ms_end:
                qc |= error_mask_12

            # is timezone filled (does it need to be checked for both ends)
            if parser.components["start"]["timezone"] is None:
                qc |= error_mask_13

            # is a time filled (limiting to hours:minutes)
            if parser.components["start"]["hours"] is not None:
                if parser.components["start"]["minutes"] is None:
                    qc |= error_mask_13
            else:
                qc |= error_mask_13

        except (ValueError, TypeError):
            qc |= error_mask_11
            logger.error("Error processing date " + record["eventDate"])
            return qc

    else:
        qc |= error_mask_7  # Filled but not valid

    return qc


def check(records, min_year=0):
    return [check_record(record, min_year) for record in records]


def check_date(date_string):
    """ for checking validity of any date expressed in the DwCA format
        It does not check if date is in the future, just that it is
        parseable and that min is smaller than max. Returns QCs as
        described.
        """
    qc = 0

    try:
        parser = ISODateParser(date_string)

        ms_start = misc.date_to_millis(parser.dates["start"])
        ms_end = misc.date_to_millis(parser.dates["end"])

        # End before start
        if ms_start > ms_end:
            qc |= error_mask_12

        # No timezone
        if parser.components["start"]["timezone"] is None:
            qc |= error_mask_13

            # No hour:minute
        if parser.components["start"]["hours"] is not None:
            if parser.components["start"]["minutes"] is None:
                qc |= error_mask_13
        else:
            qc |= error_mask_13

    except (ValueError, TypeError):
        qc |= error_mask_11
        logger.error("Error processing date " + date_string)
        raise

    return qc
