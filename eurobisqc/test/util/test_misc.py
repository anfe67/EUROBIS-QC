from unittest import TestCase
from eurobisqc.util import misc


class Test(TestCase):
    test_s1 = "{'tragusLengthInMeters': '0.014', ' weightInGrams': '120'}"  # JSON
    test_s2 = "Net type: Bogorov-Rass; Net mouth opening: 0.8 m; Mesh size: 300 mkm"  # OLD FORMAT
    test_s3 = "ObservedWeightInGrams=0.00052"
    test_s4 = ""
    test_s5 = "::"

    def test_string_to_dict(self):
        res1 = misc.string_to_dict(self.test_s1)
        self.assertTrue(res1['weightInGrams'] == '120')

        res2 = misc.string_to_dict(self.test_s2)
        self.assertTrue(res2['Net type'] == 'Bogorov-Rass')

        res3 = misc.string_to_dict(self.test_s3)
        self.assertTrue(res3['ObservedWeightInGrams'] == '0.00052')

        res4 = misc.string_to_dict(self.test_s4)
        self.assertTrue(res4['conversion_fail'])

        res5 = misc.string_to_dict(self.test_s5)
        self.assertTrue(res5['conversion_fail'])
