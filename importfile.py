from tkinter import *
from tkinter import ttk
import os
import pypandoc

os.environ.setdefault('PYPANDOC_PANDOC', '/home/x/whatever/pandoc')

#Debugging info for pypandoc
print(pypandoc.get_pandoc_version())
print(pypandoc.get_pandoc_path())
print(pypandoc.get_pandoc_formats())

from tkinter.filedialog import askopenfilename


def openfile():

     name = askopenfilename(initialdir="~", filetypes=(("Office 2007+ Open XML Document", "*.docx"), ("OpenDocument Text File", "*.odt"), ("LaTeX Source File", "*.tex"), ("MarkDown Source File", "*.md"), ("DocBook File", "*.docbook")), title="Choose a document...")
     #Will add more extensions in future.
     print(name) #Debugging

def convertfile(name):

     try:
          return pypandoc.convert(name, 'rst')
     except Exception:
          return None

     name.close()
     output.close()

def importfilescr():

     name = "Choose a document..."

     root = Tk()
     root.title("Import via document - ebookbuild")
     mainframe = ttk.Frame(root, padding="3 3 12 12")
     mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
     mainframe.columnconfigure(0, weight=1)
     mainframe.rowconfigure(0, weight=1)

     ttk.Label(mainframe, text="Import via document").grid(columnspan=3, row=1, pady=4)
     ttk.Label(mainframe, text="Choose a file to import (folders and batch import currently unsupported)").grid(column=1, row=2)
     ttk.Label(mainframe, text="Currently supported file types: .docx, .odt, .tex, .md and .docbook").grid(column=1, row=3)
     ttk.Button(mainframe, text="...", command=openfile).grid(column=2, row=4)
     ttk.Label(mainframe, text=name).grid(column=1, row=4)
     ttk.Button(mainframe, text="OK", command=convertfile).grid(column=1, row=5)
     ttk.Button(mainframe, text="Cancel", command=root.destroy).grid(column=1, row=6)
