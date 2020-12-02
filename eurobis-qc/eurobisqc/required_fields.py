from . util import qc_flags
import logging
logger = logging.getLogger(__name__)

# Return value in case of errors
error_mask = qc_flags.QCFlag.REQUIRED_FIELDS.encode()

def check_record(record):
    """Check for presence of required fields."""

    result = False

    required_fields = ["eventDate", "decimalLongitude", "decimalLatitude", "scientificName", "scientificNameID", "occurrenceStatus", "basisOfRecord"]
    # recommended_fields = ["minimumDepthInMeters", "maximumDepthInMeters"]

    present_required_fields = set(record.keys()).intersection(set(required_fields))

    if len(present_required_fields) == len(required_fields):
        result = True

    return 0 if result else error_mask

def check_source_record(record):

    """ To be called for source type records """

    vocab = ["PreservedSpecimen", "FossilSpecimen", "LivingSpecimen", "MaterialSample", "Event", "HumanObservation", "MachineObservation", "Taxon", "Occurrence"]
    if "basisOfRecord" in record and record["basisOfRecord"] is not None:
        if not record["basisOfRecord"].lower() in [value.lower() for value in vocab]:
            return error_mask
    else:
        return error_mask

    return 0

def check(records):
    return [check_record(record) for record in records]

def check_source_records(records):
    return [check_source_record(source_record) for source_record in records]