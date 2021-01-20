from distutils.util import strtobool
import sys
import os
import atexit
import configparser
import logging

this = sys.modules[__name__]

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'resources/config.ini'))

this.conn = None
this.database = None
this.driver = None
this.username = None
this.password = None
this.port = None
this.server = None
this.server_local = True

this.logger = logging.getLogger(__name__)

if "SQLSERVERDB" in config:
    try:
        this.driver = config['SQLSERVERDB']['driver']
        this.server = config['SQLSERVERDB']['server']
        this.port = config['SQLSERVERDB']['port']
        this.database = config['SQLSERVERDB']['database']
        this.username = config['SQLSERVERDB']['username']
        this.password = config['SQLSERVERDB']['password']
        this.drivermodule = config['SQLSERVERDB']['drivermodule']
        # Used in multiprocess examples
        this.server_local = bool(strtobool(config['SQLSERVERDB']['server_local']))

        if this.drivermodule == 'pymssql':
            import pymssql as db_driver
        elif this.drivermodule == 'pyodbc':
            import pyodbc as db_driver

    except (KeyError, ValueError):
        # Some Parameters cannot be loaded or are missing - Should find clean exit strategy
        this.logger.error("Some MSSQL configuration parameters are missing. Needed: Driver Name, server address, port, "
                          "database name, username, password and drivermodule (pymssql or pyodbc) "
                          "and server_local (True or False).")
        exit(1)
else:
    this.logger.error("The SQLSERVERDB section is not in the config file. Please add it if you what to "
                      "connect to teh MS SQL eurobis Database.")
    # Parameters cannot be loaded - no point in continuing
    exit(1)

# Build a connection string
this.connection_string = f'DRIVER={this.driver};' \
                         f'PORT={this.port};' \
                         f'SERVER={this.server};' \
                         f'DATABASE={this.database};' \
                         f'UID={this.username};' \
                         f'PWD={this.password}'


def open_db():
    """ Opens a DB, the parameters are already loaded from the configuration file
        upon importing the module
        """
    try:
        if this.drivermodule == 'pymssql':
            this.conn = db_driver.connect(server=this.server, user=this.username, password=this.password,
                                          database=this.database)
        else:
            this.conn = db_driver.connect(this.connection_string)
        return this.conn
    except db_driver.Error as ex:
        # The connection is not initialized, log the exception message
        sqlstate = ex.args[1]
        this.logger.error(sqlstate)
        this.conn = None
        return None


def close_db():
    """ Closes the DB after use, automatically called upon module exit """
    try :
        if this.conn is not None:
            this.conn.close()
    except :
        pass
    finally:
        this.conn = None


@atexit.register
def close_down():
    """ Upon unloading the module close the DB connection """

    if this.conn is not None:
        close_db()
