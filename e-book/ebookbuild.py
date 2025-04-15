#!/usr/bin/env python

# ebookbuild.py v0.9 - Generates a EPUB 2.0.1 file using data from metadata.json, now with lxml.

# This file is part of the ebookbuild project (also known as Project Zylon) which is licensed under GNU General Public License v3.0 (GNU GPLv3): https://www.gnu.org/licenses/gpl-3.0.en.html

import os, datetime, json, zipfile, hashlib, re
from lxml import etree

# Intro text
print(
    """
======================================================
ebookbuild 2.0.1, v1.0 - Copyright (C) 2025 Hal Motley
https://www.github.com/inferno986return/ebookbuild/
======================================================

NOTE: This program creates legacy EPUB files! Please use ebookbuild-3.3.py to create compliant EPUB 3.3 files that are recommended by the W3C.

ebookbuild is a program is designed to do one thing well. It is a Python 3 script that uses the lxml library to create fully-compliant EPUB 2.0.1 files that pass epubcheck and can be read with most e-readers including: Amazon Kindle, Google Play Books, Apple Books, Kobo, Nook, etc.

Not working? Try installing lxml via pip with 'pip install lxml'.

The v1.0 release includes support for infinite heading nesting in the toc.ncx but you should use up to 4 at most. There is also support for .html files as they are supported within EPUB 2.0.1 for the sake of completion but I don't recommend using them over .xhtml.

This program comes with ABSOLUTELY NO WARRANTY, for details see GPL-3.txt.
This is free software and you are welcome to redistribute it under certain conditions.

All trademarks belong to their respective owners.
"""
)

# JSON extraction
with open("metadata.json", "r") as json_file:
    data = json.load(json_file)

