from tkinter import *
from tkinter import ttk

def importscr():
    root = Tk()
    root.title("Import via document - ebookbuild")
    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    ttk.Label(mainframe, text="Import via document").grid(columnspan=3, row=1, pady=4)
    ttk.Label(mainframe, text="Choose a file to import (folders and batch import currently unsupported)").grid(column=1, row=2)
    '''ttk.Button(mainframe, text="Import" command=xxx).grid(column=1, row=2)
    ttk.Button(mainframe, text="Export").grid(column=2, row=2)
    ttk.Label(mainframe, text="V0.1").grid(column=1, row=3)
    ttk.Button(mainframe, text="?", command=aboutscr, width=1).grid(column=2, row=3)'''
