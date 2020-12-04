""" Definition of EUROBIS-QC Flags as per specifications """
from enum import Enum


class QCFlag(Enum):
    """ The error bitmask shall be determined by the bitmask, second element in the tuple
        includes class and object utility methods """

    REQUIRED_FIELDS = ("Not all the required fields are present", 0)
    TAXONOMY_APHIAID = ("AphiaID not retrievable", 1)
    TAXONOMY_NOT_ENOUGH = ("Taxon level lower than family", 2)
    GEO_LAT_LON_MISSING = ("Lat or Lon missing or both equal to None", 3)
    GEO_LAT_LON_INVALID = ("Lat or Lon missing or not within legal boundaries (-90 to 90 and -180 to 180)", 4)
    GEO_LAT_LON_3 = ("Lat - Lon not on sea / coastline", 5)
    DATE_TIME = ("Year or Start Year or End Year incomplete or invalid", 6)

    # All the required codes to follow

    def __init__(self, message, bitmask):

        self.text = message
        self.bitmask = bitmask

    def encode(self):

        """ Returns an integer corresponding to the error code.
            This can be combined to other codes using OR """

        return 1 << self.bitmask

    @classmethod
    def decode_message(cls, position):

        """ Returns the message of the error corresponding to the bit at position """

        # validity
        if not (0 <= position < len(QCFlag)):
            return "Invalid QC Flag code"

        # May need something more efficient
        for qc_flag in QCFlag:
            if qc_flag.bitmask == position:
                return qc_flag.text

    @classmethod
    def decode_name(cls, position):
        """ Returns the name of the error corresponding to the bit at position """

        # validity
        if not (0 <= position < len(QCFlag)):
            return "Invalid QC Flag code"

        # May need something more efficient
        for qc_flag in QCFlag:
            if qc_flag.bitmask == position:
                return QCFlag(qc_flag).name

    @classmethod
    def decode_mask(cls, mask):

        """ Finds out all flags in a bitmask and return them as a list of QC_Flags names
            adds an INVALID string at the end if the mask is too big """

        qc_flags = []
        sum_all_flags = 0
        for qc_flag in QCFlag:
            if (1 << qc_flag.bitmask) & mask:
                qc_flags.append(QCFlag(qc_flag).name)
                sum_all_flags += 1 << qc_flag.bitmask

        # I may get a mask which I cannot fully interpret, in that case I add an INVALID to the list
        if mask > sum_all_flags:
            qc_flags.append('INVALID')

        return qc_flags

    @classmethod
    def encode_qc(cls, record, error_mask):
        """ Record is a Python dictionary, will be augmented with the QC field
            if not present, error_mask shall be or-red to current value if
            existing """

        if isinstance(record, dict):
            if 'QC' not in record.keys():
                record['QC'] = 0

            record['QC'] |= error_mask
        else:
            return None

        return record

