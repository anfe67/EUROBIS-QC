""" Date/Time Quality Checks """

import datetime

from isodateparser import ISODateParser
from eurobisqc.util import qc_flags
from eurobisqc.util import misc

qc_mask_7 = qc_flags.QCFlag.DATE_TIME_OK.bitmask
qc_mask_11 = qc_flags.QCFlag.VALID_DATE_1.bitmask
qc_mask_12 = qc_flags.QCFlag.VALID_DATE_2.bitmask
qc_mask_13 = qc_flags.QCFlag.VALID_DATE_3.bitmask


# Modified to Quality mask instead of error mask
def check_record(record, min_year=0):
    """Check the event date """

    qc_mask = 0

    if "eventDate" in record and record["eventDate"] is not None:
        try:
            parser = ISODateParser(record["eventDate"])
            # Date parsed, means format is OK
            qc_mask |= qc_mask_7

            if parser.dates["mid"].year >= min_year:
                # year does not precede minimum year in settings: Invalid
                qc_mask |= qc_mask_11

            ms_start = misc.date_to_millis(parser.dates["start"])
            ms_end = misc.date_to_millis(parser.dates["end"])

            if ms_start >= misc.date_to_millis(datetime.date.today()):
                # date not in the future
                qc_mask |= qc_mask_11

            if ms_start <= ms_end:
                # Min and max consistent
                qc_mask |= qc_mask_12

            # is timezone filled (does it need to be checked for both ends)
            if parser.components["start"]["timezone"] is not None:
                qc_mask |= qc_mask_13

            # is a time filled (limiting to hours:minutes)
            if parser.components["start"]["hours"] is not None:
                if parser.components["start"]["minutes"] is not None:
                    qc_mask |= qc_mask_13


        except (ValueError, TypeError):
            return qc_mask

    return qc_mask


def check(records, min_year=0):
    return [check_record(record, min_year) for record in records]


# Modified to Quality mask instead of error mask
def check_date(date_string):
    """ for checking validity of any date expressed in the DwCA format
        It does not check if date is in the future, just that it is
        parseable and that min is smaller than max. Returns QCs as
        described.
        """
    qc_mask = 0

    try:
        parser = ISODateParser(date_string)
        qc_mask |= qc_mask_7

        ms_start = misc.date_to_millis(parser.dates["start"])
        ms_end = misc.date_to_millis(parser.dates["end"])

        # End before start
        if ms_start <= ms_end:
            qc_mask |= qc_mask_12

        # No timezone
        if parser.components["start"]["timezone"] is not None:
            qc_mask |= qc_mask_13

        # No hour:minute
        if parser.components["start"]["hours"] is not None:
            if parser.components["start"]["minutes"] is not None:
                qc_mask |= qc_mask_13


    except (ValueError, TypeError):
        return qc_mask

    return qc_mask
