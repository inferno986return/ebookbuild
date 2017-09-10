from tkinter import *
from tkinter import ttk
'''import pypandoc

#Debugging info for pypandoc
print(pypandoc.get_pandoc_version())
print(pypandoc.get_pandoc_path())
print(pypandoc.get_pandoc_formats())'''

from tkinter.filedialog import askopenfilename


def openfile():
     
     name = askopenfilename(initialdir="~", defaultextension="Rich Text File" "*.rtf", title="Choose a document...")
     #name = askopenfilename(initialdir="~", filetypes=(("LaTeX Source File", ".tex"), ("Rich Text File", "*.rtf")), title="Choose a file.") #Placeholder for future file extensions.
     open(name)
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
     ttk.Label(mainframe, text="Currently supported file types: .rtf").grid(column=1, row=3)
     ttk.Button(mainframe, text="...", command=openfile).grid(column=2, row=4)
     ttk.Label(mainframe, text=name).grid(column=1, row=4)
     ttk.Button(mainframe, text="OK", command=convertfile).grid(column=1, row=5)
