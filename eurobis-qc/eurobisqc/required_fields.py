from . util import qc_flags
import logging
logger = logging.getLogger(__name__)


def check_record(record):
    """Check for presence of required fields."""

    result = False

    required_fields = ["eventDate", "decimalLongitude", "decimalLatitude", "scientificName", "scientificNameID", "occurrenceStatus", "basisOfRecord"]
    # recommended_fields = ["minimumDepthInMeters", "maximumDepthInMeters"]

    present_required_fields = set(record.keys()).intersection(set(required_fields))

    if len(present_required_fields) == len(required_fields):
        result = True

    return 0 if result else qc_flags.QCFlag.REQUIRED_FIELDS.encode()

def check(records):
    return [check_record(record) for record in records]