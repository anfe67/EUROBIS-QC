import qc_flags
import logging

logger = logging.getLogger(__name__)

# Return values for when the quality check fails
error_mask_1 = qc_flags.QCFlag.REQUIRED_FIELDS_MISS.bitmask
error_mask_10 = qc_flags.QCFlag.NO_OBIS_DATAFORMAT.bitmask

required_fields = ["eventDate", "decimalLongitude", "decimalLatitude", "scientificName", "scientificNameID",
                   "occurrenceStatus", "basisOfRecord"]

# recommended_fields = ["minimumDepthInMeters", "maximumDepthInMeters"] # Decide whether to do something with these

# When Using lowercase for field names
fields_to_compare = [value.lower() for value in required_fields]

def check_record_required(record):
    """ Check for presence of required fields, as per reference. This corresponds to QC1.
        :param record:
    """

    qc = 0

    # This would be value.lower() if not field names must be checked in lowercase
    present_fields = list(record.keys())

    # May be it can be done differently (faster)
    present_required_fields = set(present_fields).intersection(set(required_fields))

    if len(present_required_fields) == len(required_fields):
        # Looking at the checks from obis-qc, I assume we need to verify if the fields are present but also that they are not None
        count = 0
        for required_field in required_fields:
            count += 1
            if record[required_field] is None:
                break  # No need to proceed

        if count != len(required_fields):
            qc |= error_mask_1

    return qc


def check_record_obis_format(record):
    """ To be called for source type records
        :param record:
    """
    qc = 0

    # QC 10
    vocab = ["PreservedSpecimen", "FossilSpecimen", "LivingSpecimen", "MaterialSample", "Event", "HumanObservation",
             "MachineObservation", "Taxon", "Occurrence"]
    if "basisOfRecord" in record and record["basisOfRecord"] is not None:
        if not record["basisOfRecord"].lower() in [value.lower() for value in vocab]:
            qc |= error_mask_10
    else:
         qc |= error_mask_10

    # QC 1
    qc |= check_record_required(record)

    return qc


def check(records):
    """ To be called for a batch of records (list)
        :param records:
    """
    return [check_record_obis_format(record) for record in records]

