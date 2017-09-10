from tkinter import *
from tkinter import ttk

from importfile import importfilescr

def chooseimportscr():
    root = Tk()
    root.title("Import - ebookbuild")
    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    ttk.Label(mainframe, text="Import").grid(columnspan=3, row=1, pady=4)
    ttk.Button(mainframe, text="Import via document", command=importfilescr).grid(column=1, row=2)
    ttk.Button(mainframe, text="Import via OCR", state=DISABLED).grid(column=2, row=2) #Currently disabled, will be implemented in a future update using Tesseract.