def GenOPF():
    # Get current UTC time in ISO format
    utctime = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()

    # Define reflowable and fixed layout text presentation options
    reflowable = ("Reflowable", "reflowable", "reflow", "r")
    fixed_layout = ("Fixed layout", "Fixed Layout", "fixed layout", "fixed", "f")

    # Create the root package element
    package = etree.Element("package", attrib={"xmlns": "http://www.idpf.org/2007/opf", "unique-identifier": "bookid", "version": "2.0"})

    # Create the metadata element with namespaces
    metadata = etree.SubElement(
        package,
        "metadata",
        nsmap={"dc": "http://purl.org/dc/elements/1.1/", "opf": "http://www.idpf.org/2007/opf"},
    )

    # Add metadata elements using data from metadata.json
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}title").text = data["title"]
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}creator").text = data["creator"]
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}subject").text = data["subject"]
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}publisher").text = data["publisher"]
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}identifier", id="bookid").text = data["ISBN"]
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}date").text = utctime
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}language").text = data["language"]
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}rights").text = data["rights"]
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}description").text = data["description"]
    etree.SubElement(metadata, "meta", content="cover", name="cover")

    # Handle fixed layout metadata if applicable
    if data["textPresentation"] in fixed_layout:
        etree.SubElement(metadata, "meta", name="fixed-layout", content="true")
        print("e-book type: Fixed layout")
    elif data["textPresentation"] in reflowable:
        print("e-book type: Reflowable")
    else:
        print("Invalid textPresentation in metadata.json.")

    # Create the manifest element
    manifest = etree.SubElement(package, "manifest")

    # Add the NCX item to the manifest
    etree.SubElement(manifest, "item", attrib={"href": "toc.ncx", "id": "ncx", "media-type": "application/x-dtbncx+xml"})

    # Add CSS files to the manifest
    cssindex = 0
    for subdir, dirs, files in os.walk(data["containerFolder"] + os.sep + data["cssFolder"]):
        for file in files:
            if file.endswith(".css"):
                filepath = os.path.join(subdir, file).replace(data["containerFolder"] + os.sep, "")
                etree.SubElement(manifest, "item", attrib={"href": filepath, "id": f"css{cssindex}", "media-type": "text/css"})
                print(os.path.join(subdir, file))
                cssindex += 1

    # Add image files to the manifest
    imageindex = 0
    for subdir, dirs, files in os.walk(data["containerFolder"] + os.sep + data["imagesFolder"]):
        for file in files:
            filepath = os.path.join(subdir, file).replace(data["containerFolder"] + os.sep, "")

            if file == data["epubCover"]:
                if file.lower().endswith((".jpg", ".jpeg", ".jpe")):
                    etree.SubElement(manifest, "item", attrib={"href": filepath, "id": "cover", "media-type": "image/jpeg"})
                elif file.lower().endswith((".png")):
                    etree.SubElement(manifest, "item", attrib={"href": filepath, "id": "cover", "media-type": "image/png"})
                elif file.lower().endswith((".gif")):
                    etree.SubElement(manifest, "item", attrib={"href": filepath, "id": "cover", "media-type": "image/gif"})
                print(os.path.join(subdir, file))

            else:
                if file.lower().endswith((".jpg", ".jpeg", ".jpe")):
                    etree.SubElement(manifest, "item", attrib={"href": filepath, "id": f"image{imageindex}", "media-type": "image/jpeg"})
                elif file.lower().endswith((".png")):
                    etree.SubElement(manifest, "item", attrib={"href": filepath, "id": f"image{imageindex}", "media-type": "image/png"})
                elif file.lower().endswith((".gif")):
                    etree.SubElement(manifest, "item", attrib={"href": filepath, "id": f"image{imageindex}", "media-type": "image/gif"})
                print(os.path.join(subdir, file))
                imageindex += 1

    # Add page files to the manifest
    for page in data["pages"]:
        page_id = page["fileName"].replace(".xhtml", "").replace(".html", "") # Remove both extensions
        page_id = re.sub(r"^\d+", "", page_id)
        page_id = re.sub(r"\-", "", page_id)
        media_type = "application/xhtml+xml" if page["fileName"].endswith(".xhtml") else "application/xhtml+xml" if page["fileName"].endswith(".html") else "application/xhtml+xml" # Default to xhtml
        etree.SubElement(manifest, "item", attrib={"href": page["fileName"], "id": page_id, "media-type": media_type})

    # Add font files to the manifest
    fontindex = 0
    for subdir, dirs, files in os.walk(data["containerFolder"] + os.sep + data["fontsFolder"]):
        for file in files:
            filepath = os.path.join(subdir, file).replace(data["containerFolder"] + os.sep, "")
            if file.lower().endswith(".ttf"):
                etree.SubElement(manifest, "item", attrib={"href": filepath, "id": f"font{fontindex}", "media-type": "font/truetype"})
                print(os.path.join(subdir, file))
                fontindex += 1
            elif file.lower().endswith(".otf"):
                etree.SubElement(manifest, "item", attrib={"href": filepath, "id": f"font{fontindex}", "media-type": "font/opentype"})
                print(os.path.join(subdir, file))
                fontindex += 1

    # Create the spine element
    spine = etree.SubElement(package, "spine", toc="ncx")

    # Add page references to the spine
    for page in data["pages"]:
        page_id = page["fileName"].replace(".xhtml", "").replace(".html", "") # Remove both extensions
        page_id = re.sub(r"^\d+", "", page_id)
        page_id = re.sub(r"\-", "", page_id)
        etree.SubElement(spine, "itemref", idref=page_id)

    # Create the guide element if enabled
    if data["enableGuide"] == "true":
        guide = etree.SubElement(package, "guide")
        etree.SubElement(guide, "reference", type="text", href=data["startReadingfile"], title=data["startReadingpage"])
        etree.SubElement(guide, "reference", type="toc", href=data["tocFile"], title=data["tocPage"])
        etree.SubElement(guide, "reference", type="cover", href=data["frontCoverfile"], title=data["frontCoverpage"])

    # Write the XML to content.opf
    tree = etree.ElementTree(package)
    tree.write(data["containerFolder"] + os.sep + "content.opf", encoding="utf-8", xml_declaration=True, pretty_print=True)

# Function to generate toc.ncx using lxml
def GenNCX():
    # Create the root ncx element
    ncx = etree.Element("ncx", xmlns="http://www.daisy.org/z3986/2005/ncx/", version="2005-1")
    # Create the head element
    head = etree.SubElement(ncx, "head")
    etree.SubElement(head, "meta", name="dtb:uid", content=data["ISBN"])

    # Determine the maximum depth for the NCX (this is now less important for generation, but kept for metadata)
    maxdepth = 1  # We'll calculate this dynamically, but keep a default
    etree.SubElement(head, "meta", name="dtb:depth", content=str(maxdepth))
    etree.SubElement(head, "meta", name="dtb:totalPageCount", content="0")
    etree.SubElement(head, "meta", name="dtb:maxPageNumber", content="0")

    # Create the docTitle element
    doc_title = etree.SubElement(ncx, "docTitle")
    etree.SubElement(doc_title, "text").text = data["titleShort"]

    # Create the navMap element
    nav_map = etree.SubElement(ncx, "navMap")

    index = 1

    def add_nav_point(parent, item, play_order, current_depth):
        nonlocal index  # To modify the outer 'index'
        nav_point = etree.SubElement(parent, "navPoint", id=f"navpoint-{index}", playOrder=str(index))
        nav_label = etree.SubElement(nav_point, "navLabel")
        etree.SubElement(nav_label, "text").text = item["pageName"]
        nav_point_content = etree.SubElement(nav_point, "content", src=item["fileName"])

        index += 1
        nonlocal maxdepth  # To modify the outer 'maxdepth'
        maxdepth = max(maxdepth, current_depth)

        if "subheadings" in item:
            sub_index = 1 # Added sub_index to ensure unique playOrder within subheadings
            for subitem in item["subheadings"]:
                add_nav_point(nav_point, subitem, play_order + sub_index, current_depth + 1)
                sub_index += 1

    current_index = 1
    for page in data["pages"]:
        add_nav_point(nav_map, page, current_index, 1)

    etree.SubElement(head, "meta", name="dtb:depth", content=str(maxdepth))

    # Write the XML to toc.ncx
    tree = etree.ElementTree(ncx)
    tree.write(data["containerFolder"] + os.sep + "toc.ncx", encoding="utf-8", xml_declaration=True, pretty_print=True)

