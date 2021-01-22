from unittest import TestCase
from eurobisqc import measurements
from eurobisqc.util import qc_flags


class Test(TestCase):
    """ Define a few mock records and test the function """
    records = [
        {"id": 0},  # No fields - no checks performed
        {"id": 1, "measurementType": "Wet weight Biomass", "measurementValue": 32.4},  # Type field - good
        {"id": 2, "measurementTypeID": "http://vocab.nerc.ac.uk/collection/P01/current/SDBIOL05/",
         "measurementValue": 32.4},  # Type ID field - good
        {"id": 3, "measurementType": "Wet weight Biomass"},  # Type but no measure
        {"id": 4, "measurementTypeID": "http://vocab.nerc.ac.uk/collection/P01/current/SDBIOL05/"},  # Id no val
        {"id": 5, "measurementType": "count individuals"},  # counting but no number
        {"id": 6, "measurementTypeID": "http://vocab.nerc.ac.uk/collection/P01/current/OCOUNT01/"},  # Id no val
        {"id": 7, "measurementType": "Abundance", "measurementValue": 9.4},  # Sample size
        {"id": 8, "measurementType": "Abundance"},  # Sample size no measure
        {"id": 9, "measurementType": "Abundance", "measurementValue": "a lot!"},  # Non numeric - OK
        {"id": 10, "measurementTypeID": "http://vocab.nerc.ac.uk/collection/P01/current/OCOUNT01/",
         "measurementValue": "a lot!"},  # Non numeric - OK following Bart's recommendations
        {"id": 11, "dynamicProperties": "{'tragusLengthInMeters': '0.014', ' weightInGrams': '120'}"},  # dyn prop OK
        {"id": 12, "dynamicProperties": "Net type: Bogorov-Rass; Net mouth opening: 0.8 m; Mesh size: 300 mkm"},  # OK
        {"id": 13, "dynamicProperties": "ObservedWeightInGrams=0.00052"},  # OK
        {"id": 14, "dynamicProperties": "ObservedWeightInGrams=' '"},  # NOT OK
        {"id": 15, "sex": "hermaphrodite"},  # SEX - OK
        {"id": 16, "sex": "multiversion"}  # SEX - NOT OK
    ]

    expected_results = [0,
                        qc_flags.QCFlag.OBSERVED_WEIGTH_PRESENT.bitmask,
                        qc_flags.QCFlag.OBSERVED_WEIGTH_PRESENT.bitmask,
                        0,
                        0,
                        0,
                        0,
                        qc_flags.QCFlag.SAMPLE_SIZE_PRESENT.bitmask,
                        0,
                        qc_flags.QCFlag.SAMPLE_SIZE_PRESENT.bitmask,
                        qc_flags.QCFlag.OBSERVED_COUNT_PRESENT.bitmask,
                        ]
    expected_results_dyn_prop = [qc_flags.QCFlag.OBSERVED_WEIGTH_PRESENT.bitmask,
                                 0,
                                 qc_flags.QCFlag.OBSERVED_WEIGTH_PRESENT.bitmask,
                                 0  # Verify should be weight
                                 ]

    expected_results_sex = [qc_flags.QCFlag.SEX_PRESENT.bitmask,
                            0, ]

    def test_check_record(self):
        results = []
        for record in self.records[0:11]:
            results.append(measurements.check_record(record))

        self.assertTrue(results == self.expected_results)

    def test_check(self):
        results = measurements.check(self.records[0:11])
        self.assertTrue(results == self.expected_results)

    def test_check_dyn_prop(self):
        results = measurements.check_dyn_prop(self.records[11:15])
        self.assertTrue(results == self.expected_results_dyn_prop)

    def test_check_sex(self):
        results = measurements.check_sex(self.records[15:])
        self.assertTrue(results == self.expected_results_sex)

# Note: - DynamicProperties cannot be found in DB...
