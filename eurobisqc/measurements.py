""" To check for missing fields in eMoF records as per error masks  """

import sys
from .util import qc_flags
from .util import misc
from lookupdb import db_functions

error_mask_14 = qc_flags.QCFlag.OBSERVED_COUNT_MISSING.bitmask
error_mask_15 = qc_flags.QCFlag.OBSERVED_WEIGTH_MISSING.bitmask
error_mask_16 = qc_flags.QCFlag.SAMPLE_SIZE_MISSING.bitmask
error_mask_17 = qc_flags.QCFlag.SEX_MISSING.bitmask

this = sys.modules[__name__]

# For measurement:The measurement type must contain for weight verification (lowercase check)
this.weight_measure_types = []
# And the measurement type ID must be :
this.weight_measure_type_ids = []

# For count :The measurement type must contain for weight verification (lowercase check)
this.count_measure_types = []
# And the measurement type ID must match one of
this.count_measure_type_ids = []

# For sample size
this.sample_size_measure_types = []
this.sample_size_measure_type_ids = []

# Same question for sex / gender (vocabulary) - no need for database lookup for this
sex_field = "sex"
sex_field_vocab = ["female", "male", "hermaphrodite"]

this.lookups_loaded = False


def initialize_lookups():
    """ Only needed at the first call to initialize the lookup tables """

    if this.lookups_loaded:
        return

    # row factory
    # db_functions.conn.row_factory = lambda cursor, row: row[0] # important, this has side effects
    # Fill the lookups:
    c = db_functions.conn.cursor()
    # COUNT
    data = c.execute('SELECT Value FROM countMeasurementTypeID').fetchall()
    this.count_measure_type_ids = [val[0] for val in data]
    c = db_functions.conn.cursor()
    data = c.execute('SELECT Value FROM countMeasurementType').fetchall()
    this.count_measure_types = [val[0] for val in data]
    # SAMPLE
    c = db_functions.conn.cursor()

    data = c.execute('SELECT Value FROM sampleSizeMeasurementTypeID').fetchall()
    this.sample_size_measure_type_ids =  [val[0] for val in data]
    c = db_functions.conn.cursor()
    data= c.execute('SELECT Value FROM sampleSizeMeasurementType').fetchall()
    this.sample_size_measure_types =  [val[0] for val in data]
    # WEIGHT
    c = db_functions.conn.cursor()

    data = c.execute('SELECT Value FROM weightMeasurementTypeID').fetchall()
    this.weight_measure_type_ids = [val[0] for val in data]
    c = db_functions.conn.cursor()

    data = c.execute('SELECT Value FROM weightMeasurementType').fetchall()
    this.weight_measure_types = [val[0] for val in data]
    this.lookups_loaded = True


def check_mtid(measurement_type_id, measurement_value):
    """ verifies that if one of the sought measurement
        types IDs is present, then the measurementValue is also
        present and not None
        :param measurement_type_id - as in the record
        :param measurement_value - as in the record
        purpose: attempt optimization """

    qc = 0
    # Is the measurement type id of a biomass weight
    for wmtid in this.weight_measure_type_ids:
        if wmtid in measurement_type_id:
            if measurement_value is None:
                qc |= error_mask_15

    # Is it the measurement of a sample size
    for smtid in this.sample_size_measure_type_ids:
        if smtid in measurement_type_id:
            if measurement_value is None:
                qc |= error_mask_16

    # Is it a head count
    for cmtid in this.count_measure_type_ids:
        if cmtid in measurement_type_id:
            if measurement_value is None:
                qc |= error_mask_14
    return qc


def check_mt(measurement_type, measurement_value):
    """ verifies that if one of the sought measurement
        types is present, then the measurementValue is also
        present and not None
        :param measurement_type - as in the record
        :param measurement_value - as in the record
        purpose: attempt optimization """

    qc = 0
    # Is the measurement type id of a biomass weight
    for wmt in this.weight_measure_types:
        if wmt in measurement_type:
            if measurement_value is None:
                qc |= error_mask_15

    # Is it the measurement of a sample size
    for smt in this.sample_size_measure_types:
        if smt in measurement_type:
            if measurement_value is None:
                qc |= error_mask_16

    # Is it a head count
    for cmt in this.count_measure_types:
        if cmt in measurement_type:
            if measurement_value is None:
                qc |= error_mask_14
    return qc


def check_record(record):
    """ Applies the sampling verifications, input should be a
        eMoF record or one containing the requested fields """

    qc = 0

    # It shall be done only once on the first entry
    if not this.lookups_loaded:
        initialize_lookups()

    # Starting with IDs - weight
    if "measurementTypeID" in record and record["measurementTypeID"] is not None:

        measurement_value = None if "measurementValue" not in record else record["measurementValue"]
        if isinstance(measurement_value,str) :
            if  not measurement_value.strip():
                qc |= check_mtid(record["measurementTypeID"].lower(), None)
        else:
            qc |= check_mtid(record["measurementTypeID"].lower(), measurement_value)


    # We do not have a ID measurement but we have a measurement type
    elif "measurementType" in record and record["measurementType"] is not None:
        measurement_value = None if "measurementValue" not in record else record["measurementValue"]
        if isinstance(measurement_value,str) :
            if  not measurement_value.strip():
                qc |= check_mt(record["measurementType"].lower(), None)
        else:
            qc |= check_mt(record["measurementType"].lower(), measurement_value)

    else:
        # Nothing else to verify
        pass

    # We still have to look at sex
    if "sex" in record:
        if record["sex"] is not None:
            if record["sex"] not in sex_field_vocab:
                qc |= error_mask_17
        else:
            qc |= error_mask_17

    return qc

def check_dyn_prop_record(record):
    """ runs the checks for dynamic property on the occurrence records """
    # This is a check on the properties field - to be done on the occurrence records

    qc = 0

    # It shall be done only once on the first entry
    if not this.lookups_loaded:
        initialize_lookups()

    if "dynamicProperties" in record and record["dynamicProperties"] is not None:

        # split up the value and make a dict
        properties = misc.string_to_dict(record["dynamicProperties"].strip())
        # If malformed, then skip
        if "conversion_fail" not in properties:

            for k in properties.keys():
                key = k.lower()
                for cmt in this.count_measure_types:
                    if cmt in key:
                        if properties[k] is None or (
                                isinstance(properties[k], str) and not properties[k].strip()):
                            qc |= error_mask_14


                for wmt in this.weight_measure_types:
                    if wmt in key:
                        if properties[k] is None or (
                                isinstance(properties[k], str) and not properties[k].strip()):
                            qc |= error_mask_15

                for smt in this.sample_size_measure_types:
                    if smt in key:
                        if properties[k] is None or (
                                isinstance(properties[k], str) and not properties[k].strip()):
                            qc |= error_mask_16
    return qc


def check_dyn_prop(records):
    """ runs the checks for dynamic property on the occurrence records """
    return [check_dyn_prop_record(record) for record in records]

def check(records):
    """ runs the checks for multiple records """
    return [check_record(record) for record in records]
