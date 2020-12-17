""" To build a system of database lookup tables for some
    specific fields, based on a set of text files in resources
     text files must have the Lookup suffix (camel case) """

import sys
import os
from lookupdb import db_functions

this = sys.modules[__name__]
this.resources_dir = None


def import_files():
    """ Looks for files in resources and build database lookup tables """

    this.resources_dir = os.path.join(os.path.dirname(__file__), 'resources')

    resource_files = [f for f in os.listdir(this.resources_dir) if os.path.isfile(os.path.join(this.resources_dir, f))]

    for file_name in resource_files:
        if 'Lookup' in file_name:
            table_name = file_name.split('Lookup')[0]
        else:
            continue

        # Get connection to the DB
        if db_functions.conn is None:
            db_functions.open_db()

        # If table exists in the DB, drop it
        db_functions.conn.execute(f"drop table if exists {table_name};")

        # Create the table
        q_str = f"CREATE TABLE {table_name} ('Value' TEXT)"

        db_functions.conn.execute(q_str)

        with open(os.path.join(this.resources_dir, file_name), 'r') as f:
            lines = f.readlines()

            for line in lines:
                if line.strip() != "" and line.strip()[0] != '#':
                    # Add lookup value to the table
                    q_str = f"insert into {table_name}(Value) values('{line.strip().lower()}')"
                    db_functions.conn.execute(q_str)

    db_functions.conn.commit()

    if db_functions.conn is not None:
        db_functions.close_db()

# import_files()
