from unittest import TestCase
from qc_flags import QCFlag

class TestQC_Flag(TestCase):

    def test_encode(self):
        for qc_flag in QCFlag:
            try :
                print(qc_flag.encode())
            except:
                self.fail()

    def test_decode_message(self):
        i = 0
        for qc_flag in QCFlag:
            try :
                print(qc_flag.decode_message(i))
                i += 1
            except:
                self.fail()

    def test_decode_name(self):
        i = 0
        for qc_flag in QCFlag:
            try :
                print(qc_flag.decode_name(i))
                i += 1
            except:
                self.fail()

    def test_decode_mask(self):
        test_mask = 1048575
        try :
            flags = QCFlag.decode_mask(test_mask)
            print(flags)
        except :
            self.fail()

        self.assertTrue(flags[0]!='INVALID')
        self.assertTrue(flags[-1]=='INVALID')