""" Simple wrapper to query the WORMS database and provide simple lookup services in SQLite format """

import os
import sys
import atexit
import sqlite3 as lite
import configparser

# this is a pointer to the module object instance itself.
this = sys.modules[__name__]

# Note: inspection at compile time seems to fail here
this.conn = None

# Note: databaseFile is a parameter in resources/config.ini under SQLITEDB
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'resources/config.ini'))
if "SQLITEDB" in config and "databaseFile" in config['SQLITEDB']:
    database_file = config['SQLITEDB']['databaseFile']
else:
    # default
    database_file = 'database/EUROBIS_QC_LOOKUP_DB.db'

this.database_location = os.path.join(os.path.dirname(__file__), database_file)


# Opening the dbworks database
def open_db():
    try:
        db_conn = lite.connect(this.database_location)
        # db_conn.row_factory = lambda cursor, row: row[0]
        return db_conn
    except lite.Error:
        this.conn = None
        return None


# Connection should be opened upon load - do not remove
this.conn = open_db()


# Close it after use
def close_db():
    this.conn.close()
    this.conn = None


def get_fields_of_record(table, field_name, value, fields_sought):
    """ Query the WORMS db and gets a partial record from the database
        :param table - The table to interrogate
        :param field_name: The Columns to interrogate
        :param value : The value sought
        :param fields_sought : The fields to extract

        :returns a dictionary mapped to the fields or None if no record is found
        """

    record = None
    # build a partial string
    fields_sql = ""
    for idx, f in enumerate(fields_sought):
        fields_sql += f"{f} "
        if idx < len(fields_sought) - 1:
            fields_sql += ", "

    cur = this.conn.execute(f"SELECT {fields_sql} from {table} where {field_name}='{value}'")
    retrieved_record = cur.fetchone()
    if retrieved_record is not None:
        record = dict(zip(fields_sought, retrieved_record))

    return record


def get_record(table, field_name, value, fields):
    """ Query the WORMS db and gets a single record from the database
        :param table - The table to interrogate
        :param field_name: The Column to interrogate
        :param value : The value sought
        :param fields : The table columns

        :returns a dictionary mapped to the fields or None if no record is found
        """

    record = None
    cur = this.conn.execute(f"SELECT * from {table} where {field_name}='{value}'")
    retrieved_record = cur.fetchone()
    if retrieved_record is not None:
        record = dict(zip(fields, retrieved_record))

    return record


@atexit.register
def close_down():
    """ Upon unloading the module close the DB connection """

    if this.conn is not None:
        close_db()
