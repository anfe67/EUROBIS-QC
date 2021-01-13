from pyodbc import Error
import requests
from dbworks import mssql_db_functions as mssql
from eurobisqc.util import extract_area


class EurobisDataset:
    """ all the necessary to represent
        an archive as retrieved from the DB """

    OCCURRENCE = 1
    EVENT = 2
    LOOKUP_BATCH_SIZE = 1000

    record_batch_update_count = 0
    # Query to verify that the id column exists. if no record is returned, then column does not exist
    # sql_check_id_field = "SELECT COLUMN_NAME  " \
    #                      "FROM INFORMATION_SCHEMA.COLUMNS " \
    #                      "WHERE TABLE_NAME = 'eurobis' " \
    #                      "and COLUMN_NAME ='id' " \
    #                      "ORDER BY ORDINAL_POSITION"

    # Query to create id field - takes about 4 minutes
    # sql_create_id = "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE " \
    #                 "BEGIN TRANSACTION " \
    #                   "DECLARE @id INT SET @id = 0 " \
    #                   "UPDATE eurobis SET @id = id = @id + 1  " \
    #                   "OPTION ( MAXDOP 1 ) " \
    #                 "COMMIT TRANSACTION "

    # Query to disable the triggers
    sql_disable_trigger = "disable TRIGGER [fill_field_sync_dataproviders] on [eurobis_dat].[dbo].[eurobis];"
    sql_enable_trigger = "enable TRIGGER [fill_field_sync_dataproviders] on [eurobis_dat].[dbo].[eurobis];"

    # FLAG: These maps could be parametric based on the Lookup DB
    # FLAG: Prerequisite is that the columns exist in the DB and that names do not change.
    # FLAG: Pipeline has been verified for the columns listed below
    field_map_eurobis = {'dataprovider_id': 'dataprovider_id',
                         'occurrenceID': 'occurrenceID',
                         'eventID': 'eventID',
                         'DarwinCoreType': 'DarwinCoreType',
                         'BasisOfRecord': 'basisOfRecord',
                         'Latitude': 'decimalLatitude',
                         'Longitude': 'decimalLongitude',
                         'MaximumDepth': 'maximumDepthInMeters',
                         'MinimumDepth': 'minimumDepthInMeters',
                         'ScientificName': 'scientificName',
                         "'urn:lsid:marinespecies.org:taxname:' + CONVERT(VARCHAR(255), aphia_id)": 'scientificNameID',
                         'occurrenceStatus': 'occurrenceStatus',
                         'Sex': 'sex',
                         'Genus': 'genus',
                         'qc': 'qc',
                         '%%physloc%%': 'physloc'  # Note: Undocumented, may not work in future - use as update key
                         }  # The mapping of the interesting fields DB <--> DwCA as defined for eurobis table

    field_map_emof = {'dataprovider_id': 'dataprovider_id',
                      'occurrenceID': 'occurrenceID',
                      'eventID': 'eventID',
                      'measurementType': 'measurementType',
                      'measurementTypeID': 'measurementTypeID',
                      'measurementValue': 'measurementValue',
                      }  # Mapping of the interesting fields DB <--> DwCA as def. for eurobis_measurementoorfact table

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

    # Important - query to update an event or occurrence record
    sql_update_start = "update eurobis set qc = "  # add the calculated QC
    sql_update_middle = " where dataprovider_id = "

    # If the records contains Latitude and Longitude they are indexed, so could speed updates up
    sql_if_lat = " and Latitude = "
    sql_if_lon = " and Longitude = "

    sql_update_end = " and %%physloc%% = "  # add at the end the record['physloc'] retrieved at the start

    def __init__(self):
        """ Initialises an empty dataset """

        self.darwin_core_type = 1  # 1 = Occurrence 2 = Event
        self.event_recs = []  # The Event Records
        self.occurrence_recs = []  # The Occurrence Records
        self.emof_recs = []  # The MoF/eMof records
        self.occ_indices = {}  # Key to list of occurrences for datasets where coretype = 2
        self.emof_indices = {}  # Key to list of emof
        self.dataprovider_id = None  # The dataset ID from the dataproviders table
        self.imis_das_id = None  # The IMIS dataset ID for querying the eml
        self.eml = None  # Eml as from the http://www.eurobis.org/imis?dasid=<IMIS_DasID>&show=eml API
        self.event_dates_eml = None  # Extract the dates from the EML as last resort
        self.areas = None  # Extract areas from EML (Bounding box do not have useful info - seek advice)
        self.provider_record = None  # Provider record extracted
        self.dataset_name = ""
        self.records_for_lookup = []

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
            self.dataset_name = self.provider_record['name']
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

            # We proceed differently in accordance with the type of CORE record...
            if self.darwin_core_type == self.EVENT:
                for record in records:
                    if record['DarwinCoreType'] == self.OCCURRENCE:
                        self.occurrence_recs.append(record)
                        if record['eventID'] is not None:  # To link we need an eventID
                            # make a key - it must be lined by the eventID
                            key = f"{record['dataprovider_id']}_{record['eventID']}"
                            if key in self.occ_indices:
                                # All the records with this key shall be in a list at 'key'
                                self.occ_indices[key].append(record)
                            else:
                                self.occ_indices[key] = [record]
                    elif record['DarwinCoreType'] == self.EVENT:
                        self.event_recs.append(record)
            else:  # Occurrence records (Datasets with core_type = OCCURRENCE do not have events - verified)
                for record in records:
                    if record['DarwinCoreType'] == self.OCCURRENCE:
                        self.occurrence_recs.append(record)
                    else:  # Should really never happen !!
                        self.event_recs.append(record)

    def get_mof_records(self, das_prov_id):
        """ retrieves measurementorfact records for the dataset in das_id from SQL Server
        NOTE: mof records do not exist for records that have eventID and occurrenceID NULL
        :param das_prov_id"""

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
                key = f"{record['dataprovider_id']}_{'NULL' if record['eventID'] is None else record['eventID']}_" \
                      f"{'NULL' if record['occurrenceID'] is None else record['occurrenceID']}"
                if key in self.emof_indices:
                    # All the records with this key shall be in a list at 'key'
                    self.emof_indices[key].append(record)
                else:
                    self.emof_indices[key] = [record]

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
        self.get_areas_from_eml(self.imis_das_id)

    def get_areas_from_eml(self, imis_das_id):
        """ Given a IMIS Dataset ID, queries the IMIS web servce for  """

        eml = None
        # Where to get IMIS data from
        url = f"http://www.eurobis.org/imis?dasid={imis_das_id}&show=eml"
        eml_detect = "eml:eml"

        response = requests.get(url)

        # NOTE: This API will return 200 even if the record is not found, in that case the area extractor will fail.
        if response.status_code == 200:
            if eml_detect not in response.text:
                return None
            else:
                eml = response.text

        if eml is not None:
            self.areas = extract_area.find_areas(eml)
        else:
            self.areas = None

    @classmethod
    def update_record_qc(cls, records, batch_size):
        # Check DB connection...
        if not mssql.conn:
            mssql.open_db()

        if mssql.conn is None:
            # Should find a way to exit and advice (raise an exception may be)
            return "Fail, no connection "
        else:
            record_count = len(records)
            for record in records:
                # Compose update query
                physloc = bytes.hex(record['physloc'])

                sql_update = f"{cls.sql_update_start}{record['qc']}{cls.sql_update_middle} {record['dataprovider_id']}"
                if record['decimalLatitude'] is not None:
                    sql_update = f"{sql_update}{cls.sql_if_lat}{record['decimalLatitude']}"
                if record['decimalLongitude'] is not None:
                    sql_update = f"{sql_update} {cls.sql_if_lon}{record['decimalLongitude']}"
                sql_update = f"{sql_update} {cls.sql_update_end} 0x{physloc} "

                cursor = mssql.conn.cursor()
                cursor.execute(sql_update)
            try:
                mssql.conn.commit()
                print(f"Records update Count (approx): {cls.record_batch_update_count * batch_size + record_count};")
                cls.record_batch_update_count += 1
                # Should find a way to return with no pain...
                return "Success"
            except Error as e:
                return f"Fail, batch {cls.record_batch_update_count} not updated, exception {str(e)}"
