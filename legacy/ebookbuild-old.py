#!/usr/bin/env python

#ebookbuild.py v0.82.3 - Generates an ePub file using data from the metadata.json.

#This file is part of the ebookbuild project (also known as Project Zylon) which is licensed under GNU General Public License v3.0 (GNU GPLv3): https://www.gnu.org/licenses/gpl-3.0.en.html

#opf = "OEBPS/content.opf"
#ncx = "OEBPS/toc.ncx"

# remove time from import

import os, datetime, json, zipfile, hashlib, re
# from collections import OrderedDict

#Intro text
print(f"""
================================================
ebookbuild, v0.82.3 - Copyright (C) 2025 Hal Motley
https://www.github.com/inferno986return/ebookbuild/
================================================

This program comes with ABSOLUTELY NO WARRANTY, for details see GPL-3.txt.
This is free software and you are welcome to redistribute it under certain conditions.

""")

#JSON extraction magic
with open("metadata.json") as json_file:
    data = json.load((json_file)) # Removed OrderedDict - Python 3.6+

#Create a compatible content.opf from scratch.
def GenOPF():
    utctime = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    reflowable = ("Reflowable", "reflowable", "reflow", "r")
    fixed_layout = ("Fixed layout", "Fixed Layout", "fixed layout", "fixed", "f")

    opf = open(data["containerFolder"] + os.sep + "content.opf", "w", encoding="utf-8")

    opf.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
    opf.write('<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid" version="2.0">\n')

    #Metadata tags
    opf.write('\t<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">\n')
    opf.write('\t\t<dc:title>' + data["title"] + '</dc:title>\n')
    opf.write('\t\t<dc:creator>' + data["creator"] + '</dc:creator>\n')
    opf.write('\t\t<dc:subject>' + data["subject"] + '</dc:subject>\n')
    opf.write('\t\t<dc:publisher>' + data["publisher"] + '</dc:publisher>\n')
    opf.write('\t\t<dc:identifier id="bookid">' + data["ISBN"] + '</dc:identifier>\n')
    opf.write('\t\t<dc:date>' + utctime + '</dc:date>\n') #Date and time using ISO 8601 to ensure a unique checksum (YYYY-MM-DDThh:mm:ss)
    opf.write('\t\t<dc:language>' + data["language"] + '</dc:language>\n')
    opf.write('\t\t<dc:rights>' + data["rights"] + '</dc:rights>\n')
    opf.write('\t\t<dc:description>' + data["description"] + '</dc:description>\n')
    opf.write('\t\t<meta content="cover" name="cover"/>\n')

    #Fixed (non-reflowable) support
    if (data["textPresentation"] in reflowable):
        print('e-book type: Reflowable')

    elif (data["textPresentation"] in fixed_layout):
        opf.write('\t\t<meta name="fixed-layout" content="true"/>\n')
        print('e-book type: Fixed layout')

    else:
        print('Invalid textPresentation in metadata.json.')

    opf.write('\t</metadata>\n')

    #Manifest tags
    opf.write('\t<manifest>\n')

    #Write out the CSS files
    cssindex = 0

    for subdir, dirs, files in os.walk(data["containerFolder"] + os.sep + data["cssFolder"]):
        for file in files:
            filepath = subdir + os.sep + file
            correctfilepath = filepath.replace(data["containerFolder"] + os.sep, "") #removes the redudant OEBPS

            if filepath.endswith(".css"):
                opf.write('\t\t<item href="' + correctfilepath + '" id="css' + str(cssindex) + '" media-type="text/css"/>\n')
                print (filepath)
                cssindex += 1

    #Write out the NCX and cover image files
    opf.write('\t\t<item href="toc.ncx" id="ncx" media-type="application/x-dtbncx+xml"/>\n')
    #opf.write('\t\t<item href="'+ data["imagesFolder"] + '/' + data["epubCover"] +'" id="main_cover_image" media-type="image/jpeg"/>\n') #Removes duplicate output, leaving commented as I might it later for the Kindle covers.

    #Write out the images

    imageindex = 0

    for subdir, dirs, files in os.walk(data["containerFolder"] + os.sep + data["imagesFolder"]):

        for file in files:
            filepath = subdir + os.sep + file
            correctfilepath = filepath.replace(data["containerFolder"] + os.sep, "") #removes the redudant OEBPS

            jpeg_files = (".jpg", ".JPG", ".jpeg", ".JPEG", ".jpe", ".JPE")
            png_files = (".png", ".PNG")
            gif_files = (".gif", ".GIF")

            if file == data["epubCover"]:

                if filepath.endswith(jpeg_files):
                    opf.write('\t\t<item href="' + correctfilepath + '" id="cover" media-type="image/jpeg"/>\n')
                    print (filepath)

                elif filepath.endswith(png_files):
                    opf.write('\t\t<item href="' + correctfilepath + '" id="cover" media-type="image/png"/>\n')
                    print (filepath)

                elif filepath.endswith(gif_files):
                    opf.write('\t\t<item href="' + correctfilepath + '" id="cover" media-type="image/gif"/>\n')
                    print (filepath)
                    imageindex += 1

            if file != data["epubCover"]:

                if filepath.endswith(jpeg_files):
                    opf.write('\t\t<item href="' + correctfilepath + '" id="image' + str(imageindex) + '" media-type="image/jpeg"/>\n')
                    print (filepath)
                    imageindex += 1

                elif filepath.endswith(png_files):
                    opf.write('\t\t<item href="' + correctfilepath + '" id="image' + str(imageindex) + '" media-type="image/png"/>\n')
                    print (filepath)
                    imageindex += 1

                elif filepath.endswith(gif_files):
                    opf.write('\t\t<item href="' + correctfilepath + '" id="image' + str(imageindex) + '" media-type="image/gif"/>\n')
                    print (filepath)
                    imageindex += 1

    #Write out all the pages in the book.
    #Count all the instances within the pages block.

    currentpage = 0
    totalpages = len(data["pages"]) #Number of pages

    while currentpage != totalpages: #Write out all the xhtml files as declared in the JSON.
        pageid = data["pages"][currentpage]["fileName"] #remove capital letters and spaces from the id attribute (works with Unicode)
        correctpageid = pageid.replace(".xhtml","")

        #Need to remove invalid characters such as numbers and hyphens from id. This does work, though files shouldn't start with numbers anyway.
        if re.match(r"^\d+", correctpageid):
            correctpageid = re.sub(r"^\d+", "", correctpageid)

        if re.match(r"\-", correctpageid):
            correctpageid = re.sub(r"\-", "", correctpageid)

        opf.write('\t\t<item href="' + data["pages"][currentpage]["fileName"] + '" id="' + correctpageid + '" media-type="application/xhtml+xml"/>\n')
        currentpage += 1

    #Write out all the custom fonts in the book.

    fontindex = 0

    for subdir, dirs, files in os.walk(data["containerFolder"] + os.sep + data["fontsFolder"]):
        for file in files:
            filepath = subdir + os.sep + file
            correctfilepath = filepath.replace(data["containerFolder"] + os.sep, "") #removes the redudant OEBPS

            ttf_files = (".ttf", ".TTF")
            otf_files = (".otf", ".OTF")

            if filepath.endswith(ttf_files):
                opf.write('\t\t<item href="' + correctfilepath + '" id="font' + str(fontindex) + '" media-type="font/truetype"/>\n')
                print (filepath)
                fontindex += 1

            elif filepath.endswith(otf_files):
                opf.write('\t\t<item href="' + correctfilepath + '" id="font' + str(fontindex) + '" media-type="font/opentype"/>\n')
                print (filepath)
                fontindex += 1

    opf.write('\t</manifest>\n')

    #Spine tags
    opf.write('\t<spine toc="ncx">\n')

    #Write out all the filenames in order again as declared in the JSON.

    currentpage = 0
    totalpages = len(data["pages"]) #Number of pages

    while currentpage != totalpages: #Write out all the xhtml files as declared in the JSON.
        pageid = data["pages"][currentpage]["fileName"] #remove capital letters and spaces from the id attribute (works with Unicode)
        correctpageid = pageid.replace(".xhtml", "") #pageid.replace(" & ", " "), pageid.replace("'", "&quot;"), pageid.replace('"', "&dquot;"), pageid.replace('<', "&lt;"), pageid.replace('>', "&gt;") #Remove the characters disallowed for ID in XML.

        #Need to remove invalid characters such as numbers and hyphens from id. This does work, though files shouldn't start with numbers anyway.
        if re.match(r"^\d+", correctpageid):
            correctpageid = re.sub(r"^\d+", "", correctpageid)

        if re.match(r"\-", correctpageid):
            correctpageid = re.sub(r"\-", "", correctpageid)

        opf.write('\t\t<itemref idref="' + correctpageid + '"/>\n')
        currentpage += 1

    opf.write('\t</spine>\n')

    #Write the guide tags - need to make these optional
    if data["enableGuide"] == "true":
        opf.write('\t<guide>\n')
        opf.write('\t\t<reference type="text" ' + 'href="' + data["startReadingfile"] + '" ' + 'title="' + data["startReadingpage"] + '"/>\n')
        # <reference type="text" href="pages/page001.html" title="Front Page"/>
        opf.write('\t\t<reference type="toc" ' + 'href="' + data["tocFile"] + '" ' + 'title="' + data["tocPage"] + '"/>\n')
        # <reference type="toc" href="pages/page005.html" title="Contents"/>
        opf.write('\t\t<reference type="cover" ' + 'href="' + data["frontCoverfile"] + '" ' + 'title="' + data["frontCoverpage"] + '"/>\n')
        # <reference type="cover" href="titlepage.xhtml" title="Cover"/>
        opf.write('\t</guide>\n')

    #End of file
    opf.write('</package>')

    #Eventually save directly to the OEBPS folder
    opf.close()

