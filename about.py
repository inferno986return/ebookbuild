from tkinter import *
from tkinter import ttk

def aboutscr():
    root = Tk()
    root.title("About - ebookbuild")
    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    ttk.Label(mainframe, text="About ebookbuild").grid(columnspan=2)
    ttk.Label(mainframe, text="ebookbuild is a free (see GNU Lesser Public License (https://www.gnu.org/licenses/lgpl-3.0.en.html))/ntool designed to assist with e-book production.").grid(column=1, row=2, pady=4)
    ttk.Button(mainframe, text="OK", command=root.destroy).grid(column=2, row=3)
