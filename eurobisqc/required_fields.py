from .util import qc_flags
import logging

logger = logging.getLogger(__name__)

# Return value when the quality check fails
error_mask = qc_flags.QCFlag.REQUIRED_FIELDS.encode()


def check_record_strict(record):
    """Check for presence of required fields."""

    result = False

    required_fields = ["eventDate", "decimalLongitude", "decimalLatitude", "scientificName", "scientificNameID",
                       "occurrenceStatus", "basisOfRecord"]

    # When Using lowercase for field names
    fields_to_compare = [value.lower() for value in required_fields]
    # recommended_fields = ["minimumDepthInMeters", "maximumDepthInMeters"] # Decide whether to do something with these

    # This would be value.lower() if not field names must be checked in lowercase
    present_fields = [value for value in record.keys()]

    present_required_fields = set(present_fields).intersection(set(required_fields))

    if len(present_required_fields) == len(required_fields):
        # Looking at the checks from obis-qc, I assume we need to verify if the fields are present but also that they are not None
        count = 0
        for required_field in required_fields:
            count += 1
            if record[required_field] is None:
                break  # No need to proceed

        if count == len(required_fields):
            result = True

    return 0 if result else error_mask


def check_record(record, strict=False):
    """ To be called for source type records
    :param record:
    :param strict:
    """

    vocab = ["PreservedSpecimen", "FossilSpecimen", "LivingSpecimen", "MaterialSample", "Event", "HumanObservation",
             "MachineObservation", "Taxon", "Occurrence"]
    if "basisOfRecord" in record and record["basisOfRecord"] is not None:
        if not record["basisOfRecord"].lower() in [value.lower() for value in vocab]:
            return error_mask
    else:
        return error_mask

    if strict:
        return check_record_strict(record)

    return 0


def check(records):
    return [check_record(record, False) for record in records]


def check_source_records(records):
    return [check_record(source_record, False) for source_record in records]
