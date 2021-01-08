import sys

from eurobisqc.util import qc_flags

this = sys.modules[__name__]

# Return values for when the quality check fails
qc_mask_1 = qc_flags.QCFlag.REQUIRED_FIELDS_PRESENT.bitmask
qc_mask_10 = qc_flags.QCFlag.OBIS_DATAFORMAT_OK.bitmask

# TODO: Maybe make this parameterable from config file as in measurements...
this.required_fields = {"eventDate", "decimalLongitude", "decimalLatitude", "scientificName", "scientificNameID",
                        "occurrenceStatus", "basisOfRecord"}

this.recommended_fields = {"minimumDepthInMeters", "maximumDepthInMeters"}  # Decide whether to do something with these

this.values_basis_of_record = {"PreservedSpecimen", "FossilSpecimen", "LivingSpecimen", "MaterialSample", "Event",
                               "HumanObservation", "MachineObservation", "Taxon", "Occurrence"}

this.vocab = {value.lower() for value in this.values_basis_of_record}

# When Using lowercase for field names
fields_to_compare = {value.lower() for value in this.required_fields}


def check_record_required(record, option=False):
    """ Check for presence of required fields, as per reference. This corresponds to QC1.
        Optionally look at a set of recommended fields
        :param record: The record to QC
        :param option: Recommended fields are verified or not
    """

    qc_mask = 0

    # This would be value.lower() if not field names must be checked in lowercase
    present_fields = set(record.keys())

    # May be it can be done differently (faster)
    present_required_fields = present_fields.intersection(this.required_fields)

    if len(present_required_fields) == len(this.required_fields):
        # Looking at the checks from obis-qc, verify that fields are present but also that they are not None
        count = 0
        for required_field in this.required_fields:
            count += 1
            if record[required_field] is None:
                break  # No need to proceed

        if count == len(this.required_fields):
            qc_mask |= qc_mask_1
    # else:
    #     qc_mask |= qc_mask_1
    # An option to be pedantic and require presence of the optional fields
    if option:
        present_optional_fields = set(present_fields).intersection(set(this.recommended_fields))
        if len(present_optional_fields) == len(this.recommended_fields):
            count = 0
            for optional_field in this.recommended_fields:
                count += 1
                if record[optional_field] is None:
                    break  # No need to proceed

            if count == len(this.recommended_fields):
                qc_mask |= qc_mask_1

    return qc_mask


def check_record_obis_format(record):
    """ To be called for source type records
        :param record:
    """
    qc_mask = 0

    # QC 10
    if "basisOfRecord" in record and record["basisOfRecord"] is not None:
        if record["basisOfRecord"].lower() in this.vocab:
            qc_mask |= qc_mask_10
    # else:
    #     qc_mask |= qc_mask_10

    return qc_mask


def check_obis(records):
    """ To be called for a batch of records (list)
        :param records:
        it shall return the results of QC 10
    """

    return [check_record_obis_format(record) for record in records]


def check_required(records):
    """ To be called for a batch of records (list)
        :param records:
        it shall return the results of QC 1
        """

    return [check_record_required(record) for record in records]


def check(records):
    """ To be called for a batch of records (list)
        :param records:
        it shall return the results of QC 1 combined with QC 10 (saves some looping)
        """

    return [check_record_required(record) | check_record_obis_format(record) for record in records]