#Create a compatible toc.ncx from scratch.
def GenNCX():

    ncx = open(data["containerFolder"] + os.sep + "toc.ncx", "w", encoding="utf-8")

    ncx.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
    ncx.write('<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd"><ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">\n')

    #Head tags
    ncx.write('<head>\n')
    ncx.write('\t<meta name="dtb:uid" content="' + data["ISBN"] + '" />\n') #Has to be the same as dc:identifier.

    #Declare the maximum amount of indentation from 1 to 4.

    indentations = [] #Assemble a Python list (array) with all the indentations and take the largest number.
    currentpage = 0
    totalpages = len(data["pages"]) #Number of pages

    while currentpage != totalpages:
        indentations.append(data["pages"][currentpage]["indentation"])
        maxdepth = max(indentations)
        currentpage += 1

    ncx.write('\t<meta name="dtb:depth" content="' + str(maxdepth) + '" />\n')
    ncx.write('\t<meta name="dtb:totalPageCount" content="0" />\n')
    ncx.write('\t<meta name="dtb:maxPageNumber" content="0" />\n')
    ncx.write('</head>\n')

    #Doctitle tags
    ncx.write('<docTitle>\n')
    ncx.write('\t<text>' + data["titleShort"] + '</text>\n')
    ncx.write('</docTitle>\n')

    #Write out the NavMap tags (and their children)
    ncx.write('<navMap>\n')

    currentpage = 0
    index = 1
    totalpages = len(data["pages"]) #Number of pages

    while currentpage != totalpages: #Write out all the xhtml files as declared in the JSON, indendation currently unsupported (data["pages"][currentpage]["indentation"].
        ncx.write('\t<navPoint id="navpoint-' + str(index) + '" playOrder="' + str(index) + '">\n') #id=001 class=h1 playOrder=1
        ncx.write('\t\t<navLabel>\n')
        ncx.write('\t\t\t<text>' + data["pages"][currentpage]["pageName"] + '</text>\n')
        ncx.write('\t\t</navLabel>\n')
        ncx.write('\t\t<content src="' + data["pages"][currentpage]["fileName"] + '" />\n')

    #Write out the page's anchor tags.
        try:
            currentanchor = 0
            totalanchors = len(data["pages"][currentpage]["anchorNames"])

            while currentanchor != totalanchors:
                index += 1

                ncx.write('\t\t<navPoint id="navpoint-' + str(index) + '" playOrder="' + str(index) + '">\n') #id=001 class=h1 playOrder=1
                ncx.write('\t\t\t\t<navLabel>\n')
                ncx.write('\t\t\t\t\t<text>' + data["pages"][currentpage]["anchorNames"]["anchorName" + str(currentanchor) + ""] + '</text>\n')
                ncx.write('\t\t\t\t</navLabel>\n')
                ncx.write('\t\t\t\t<content src="'+ data["pages"][currentpage]["fileName"] + data["pages"][currentpage]["anchorLinks"]["anchorLink" + str(currentanchor) + ""] + '" />\n')
                ncx.write('\t\t</navPoint>\n')

                currentanchor += 1

            print('Added anchor tags to page ' + str(currentpage) + ', ' + data["pages"][currentpage]["fileName"] + '.')

        except KeyError:
            print('Skipped page ' + str(currentpage) + ', ' + data["pages"][currentpage]["fileName"] + ' as it had no anchor tags.')

        ncx.write('\t</navPoint>\n')

        currentpage += 1
        index += 1

    ncx.write('</navMap>\n')

    #End of file
    ncx.write('</ncx>')

