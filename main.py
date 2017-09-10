from tkinter import *
from tkinter import ttk

from chooseimport import chooseimportscr
from about import aboutscr

def mainscr():
    root = Tk()
    root.title("ebookbuild")
    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    ttk.Label(mainframe, text="Welcome to ebookbuild").grid(columnspan=3, row=1, pady=4)
    ttk.Button(mainframe, text="Import", command=chooseimportscr).grid(column=1, row=2)
    ttk.Button(mainframe, text="Export").grid(column=2, row=2)
    ttk.Label(mainframe, text="V0.1").grid(column=1, row=3)
    ttk.Button(mainframe, text="?", command=aboutscr, width=1).grid(column=2, row=3)

mainscr()
