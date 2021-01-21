""" This module is a simple graphical file chooser used to pick a directory where
    a set of DwCA files is stored, nothing more """

import os.path
import sys

import PySimpleGUI as sg

this = sys.modules[__name__]
this.filename = None
this.foldername = None


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
            sg.Listbox(values=[], enable_events=True, size=(40, 20), key="-FILE LIST-")
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
            except os.error:
                file_list = []

            fnames = [f
                      for f in file_list
                      if os.path.isfile(os.path.join(folder, f))
                      and f.lower().endswith(".zip")
                      ]

            window.FindElement("-FILE LIST-").Update(values=fnames)

        elif event == "-FILE LIST-":  # A file was chosen from the listbox
            try:
                this.filename = os.path.join(
                    values["-FOLDER-"], values["-FILE LIST-"][0]
                )

            except os.error:
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
        elif event == sg.WIN_CLOSED:
            this.filename = None
            run_loop = False

    window.Close()
    return this.filename


def browse_for_folder():
    layout = [[sg.Text('Select Directory')],
              [sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"), sg.FolderBrowse()],
              [sg.Button('OK'), sg.Button('Cancel')]]

    # event1, values1 = sg.Window('Window Title', layout).read(close=True)
    window = sg.Window('Folder Browser', layout)
    run_loop = True
    while run_loop:
        event, values = window.read()
        if event == 'OK':
            this.foldername = values["-FOLDER-"]
            window.Hide()
            run_loop = False
        elif event == "Exit" or event == "Cancel" or event == sg.WIN_CLOSED:
            this.foldername = None
            window.Hide()
            run_loop = False
        elif event == "FOLDER":
            this.foldername = values["-FOLDER-"]

    window.Close()
    return this.foldername
