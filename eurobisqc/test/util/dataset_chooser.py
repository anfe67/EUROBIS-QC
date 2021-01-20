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
this.sql_datasets = "SELECT id, displayname from dataproviders;"
this.names = []
this.dataset_ids = []
this.dataset_name = None
this.dataset_id = None
this.sel_dataset_names = []
this.sel_dataset_ids = []

if mssql_db_functions.conn is None:

    this.conn = mssql_db_functions.open_db()

    if this.conn is not None:
        cursor = this.conn.cursor()
        cursor.execute(this.sql_datasets)
        # Should extract something meaningful from the dataset...
        for row in cursor:
            this.names.append(f"{row[0]:05d} | {row[1]}")
            # this.dataset_ids.append(row[0])

        this.names.sort()
    else:
        this.logger.error("No DB connection!")
        exit(0)


def get_dataset_chooser():
    """ Simple dataset chooser to test different archives """

    sg.theme("LightGrey1")
    dataset_list_column = [
        [
            sg.Text("DwCA datasets"),
        ],
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

    window = sg.Window("Dataset Chooser", layout)

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
            run_loop = False
            window.Hide()

        elif event == sg.WIN_CLOSED:
            run_loop = False

    window.Close()
    if len(this.sel_dataset_ids):
        return this.sel_dataset_ids, this.sel_dataset_names
    else:
        return this.dataset_id
