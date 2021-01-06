import requests
from dbworks import mssql_db_functions as mssql
from eurobisqc.util import extract_area


class Dataset:
    """ all the necessary to represent
        an archive as retrieved from the DB """
    # The data that I need from eurobis and their names

    # FLAG: These maps could also be parametric based on the Lookup DB
    # FLAG: Prerequisite is that the columns exist in the DB. This has been verified for these columns
    field_map_eurobis = {'dataprovider_id': 'dataprovider_id',
                         'occurrenceID': 'occurenceID',
                         'eventID': 'eventID',
                         'DarwinCoreType': 'DarwinCoreType',
                         'BasisOfRecord': 'basisOfRecord',
                         'Latitude': 'decimalLatitude',
                         'Longitude': 'decimalLongitude',
                         'MaximumDepth': 'maximumDepthInMeters',
                         'MinimumDepth': 'minimumDepthInMeters',
                         'ScientificName': 'scientificName',
                         'aphia_id': 'scientificNameId',
                         'occurrenceStatus': 'occurrenceStatus',
                         'Sex': 'sex',
                         'Genus': 'genus',
                         'qc': 'qc'
                         }  # The mapping of the interesting fields DB <--> DwCA as defined for eurobis table

    field_map_emof = {'dataprovider_id': 'dataprovider_id',
                      'occurrenceID': 'occurenceID',
                      'eventID': 'eventID',
                      'measurementType': 'measurementType',
                      'measurementTypeID': 'measurementTypeID',
                      'measurementValue': 'measurementValue',
                      }  # The mapping of the interesting fields DB <--> DwCA as defined for eurobis_measurementoorfact table

    sql_eurobis_start = "SELECT "
    sql_eurobis_end = " FROM eurobis WHERE dataprovider_id="

    # I hate this one... we should do a SQL SP instead with parameter dataprovider_id
    sql_eurobis_eventdate = \
        """ 
    COALESCE(dbo.ipt_date_iso8601(StartYearCollected,
                              StartMonthCollected,
                              StartDayCollected,
                              COALESCE(StartTimeOfDay,TimeOfDay),
                              TimeZone),
             dbo.ipt_date_iso8601(YearCollected,
                              MonthCollected,
                              DayCollected,
                              COALESCE(StartTimeOfDay,TimeOfDay),
                              TimeZone))
                              + (CASE WHEN (EndYearCollected IS NOT NULL) 
                                          THEN '/'+ 
                                dbo.ipt_date_iso8601(EndYearCollected,
                                                     EndMonthCollected,
                                                     EndDayCollected,
                                                     COALESCE(EndTimeOfDay,TimeOfDay),TimeZone) 
                                          ELSE '' END)

                               + (CASE WHEN (EndYearCollected IS NULL AND EndTimeOfDay IS NOT NULL) 
                                          THEN '/'+ 
                                       COALESCE(dbo.ipt_date_iso8601(StartYearCollected,
                                                                     StartMonthCollected,
                                                                     StartDayCollected,
                                                                     EndTimeOfDay,
                                                                     TimeZone), 
                                                dbo.ipt_date_iso8601(YearCollected,
                                                                     MonthCollected,
                                                                     DayCollected,
                                                                     EndTimeOfDay,
								     TimeZone)) 
                                           ELSE '' END) 
            AS eventDate """

    sql_providers = "SELECT * FROM dataproviders WHERE id="
    sql_emof_start = "SELECT "
    sql_emof_end = " FROM eurobis_measurementorfact WHERE dataprovider_id="

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
            sql_str = f"select * from dataproviders d where id = {das_prov_id};"

            # Fetch the provider line
            cur = mssql.conn.cursor()
            cur.execute(sql_str)
            # Get a dictionary
            provider_fields = [description[0] for description in cur.description]

            provider = cur.fetchone()

            self.provider_record = dict(zip(provider_fields, provider))
            self.imis_das_id = self.provider_record['IMIS_DasID']
            self.dataprovider_id = self.provider_record['id']  # Of course this we have already
            self.darwin_core_type = self.provider_record['core']
            # Should see if more is needed

    def get_ev_occ_records(self, das_prov_id):
        """ retrieves event and occurrence records for the dataset in das_id from SQL Server"""
        if not mssql.conn:
            mssql.open_db()

        if mssql.conn is None:
            # Should find a way to exit and advice
            pass
        else:
            # get records
            sql_string = self.query_builder_eve_occur(das_prov_id)
            cursor = mssql.conn.cursor()
            cursor.execute(sql_string)

            columns = [column[0] for column in cursor.description]
            records = []
            for row in cursor:
                records.append(dict(zip(columns, row)))

            for record in records:
                if record['DarwinCoreType'] == 1:  # Occurrence
                    self.occurrence_recs.append(record)
                elif record['DarwinCoreType'] == 2:
                    self.event_recs.append(record)


    def get_mof_records(self, das_prov_id):
        """ retrieves measurementorfact records for the dataset in das_id from SQL Server """

        if not mssql.conn:
            mssql.open_db()

        if mssql.conn is None:
            # Should find a way to exit and advice
            pass
        else:
            # get records
            sql_string = self.query_builder_emof(das_prov_id)
            cursor = mssql.conn.cursor()
            cursor.execute(sql_string)

            columns = [column[0] for column in cursor.description]
            records = []
            for row in cursor:
                records.append(dict(zip(columns, row)))

            for record in records:
                    self.emof_recs.append(record)


    def query_builder_eve_occur(self, dataprovider_id):
        """ Builds the SQL query string to retrieve all event, occur records for a dataset
            inclusive of the eventDate"""

        sql_string = self.sql_eurobis_start

        for par in self.field_map_eurobis:
            sql_string = sql_string + f"{par} as {self.field_map_eurobis[par]}, "

        # add eventDate, end and parameter
        sql_string = sql_string + self.sql_eurobis_eventdate + self.sql_eurobis_end + f"{dataprovider_id};"

        return sql_string

    def query_builder_emof(self, dataprovider_id):
        """ Builds the SQL query string to retrieve all emof records for a dataset """

        sql_string = self.sql_emof_start

        for idx, par in enumerate(self.field_map_emof):

            sql_string = sql_string + f"{par} as {self.field_map_emof[par]} "

            if idx < len(self.field_map_emof) - 1:
                sql_string += ", "

        sql_string = sql_string + self.sql_emof_end + f"{dataprovider_id};"

        return sql_string

    def load_dataset(self, das_prov_id):
        """ given a dataset id from the dataprovider
            loads an entire dataset in RAM for processing
            """
        self.get_provider_data(das_prov_id)
        self.get_ev_occ_records(das_prov_id)
        self.get_mof_records(das_prov_id)
        # Misses the API call to get the areas, this needs to be called AFTER having loaded the dataset data
        # from providers ...
        self.get_areas_from_eml(self.imis_das_id)


    def get_areas_from_eml(self, imis_das_id):

        eml = None
        url = f"http://www.eurobis.org/imis?dasid={imis_das_id}&show=eml"

        response = requests.get(url)
        if response is not None:
            eml =response.text

        if eml is not None:
            self.areas = extract_area.find_areas(eml)
