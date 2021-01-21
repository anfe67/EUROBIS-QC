""" This module, through the get_dataset_chooser method, connects to the EUROBIS MS SQL DB and fetches the
    list of dataproviders from the dataproviders table. They are then presented in a list sorted by dataprovider id """

import sys
import logging

import PySimpleGUI as sg

from dbworks import mssql_db_functions

this = sys.modules[__name__]
this.logger = logging.getLogger(__name__)
this.logger.setLevel(logging.DEBUG)
this.logger.addHandler(logging.StreamHandler())

# query the dataset on entering and stores the datasets ...
this.sql_datasets1 = "SELECT id, displayname from dataproviders;"

# Alternate query: This query selects datasets containinng records with 0 or
this.sql_datasets2 = "select d.id, d.displayname, d.rec_count  " \
                     "from eurobis e inner join dataproviders d on e.dataprovider_id = d.id " \
                     "where e.qc = 0 or e.qc is NULL group by d.id, d.displayname, d.rec_count"

this.names = []
this.dataset_ids = []
this.dataset_name = None
this.dataset_id = None
this.sel_dataset_names = []
this.sel_dataset_ids = []

this.exit = False


def grab_datasets(sql_string):
    if mssql_db_functions.conn is None:
        this.conn = mssql_db_functions.open_db()

    if this.conn is not None:
        cursor = this.conn.cursor()
        cursor.execute(sql_string)
        # Should extract something meaningful from the dataset...
        for row in cursor:
            this.names.append(f"{row[0]:05d} | {row[1]}")
            # this.dataset_ids.append(row[0])

        this.names.sort()
        return this.names
    else:
        this.logger.error("No DB connection!")
        exit(0)


grab_datasets(this.sql_datasets1)


def get_dataset_chooser():
    """ Simple dataset chooser to test different archives """

    sg.theme("LightGrey1")
    dataset_list_column = [
        [
            sg.Text("DwCA datasets"),
        ],
        [sg.Radio('Get all datasets', "RADIO", default=True, size=(10, 1), key="RADIO1"),
         sg.Radio('Datasets with records not labeled', "RADIO", key="RADIO2"), sg.Button("Reload List")],
        [
            sg.Listbox(
                values=this.names,
                enable_events=True,
                size=(100, 40), key="-DATASET LIST-",
                select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED
            )
        ],
        [sg.Button("OK"), sg.Button("Cancel")],
    ]

    layout = [
        [
            sg.Column(dataset_list_column),
        ]
    ]

    window = sg.Window("Dataset Chooser", layout).Finalize()

    run_loop = True

    # Simple event loop
    while run_loop:
        event, values = window.read()

        if event == "-DATASET LIST-":  # A dataset was chosen from the listbox

            if len(values["-DATASET LIST-"]) > 0:
                # First selected Dataset if one exists
                this.dataset_name = values["-DATASET LIST-"][0]
                index = int(this.dataset_name[0:6])
                this.dataset_id = index

                this.sel_dataset_ids = []
                this.sel_dataset_names = []

                if len(values["-DATASET LIST-"]) > 1:
                    for sel in values["-DATASET LIST-"]:
                        this.sel_dataset_ids.append(int(sel[0:6]))
                        this.sel_dataset_names.append(sel[7:])

        elif event == "OK":
            if len(values["-DATASET LIST-"]) > 0:
                # First selected Dataset if one exists
                this.dataset_name = values["-DATASET LIST-"][0]
                index = int(this.dataset_name[0:6])
                this.dataset_id = index

                this.sel_dataset_ids = []
                this.sel_dataset_names = []

                if len(values["-DATASET LIST-"]) > 1:
                    for sel in values["-DATASET LIST-"]:
                        this.sel_dataset_ids.append(int(sel[0:6]))
                        this.sel_dataset_names.append(sel[7:])

            run_loop = False
            window.Hide()
        elif event == "Exit" or event == "Cancel":
            this.exit = True
            run_loop = False
            window.Hide()
        elif event == "Reload List":
            this.names = []
            if values['RADIO1']:
                this.names = grab_datasets(this.sql_datasets1)
            else:
                this.names = grab_datasets(this.sql_datasets2)

            window.FindElement('-DATASET LIST-').Update(values=this.names)

        elif event == sg.WIN_CLOSED:
            run_loop = False

    window.Close()
    if this.exit:
        sys.exit(0)
    if len(this.sel_dataset_ids):
        return this.sel_dataset_ids, this.sel_dataset_names
    else:
        return this.dataset_id