def GenEpub():
#GenEpub.py - Generates an .epub file from the data provided.
#Ideally with no errors or warnings from epubcheck (needs to be implemented, maybe with the Python wrapper).

    #Generate the mimetype.
    mime = open("mimetype", "w")

    mime.write('application/epub+zip')

    mime.close()

    #Generate the META-INF.
    try:
        os.stat('META-INF')

    except:
        os.mkdir('META-INF')

    metainf = open('META-INF' + os.sep + "container.xml", "w")

    metainf.write('<?xml version="1.0"?>\n')
    metainf.write('<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n')
    metainf.write('\t<rootfiles>\n')
    metainf.write('\t\t<rootfile full-path="' + data["containerFolder"] + '/content.opf" media-type="application/oebps-package+xml" />\n')
    metainf.write('\t</rootfiles>\n')
    metainf.write('</container>')

    metainf.close()

    #The ePub standard requires deflated compression and a compression order.
    zf = zipfile.ZipFile(data["fileName"] + '.epub', mode='w', compression=zipfile.ZIP_STORED)

    zf.write('mimetype')

    for dirname, subdirs, files in os.walk('META-INF'):
        zf.write(dirname)
        for filename in files:
            if filename != '.DS_Store': #epubcheck hates uninvited files and macOS places these everywhere.
                    zf.write(os.path.join(dirname, filename))
                    print('dirname:' + dirname)
                    print('filename:' + filename)

    for dirname, subdirs, files in os.walk(data["containerFolder"]):
        zf.write(dirname)
        for filename in files:
            if filename != '.DS_Store': #epubcheck hates uninvited files
                zf.write(os.path.join(dirname, filename))
                print('dirname:' + dirname)
                print('filename:' + filename)

    zf.close()

    #zipfile has a built-in validator for debugging
    with open(data["fileName"] + '.epub', 'r') as f:
        if zipfile.is_zipfile(f) is True:
            print("ZIP file is valid.")