# Function to create META-INF and container.xml
def GenMetadata():
    # Create the mimetype file
    with open("mimetype", "w") as mime:
        mime.write("application/epub+zip")

    # Create the META-INF directory if it doesn't exist
    if not os.path.exists("META-INF"):
        print("Create META-INF")
        os.makedirs("META-INF", exist_ok=True)
 
    if not os.path.exists("META-INF/container.xml"):
        container = etree.Element(
        "container",
        version="1.0",
        xmlns="urn:oasis:names:tc:opendocument:xmlns:container",  # Correct namespace
        )

        rootfiles = etree.SubElement(container, "rootfiles")
        etree.SubElement(rootfiles, "rootfile", attrib={"full-path": data["containerFolder"] + "/content.opf", "media-type": "application/oebps-package+xml"})

        tree = etree.ElementTree(container)
        tree.write("META-INF" + os.sep + "container.xml", encoding="utf-8", xml_declaration=True, pretty_print=True,)

# Function to generate the EPUB file
def GenEpub():
    # Create the EPUB zip file
    with zipfile.ZipFile(data["fileName"] + ".epub", mode="w", compression=zipfile.ZIP_STORED) as zf:
        zf.write("mimetype")

        for dirname, subdirs, files in os.walk("META-INF"):
            zf.write(dirname)
            for filename in files:
                if filename != ".DS_Store":
                    zf.write(os.path.join(dirname, filename))
                    print("dirname:" + dirname)
                    print("filename:" + filename)

        for dirname, subdirs, files in os.walk(data["containerFolder"]):
            zf.write(dirname)
            for filename in files:
                if filename != ".DS_Store":
                    zf.write(os.path.join(dirname, filename))
                    print("dirname:" + dirname)
                    print("filename:" + filename)

    # Validate the generated zip file
    with open(data["fileName"] + ".epub", "rb") as f:
        if zipfile.is_zipfile(f) is True:
            print("ZIP file is valid.")

# Function to generate and display checksums
def GenChksum():
    # Check if checksum generation is enabled
    enable_checksums = ("True", "true", "Yes", "yes", "Y", "y")

    if data["enableChecksums"] in enable_checksums:
        # Get current UTC time in ISO format
        utctime = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(" ")

        # Create hash objects
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()
        sha512 = hashlib.sha512()

        # Read the EPUB file and update the hash objects
        with open(data["fileName"] + ".epub", "rb") as afile:
            buffer = afile.read()

            md5.update(buffer)
            sha256.update(buffer)
            sha512.update(buffer)

        # Print checksums to the console
        print(
            f"""
    -This output is saved to checksums.txt-
                
    WARNING: MD5 is cryptographically weak and is not recommended for verifying file integrity! Use SHA-256 or SHA-512 instead.
                    
    Checksum values for {data["fileName"]}.epub on {str(utctime)} UTC
    ==========================================================

    MD5: {md5.hexdigest()}
    SHA-256: {sha256.hexdigest()}
    SHA-512: {sha512.hexdigest()}
                
            """
        )

        # Write checksums to checksums.txt
        with open("checksums.txt", "w") as chksum:
            chksum.write("Checksum values for " + data["fileName"] + ".epub on " + str(utctime) + "UTC" + "\n\n")
            chksum.write("WARNING: MD5 is cryptographically weak and is not recommended for verifying file integrity! Use SHA-256 or SHA-512 instead.\n\n")
            chksum.write("=================================================================================\n\n")
            chksum.write("MD5: " + md5.hexdigest() + "\n")
            chksum.write("SHA-256: " + sha256.hexdigest() + "\n")
            chksum.write("SHA-512: " + sha512.hexdigest() + "\n")

# Call the functions to generate the EPUB
GenOPF()
GenNCX()
GenMetadata()
GenEpub()
GenChksum()