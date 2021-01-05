from dbworks import mssql_db_functions as mssql


class Dataset:
    """ all the necessary to represent
        an archive as retrieved from the DB """

    data_map = {'BasisOfRecord': 'basisOfRecord',
                'Latitude': 'decimalLatitude',
                'Longitude': 'decimalLongitude',
                'ScientificName': 'scientificName',
                'aphia_id': 'scientificNameId',
                'Sex': 'sex',
                'Genus': 'genus'}  # The mapping of the interesting fields DB <--> DwCA as defined

    # Need to build eventDate from the other fields...
    # eventDate from EndDayCollected, ..Month.., ..Year.., Time of Day, start fields and timezone (8 fields)

    def __init__(self):
        """ Initialises an empty dataset """

        self.darwin_core_type = 1  # 1 = Occurrence 2 = Event
        self.event_recs = []  # The Event Records
        self.occurrence_recs = []  # The Occurrence Records
        self.emof_recs = []  # The MoF/eMof records
        self.dataprovider_id = None  # The dataset ID from the dataproviders table
        self.imis_das_id = None  # The IMIS dataset ID for querying the eml
        self.eml = None  # Eml as from the http://www.eurobis.org/imis?dasid=<IMIS_DasID>&show=eml API
        self.event_dates_eml = None  # Extract the dates from the EML as last resort
        self.areas = []  # Extract areas from EML (Bounding box do not have useful info - seek advice)
        self.provider_record = None  # Provider record extracted

    def get_eml(self, imis_das_id):
        """ retrieves eml for the dataset """

        pass

    def get_provider_data(self, das_prov_id):
        if not mssql.conn:
            mssql.open_db()

        if mssql.conn is None:
            # Should find a way to exit and advice
            pass
        else:
            # Can start querying the DB using the dataset provider ID
            sql_str = f"select * from dataproviders d where IMIS_DasID = {das_prov_id};"

            # Fetch the provider line
            cur = mssql.conn.cursor()
            cur.execute(sql_str)
            # Get a dictionary
            provider_fields = [description[0] for description in cur.description]
            provider = cur.fetchOne()
            self.provider_record = dict(zip(provider_fields, provider))
            self.imis_das_id = self.provider_record['IMIS_DasID']
            self.dataprovider_id = self.provider_record['id']
            self.darwin_core_type = self.provider_record['core']
            # Should see if more is needed

    def get_ev_occ_records(self, das_prov_id):
        """ retrieves event and occurrence records for the dataset in das_id from SQL Server"""
        pass

    def get_mof_records(self, das_prov_id):
        """ retrieves measurementorfact records for the dataset in das_id from SQL Server """

        pass

    def get_ds_properties(self, das_prov_id):
        """ retrieves the dataset properties included IMIS_DaSID from SQL Server"""
        pass
