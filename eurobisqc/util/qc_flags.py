""" Definition of EUROBIS-QC Flags as per specifications """
from enum import Enum


class QCFlag(Enum):
    """ The error bitmask shall be determined by the bitmask, second element in the tuple
        includes class and object utility methods """

    REQUIRED_FIELDS_MISS = ("Not all the required fields are present", 1)  # In required_fields
    TAXONOMY_APHIAID_MISS = ("AphiaID not found", 2)  # In taxonomy_db
    TAXONOMY_RANK_LOW = ("Taxon level lower than family", 3)  # In taxonomy_db
    GEO_LAT_LON_MISSING = ("Lat or Lon missing or either equal to None", 4)  # In location
    GEO_LAT_LON_INVALID = ("Lat or Lon missing or not within boundaries (-90 to 90 and -180 to 180)", 5)  # In location
    GEO_LAT_LON_NOT_SEA = ("Lat - Lon not on sea / coastline", 6)  # In location
    DATE_TIME_NOT_COMPLETE = ("Year or Start Year or End Year incomplete or invalid", 7)  # In time_qc
    TAXON_APHIAID_NOT_EXISTING = ("Marine Taxon not existing in APHIA", 8)  # FLAG - Probably not doing it
    GEO_COORD_AREA = ("Coordinates not in the specified area", 9)  # In location
    NO_OBIS_DATAFORMAT = ("No valid code found in basisOfRecord", 10)  # in required_fields
    INVALID_DATE_1 = ("Invalid sampling date", 11)  # In time_qc
    INVALID_DATE_2 = ("End sampling date before start date", 12)  # In time_qc
    INVALID_DATE_3 = ("Sampling time invalid or timezone not completed", 13)  # In time_qc
    OBSERVED_COUNT_MISSING = ("Empty or missing observed individual count", 14)  # In measurements
    OBSERVED_WEIGTH_MISSING = ("Empty or missing observed weigth", 15)  # In measurements
    SAMPLE_SIZE_MISSING = ("Observed individual count > 0 but sample size missing", 16)  # In measurements
    SEX_MISSING_OR_WRONG = ("Sex missing or wrong OBIS code", 17)  # In measurements
    MIN_MAX_DEPTH_ERROR = ("Minimum depth greater than maximum depth", 18)  # in location
    WRONG_DEPTH_MAP = ("Depth incoherent with depth map", 19)  # In location
    WRONG_DEPTH_SPECIES = ("Depth incoherent with species depth range", 20)  # FLAG - Probably not doing it

    # All the required codes to follow

    def __init__(self, message, qc_number):

        self.text = message
        self.qc_number = qc_number
        self.bitmask = self.encode(qc_number - 1)

    @staticmethod
    def encode(bit_number):

        """ Returns an integer corresponding to the error code.
            This can be combined to other codes using OR """

        return 1 << bit_number

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

# TODO: NOT WORKING !
    @classmethod
    def decode_mask(cls, mask):

        """ Finds out all flags in a bitmask and return them as a list of QC_Flags names
            adds an INVALID string at the end if the mask is too big """

        qc_flags = []
        sum_all_flags = 0
        for qc_flag in QCFlag:
            if (1 << (qc_flag.qc_number -1) ) & mask:
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