#Extra debugging information
#print(getinfo.compress_type(zf))
#print(getinfo.compress_size(zf))
#print(getinfo.file_size(zf))

def GenChksum():
#Generate and show MD5 and SHA512 checksums for the ePub using hashlib
    enable_checksums = ["True", "true", "Yes", "yes", "Y", "y"]

    if data["enableChecksums"] in enable_checksums:
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
            print(f"""
    -This output is saved to checksums.txt-
                  
    WARNING: MD5 is cryptographically weak and is not recommended for verifying file integrity! Use SHA-256 or SHA-512 instead.
              
    Checksum values for {data["fileName"]}.epub on {str(utctime)} UTC
    ==========================================================

    MD5: {md5.hexdigest()}
    SHA-256: {sha256.hexdigest()}
    SHA-512: {sha512.hexdigest()}
            """)

            chksum = metainf = open("checksums.txt", "w")

            chksum.write("Checksum values for " + data["fileName"] + ".epub on " + str(utctime) + "UTC" + "\n\n")

            chksum.write("WARNING: MD5 is cryptographically weak and is not recommended for verifying file integrity! Use SHA-256 or SHA-512 instead.\n\n")

            chksum.write("=================================================================================\n\n")

            chksum.write("MD5: " + md5.hexdigest() + "\n")
            chksum.write("SHA-256: " + sha256.hexdigest() + "\n")
            chksum.write("SHA-512: " + sha512.hexdigest() + "\n")


GenOPF()
GenNCX()
GenEpub()
GenChksum()
