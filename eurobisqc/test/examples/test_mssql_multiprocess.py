from unittest import TestCase
from eurobisqc.examples import mssql_multiprocess


class Test(TestCase):
    dataset_names = [
        ' Zooplankton respiration data from Fort Jesus and measurements of dry weight and length of copepods collected '
        'at Tudor Creek between August 1985 and June 1986',
        ' Faunal species composition of brackish water crabs at Gazi, Kanamai, Bamburi and Mkomani (Kenya)',
        ' Abundance of <i>Echinothrix diadema</i> and its substrate coverage in the Mombasa Marine National Park and '
        'Reserve (Kenya) in September-October 1997',
        ' Macrofaunal composition and zonation on sandy beaches at Gazi, Kanamai and Malindi Bay Kenya between April '
        'and December 1986',
        ' Counts of Mysidacea sampled at night in Gazi Bay in October 1994',
        ' Mangrove crabs and their relationship with the environment in mangrove forests of Dabaso and Gazi (Kenya) '
        'sampled in 1998 and 1999',
        " Israel's sea turtle monitoring program",
        ' Cetacean coordinated transborder monitoring using ferries as platforms of observation off Tunisia '
        '2013-2014 - Atutax',
        ' University of Liverpool seabird tracking in Anguilla 2012-2015',
        ' Andalusia, Spain. Small loggerheads from a nest at Pulpí (Almería)',
        ' A summary of benthic studies in the sluice dock of Ostend during 1976-1981']
    dataset_ids = [899,
                   918,
                   928,
                   933,
                   938,
                   955,
                   1012,
                   1020,
                   1022,
                   1028,
                   1213]

    def test_do_db_multi_selection_ok(self):
        mssql_multiprocess.do_db_multi_selection(self.dataset_ids, self.dataset_names)
        # Need to observe the logs
        assert True

    def test_do_db_multiselection_notok(self):
        # Need to observe the logs
        # Change one of the datasets to a non-existing number. What should happen?
        self.dataset_ids[4] = 9999
        mssql_multiprocess.do_db_multi_selection(self.dataset_ids, self.dataset_names)
        assert True

