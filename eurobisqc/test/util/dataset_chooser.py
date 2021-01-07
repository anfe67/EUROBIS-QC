import sys
import PySimpleGUI as sg

from dbworks import mssql_db_functions

this = sys.modules[__name__]

# query the dataset on entering and stores the datasets ...
this.sql_datasets = "SELECT id, name from dataproviders;"
this.names = []
this.dataset_ids = []
this.dataset_name = None
this.dataset_id = None

if mssql_db_functions.conn is None:

    this.conn = mssql_db_functions.open_db()

    if this.conn is not None:
        cursor = this.conn.cursor()
        cursor.execute(this.sql_datasets)
        # Should extract something meaningful from the dataset...
        for row in cursor:
            this.names.append(row[1])
            this.dataset_ids.append(row[0])

    else:
        print("No DB connection!")
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
                values=this.names, enable_events=True, size=(40, 20), key="-DATASET LIST-"
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
            this.dataset_name = values["-DATASET LIST-"][0]
            index = this.names.index(this.dataset_name)
            this.dataset_id = this.dataset_ids[index]

        elif event == "OK":
            if len(values["-DATASET LIST-"]) > 0:
                this.dataset_name = values["-DATASET LIST-"][0]
                index = this.names.index(this.dataset_name)
                this.dataset_id = this.dataset_ids[index]

            run_loop = False
            window.Hide()
        elif event == "Exit" or event == "Cancel":
            run_loop = False
            window.Hide()

        elif event == sg.WIN_CLOSED:
            run_loop = False

    window.Close()
    return this.dataset_id

# get_dataset_chooser()
# print(this.dataset_name)
# print(this.dataset_id)
