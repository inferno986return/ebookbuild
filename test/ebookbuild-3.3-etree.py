# ebookbuild-oop-3.3.py - Create EPUB 3.3-compliant files

import os, datetime, json, zipfile, hashlib, re
import xml.etree.ElementTree as ET

# intro text
print("""
=================================================================
ebookbuild, v1.0 - Copyright (C) 2024 Hal Motley
https://www.github.com/inferno986return/ebookbuild/
=================================================================
This script is designed for Python v3.6+ and may do weird things if run in an older version of Python!

The UNIX philosophy is to "do one thing and do it well":

* Use this script (ebookbuild-3.3.py) to generate a compliant EPUB 3.3 file.
* Use the old script (ebookbuild.py) to generate a compliant legacy EPUB 2.0.1 file.

This program comes with ABSOLUTELY NO WARRANTY, for details see GPL-3.txt.
This is free software and you are welcome to redistribute it under certain conditions.

""")

# How can I make this brutally simple and efficient?

with open("metadata.json") as json_file: #JSON extraction magic
    data = json.load((json_file)) # Removed OrderedDict - Python 3.6+

def gen_mimetypes(): # Generate all the mimetypes
     
    #Dictionaries to map file extensions to their MIME types - see 3.2 Core media types of EPUB 3.3 standard
    imageformats = {".gif":"image/gif", ".jpe":"image/jpeg", ".jpg":"image/jpeg", ".jpeg":"image/jpeg", ".png":"image/png", ".svg":"image/svg+xml", ".webp":"image/webp"}
    fontformats = {".otf":"font/opentype", ".ttf":"font/truetype", ".woff":"font/woff", ".woff2":"font/woff2"}
    webformats = {".css":"text/css", ".xhtml":"application/xhtml+xml"}
    audioformats = {".mp3":"audio/mpeg", ".mp4":"audio/mp4", ".ogg":"audio/ogg; codecs=opus"}
    xmlformats = {".ncx":"application/x-dtbncx+xml", "meta-inf":"application/oebps-package+xml"}
    epubformat = {".epub":"application/epub+zip"}

    #Combine those dictionaries into one big dictionary
    mimetypes = {**imageformats, **fontformats, **webformats, **audioformats, **xmlformats, **epubformat}

    return mimetypes

def gen_opf(mimetypes): # Generate the .opf file, such as: content.opf, package.opf, etc.
    print(mimetypes)

def gen_ncx(mimetypes): # Generate a toc.ncx to provide legacy support for older e-readers
    
    doctype = '<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd"><ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">\n'

    tree = ET.ElementTree() # Create an ElementTree object

    container = ET.Element("container", version="1.0", xmlns="urn:oasis:names:tc:opendocument:xmlns:container") # Create the root element



    tree.write("toc.ncx", encoding="utf-8", xml_declaration=True)

def meta_inf(mimetypes): #Files which assist EPUB readers with recognising the EPUB file - i.e. that the META-INF, mimetype and container.xml files are present

        try: #Check if mimetype already exists
            os.stat("mimetype")

        except: #Generate the mimetype.
            mime = open("mimetype", "w")
            mime.write(mimetypes[".epub"])
            mime.close()

        try: # Check the META-INF folder is present
            os.stat("META-INF")

        except:
            os.mkdir("META-INF")
 
        tree = ET.ElementTree() # Create an ElementTree object

        container = ET.Element("container", version="1.0", xmlns="urn:oasis:names:tc:opendocument:xmlns:container") # Create the root element

        rootfiles = ET.SubElement(container, "rootfiles") # Add rootfiles element
        ET.SubElement(rootfiles, "rootfile", full_path=data["containerFolder"] + "/" + data["opfFile"], media_type=mimetypes["meta-inf"])

        tree._setroot(container) # Set the tree's root

        output_path = os.path.join("META-INF", "container.xml")
        tree.write(output_path, encoding="UTF-8", xml_declaration=True) # Write the XML to a file

def gen_epub(): # Add the files and folders recursively to create an EPUB file

def gen_checksums(): # Generate and show MD5, SHA256 and SHA512 checksums for the ePub using hashlib

    utctime = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(' ')

    md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    sha512 = hashlib.sha512()

    with open(data["fileName"] + ".epub", 'rb') as afile:
        buffer = afile.read()

        md5.update(buffer)
        sha256.update(buffer)
        sha512.update(buffer)

        # Seperates the checksum output from the files going into the book.
        print()
        print("-This output is saved to checksums.txt-\n")
        print(f"Checksum values for {data["fileName"]}.epub on {str(utctime)} UTC")
        print("=============================================================================\n")
        print(f"MD5: {md5.hexdigest()}")
        print(f"SHA-256: {sha256.hexdigest()}")
        print(f"SHA-512: {sha512.hexdigest()}")

        chksum = open("checksums.txt", "w")

        chksum.write("Checksum values for " + data["fileName"] + ".epub on " + str(utctime) + "UTC" + "\n")
        chksum.write("=================================================================================\n")
        chksum.write("\n")

        chksum.write(f"MD5: {md5.hexdigest()}\n")
        chksum.write(f"SHA-256: {sha256.hexdigest()}\n")
        chksum.write(f"SHA-512: {sha512.hexdigest()}\n")


# Run the functions
mimetypes = gen_mimetypes()
gen_opf(mimetypes)
gen_ncx(mimetypes)
meta_inf(mimetypes)
gen_epub()
gen_checksums()