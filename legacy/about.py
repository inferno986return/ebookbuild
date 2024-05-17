from tkinter import *
from tkinter import ttk

def aboutscr():
    root = Tk()
    root.title("About - ebookbuild")
    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)
    
    ttk.Label(mainframe, text="Version:").grid(columnspan=2, pady=1) #Make these headings bold eventually.
    ttk.Label(mainframe, text="V0.1 - Pre-pre alpha").grid(columnspan=2)
    
    ttk.Label(mainframe, text="Overview:").grid(columnspan=2)
    ttk.Label(mainframe, text="ebookbuild is a FOSS tool designed to assist with e-book production.").grid(columnspan=2)
    
    ttk.Label(mainframe, text="Licensing:").grid(columnspan=2)
    ttk.Label(mainframe, text="ebookbuild is licensed under the GNU General Public License v3 (https://www.gnu.org/licenses/gpl-3.0.en.html)").grid(columnspan=2)
    
    ttk.Label(mainframe, text="Documentation:").grid(columnspan=2)
    ttk.Label(mainframe, text="Currently the only documentation is the provided README.md and PDF file.").grid(columnspan=2)
    
    ttk.Label(mainframe, text="Technologies:").grid(columnspan=2)
    ttk.Label(mainframe, text="ebookbuild currently makes use of the following technologies:").grid(columnspan=2)
    ttk.Label(mainframe, text="Python 3.62").grid(columnspan=2)
    ttk.Label(mainframe, text="Tkinter").grid(columnspan=2)
    
    ttk.Button(mainframe, text="OK", command=root.destroy).grid(columnspan=2)
