import os.path
import sys
import PySimpleGUI as sg

this = sys.modules[__name__]
this.filename = None


def get_archive_chooser():
    """ Simple file chooser to test different archives """

    sg.theme("LightGrey1")

    file_list_column = [
        [
            sg.Text("DwCA Folder"),
            sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
            sg.FolderBrowse(),
        ],
        [
            sg.Listbox(
                values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
            )
        ],
    ]

    # For now will only show the name of the file that was chosen
    image_viewer_column = [
        [sg.Text("Choose a DwCA from the list :")],
        [sg.Button("OK"), sg.Button("Cancel")],
    ]

    layout = [
        [
            sg.Column(file_list_column),
            sg.VSeperator(),
            sg.Column(image_viewer_column),
        ]
    ]

    window = sg.Window("DwCa Chooser", layout)

    run_loop = True

    # Simple event loop
    while run_loop:
        event, values = window.read()
        # Folder name was filled in, make a list of (zip)  files in the folder
        if event == "-FOLDER-":
            folder = values["-FOLDER-"]
            try:
                # Get list of files in folder
                file_list = os.listdir(folder)
            except:
                file_list = []

            fnames = [f
                      for f in file_list
                      if os.path.isfile(os.path.join(folder, f))
                      and f.lower().endswith(".zip")
                      ]
            window["-FILE LIST-"].update(fnames)

        elif event == "-FILE LIST-":  # A file was chosen from the listbox
            try:
                this.filename = os.path.join(
                    values["-FOLDER-"], values["-FILE LIST-"][0]
                )

            except:
                pass
        elif event == "OK":
            if len(values["-FILE LIST-"]) > 0:
                this.filename = os.path.join(
                    values["-FOLDER-"], values["-FILE LIST-"][0]
                )
            else:
                this.filename = None
            run_loop = False
            window.Hide()
        elif event == "Exit" or event == "Cancel":
            this.filename = None
            run_loop = False
            window.Hide()
        elif event == event == sg.WIN_CLOSED:
            this.filename = None
            run_loop = False

    window.Close()

    return this.filename
