#!/usr/bin/env python

# ebookbuild.py v1.5.0 - Generates an EPUB 3.3 file using data from metadata.json, now with lxml, orjson, and modular minification/CSS purging.

# This file is part of the ebookbuild project (also known as Project Zylon) which is licensed under GNU General Public License v3.0 (GNU GPLv3): https://www.gnu.org/licenses/gpl-3.0.en.html

import os, datetime, zipfile, hashlib, re
import orjson
from lxml import etree

# Intro text
print(
    """
======================================================
ebookbuild 3.3, v1.5.0 - Copyright (C) 2026 Hal Motley
https://www.github.com/inferno986return/ebookbuild/
======================================================

NOTE: This program creates EPUB 3.3 files that are recommended by the W3C!

This script uses the lxml and orjson libraries to create fully-compliant
EPUB 3.3 files that pass epubcheck and can be read with most e-readers.

Not working? Try installing the dependencies:
    * lxml - 'pip install lxml'
    * orjson - 'pip install orjson'

This program comes with ABSOLUTELY NO WARRANTY; for details see the license.
This is free software, and you are welcome to redistribute it
under certain conditions. All trademarks belong to their respective owners.
"""
)

# JSON extraction with orjson for performance
try:
    with open("metadata.json", "rb") as json_file:
        data = orjson.loads(json_file.read())
except FileNotFoundError:
    print("FATAL ERROR: metadata.json not found. The script cannot continue.")
    exit()


def create_page_id(filename):
    """Generates a clean, consistent ID from a page filename."""
    page_id = filename.split('#')[0].replace(".xhtml", "").replace(".html", "")
    page_id = page_id.replace("-", "")
    return page_id


def GenOPF(output_dir, data):
    """Generate the content.opf file for EPUB 3.3."""
    opf_filename = data.get("opfName", "content.opf")
    print(f"Generating {opf_filename}...")
    utctime = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

    nsmap = {
        "dc": "http://purl.org/dc/elements/1.1/",
        None: "http://www.idpf.org/2007/opf"
    }

    package = etree.Element("package", attrib={"unique-identifier": "bookid", "version": "3.0"}, nsmap=nsmap)
    metadata = etree.SubElement(package, "metadata")

    # --- METADATA ---
    identifier_el = etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}identifier", id="bookid")
    identifier_el.text = data["ISBN"]
    etree.SubElement(metadata, "meta", refines="#bookid", property="identifier-type", scheme="xsd:string").text = "ISBN"

    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}title").text = data["title"]

    i = 1
    while True:
        creator_key = f"creator{i}"
        role_key = f"creator{i}Role"
        if creator_key in data:
            creator_id = f"creator{i}"
            etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}creator", id=creator_id).text = data[creator_key]
            if role_key in data:
                etree.SubElement(metadata, "meta", refines=f"#{creator_id}", property="role", scheme="marc:relators").text = data[role_key]
            i += 1
        else:
            break

    i = 1
    while True:
        contrib_key = f"contributor{i}"
        role_key = f"contributor{i}Role"
        if contrib_key in data:
            contrib_id = f"contributor{i}"
            etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}contributor", id=contrib_id).text = data[contrib_key]
            if role_key in data:
                etree.SubElement(metadata, "meta", refines=f"#{contrib_id}", property="role", scheme="marc:relators").text = data[role_key]
            i += 1
        else:
            break

    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}publisher").text = data["publisher"]
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}language").text = data["language"]
    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}rights").text = data["rights"]

    if data.get("date"):
        etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}date").text = data["date"]

    if data.get("sourceUrn") and data.get("sourceISBN"):
        urn_type = data["sourceUrn"].lower()
        source_id = data["sourceISBN"]
        source_urn = f"urn:{urn_type}:{source_id}"
        etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}source").text = source_urn

    etree.SubElement(metadata, "{http://purl.org/dc/elements/1.1/}description").text = data["description"]
    
    # dcterms:modified is required by EPUB 3.3
    etree.SubElement(metadata, "meta", property="dcterms:modified").text = utctime

    if ("collection" in data and
        bool(data["collection"].get("enableCollection")) and
        all(k in data["collection"] for k in ["name", "type", "position"])):
        collection_data = data["collection"]
        etree.SubElement(metadata, "meta", property="belongs-to-collection", id="collection").text = collection_data["name"]
        etree.SubElement(metadata, "meta", refines="#collection", property="collection-type").text = collection_data["type"]
        etree.SubElement(metadata, "meta", refines="#collection", property="group-position").text = str(collection_data["position"])
        if collection_data.get("fileAs"):
            etree.SubElement(metadata, "meta", refines="#collection", property="file-as").text = collection_data["fileAs"]
        if collection_data.get("alternativeScript"):
            etree.SubElement(metadata, "meta", refines="#collection", property="alternate-script").text = collection_data["alternativeScript"]

    etree.SubElement(metadata, "meta", name="cover", content="cover-image")

    # --- THE ELEGANT ARCHITECTURE: MANIFEST & SPINE ---

    # 1. Asset Definitions (with .js added)
    SUPPORTED_ASSETS = {
        ".xhtml": "application/xhtml+xml", ".html": "application/xhtml+xml",
        ".css": "text/css", ".js": "application/javascript",
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".gif": "image/gif", ".svg": "image/svg+xml", ".webp": "image/webp", ".ttf": "font/truetype",
        ".otf": "font/opentype", ".woff": "font/woff", ".woff2": "font/woff2", ".mp3": "audio/mpeg",
        ".mp4": "video/mp4", ".m4a": "audio/mp4", ".m4v": "video/mp4", ".opus": "audio/opus",
        ".pls": "application/pls+xml", ".smil": "application/smil+xml"
    }

    # 2. Build the File Registry (Single Source of Truth)
    manifest_registry = {}  # Maps filepath -> unique_id
    asset_counters = {}
    
    # Pre-register reserved IDs mapping to your metadata
    manifest_registry[data["navDocFile"]] = "nav"
    if bool(data.get("enableNcx")):
        manifest_registry["toc.ncx"] = "ncx"

    epub_cover_filename = data.get("epubCover")

    # Walk the directory ONCE to index all actual files
    for dirpath, _, filenames in os.walk(output_dir):
        for file in sorted(filenames):
            ext = os.path.splitext(file)[1].lower()
            if ext in SUPPORTED_ASSETS:
                href_path = os.path.relpath(os.path.join(dirpath, file), output_dir).replace(os.sep, '/')
                
                if href_path not in manifest_registry:
                    if epub_cover_filename and file == epub_cover_filename:
                        manifest_registry[href_path] = "cover-image"
                    else:
                        prefix = ext.strip('.')
                        idx = asset_counters.get(prefix, 0)
                        manifest_registry[href_path] = f"{prefix}{idx}"
                        asset_counters[prefix] = idx + 1

    # 3. Generate Manifest using the Registry
    manifest = etree.SubElement(package, "manifest")
    for href, item_id in manifest_registry.items():
        ext = os.path.splitext(href)[1].lower()
        media_type = "application/x-dtbncx+xml" if item_id == "ncx" else SUPPORTED_ASSETS.get(ext, "application/xhtml+xml")
        
        attrs = {"id": item_id, "href": href, "media-type": media_type}
        
        if item_id == "nav":
            attrs["properties"] = "nav"
        elif item_id == "cover-image":
            attrs["properties"] = "cover-image"
            
        etree.SubElement(manifest, "item", **attrs)

    # 4. Generate Spine by querying the Registry
    spine_attrs = {}
    if bool(data.get("enableNcx")):
        spine_attrs['toc'] = 'ncx'
        
    spine = etree.SubElement(package, "spine", **spine_attrs)
    seen_spine_items = set()

    def process_spine_items(items):
        for item in items:
            base_filename = item["fileName"].split('#')[0]
            
            if base_filename not in seen_spine_items:
                item_id = manifest_registry.get(base_filename)
                if item_id:
                    itemref = etree.SubElement(spine, "itemref", idref=item_id)
                    if item.get("type") == "cover":
                        itemref.set("linear", "no")
                else:
                    print(f"  -> WARNING: Spine item '{base_filename}' missing from output folder. Excluded from OPF.")
                
                seen_spine_items.add(base_filename)
            
            if "subheadings" in item and item["subheadings"]:
                process_spine_items(item["subheadings"])

    process_spine_items(data["pages"])

    tree = etree.ElementTree(package)
    output_path = os.path.join(output_dir, opf_filename)
    tree.write(output_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)


def GenNav(output_dir, data):
    """Generate the nav.xhtml file required by EPUB 3."""
    print("Generating nav.xhtml...")
    
    def build_nav_list(parent_ol, items):
        for item in items:
            li = etree.SubElement(parent_ol, "li")
            etree.SubElement(li, "a", href=item["fileName"]).text = item["pageName"]
            if "subheadings" in item and item["subheadings"]:
                nested_ol = etree.SubElement(li, "ol")
                build_nav_list(nested_ol, item["subheadings"])

    nav_html = etree.Element("html", nsmap={None: "http://www.w3.org/1999/xhtml", "epub": "http://www.idpf.org/2007/ops"})
    head = etree.SubElement(nav_html, "head")
    etree.SubElement(head, "title").text = data["tocTitle"]
    body = etree.SubElement(nav_html, "body")
    
    nav = etree.SubElement(body, "nav", **{"{http://www.idpf.org/2007/ops}type": "toc", "id": "toc"})
    etree.SubElement(nav, "h1").text = data["tocTitle"]
    ol = etree.SubElement(nav, "ol")
    build_nav_list(ol, data["pages"])

    if bool(data.get("enableGuide")):
        landmarks_nav = etree.SubElement(body, "nav", **{"{http://www.idpf.org/2007/ops}type": "landmarks", "id": "landmarks"})
        etree.SubElement(landmarks_nav, "h1").text = "Landmarks"
        landmarks_ol = etree.SubElement(landmarks_nav, "ol")
        
        cover_li = etree.SubElement(landmarks_ol, "li")
        etree.SubElement(cover_li, "a", **{
            "{http://www.idpf.org/2007/ops}type": "cover", 
            "href": data["frontCoverfile"]
        }).text = data["frontCoverpage"]
        
        toc_li = etree.SubElement(landmarks_ol, "li")
        etree.SubElement(toc_li, "a", **{
            "{http://www.idpf.org/2007/ops}type": "toc", 
            "href": data["tocFile"]
        }).text = data["tocPage"]
        
        start_li = etree.SubElement(landmarks_ol, "li")
        etree.SubElement(start_li, "a", **{
            "{http://www.idpf.org/2007/ops}type": "bodymatter", 
            "href": data["startReadingfile"]
        }).text = data["startReadingpage"]

    tree = etree.ElementTree(nav_html)
    output_path = os.path.join(output_dir, data["navDocFile"])
    tree.write(output_path, encoding="UTF-8", xml_declaration=True, pretty_print=True, doctype='<!DOCTYPE html>')


def GenNCX(output_dir, data):
    """Generate the toc.ncx file for backward compatibility."""
    if not bool(data.get("enableNcx")):
        print("Skipping toc.ncx generation as 'enableNcx' is false.")
        return
        
    print("Generating toc.ncx...")
    ncx = etree.Element("ncx", xmlns="http://www.daisy.org/z3986/2005/ncx/", version="2005-1")
    head = etree.SubElement(ncx, "head")
    etree.SubElement(head, "meta", name="dtb:uid", content=data["ISBN"])
    etree.SubElement(head, "meta", name="dtb:totalPageCount", content="0")
    etree.SubElement(head, "meta", name="dtb:maxPageNumber", content="0")
    
    doc_title = etree.SubElement(ncx, "docTitle")
    etree.SubElement(doc_title, "text").text = data["titleShort"]
    nav_map = etree.SubElement(ncx, "navMap")
    
    play_order_counter, max_depth = 1, 0
    def add_nav_point(parent, item, current_depth):
        nonlocal play_order_counter, max_depth
        nav_point = etree.SubElement(parent, "navPoint", id=f"navpoint-{play_order_counter}", playOrder=str(play_order_counter))
        nav_label = etree.SubElement(nav_point, "navLabel")
        etree.SubElement(nav_label, "text").text = item["pageName"]
        etree.SubElement(nav_point, "content", src=item["fileName"])
        play_order_counter += 1
        max_depth = max(max_depth, current_depth)
        if "subheadings" in item and item["subheadings"]:
            for subitem in item["subheadings"]:
                add_nav_point(nav_point, subitem, current_depth + 1)

    for page in data["pages"]:
        add_nav_point(nav_map, page, 1)
        
    etree.SubElement(head, "meta", name="dtb:depth", content=str(max_depth))
    tree = etree.ElementTree(ncx)
    output_path = os.path.join(output_dir, "toc.ncx")
    tree.write(output_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)


def GenPackagingFiles(data):
    """Check, inspect, and create the mimetype and container.xml files if needed."""
    print("Checking container metadata...")
    
    mimetype_content = "application/epub+zip"
    write_mimetype = True
    if os.path.exists("mimetype"):
        with open("mimetype", "r") as f:
            if f.read() == mimetype_content:
                print("  - mimetype file is already correct. Leaving it alone.")
                write_mimetype = False
            else:
                print("  - WARNING: mimetype file is incorrect. Overwriting.")
    if write_mimetype:
        print("  - Creating mimetype file.")
        with open("mimetype", "w") as mime:
            mime.write(mimetype_content)

    meta_inf_dir = "META-INF"
    container_path = os.path.join(meta_inf_dir, "container.xml")
    os.makedirs(meta_inf_dir, exist_ok=True)
    
    opf_filename = data.get("opfName", "content.opf")
    expected_path = f"{data['containerFolder']}/{opf_filename}"
    write_container = True
    if os.path.exists(container_path):
        try:
            tree = etree.parse(container_path)
            ns = {'c': 'urn:oasis:names:tc:opendocument:xmlns:container'}
            rootfile = tree.find('c:rootfiles/c:rootfile', namespaces=ns)
            if rootfile is not None and rootfile.get('full-path') == expected_path:
                print("  - container.xml is already correct. Leaving it alone.")
                write_container = False
            else:
                print("  - WARNING: container.xml has incorrect path. Overwriting.")
        except etree.XMLSyntaxError:
            print("  - WARNING: container.xml is malformed. Overwriting.")
            
    if write_container:
        print("  - Creating container.xml.")
        container = etree.Element("container", version="1.0", xmlns="urn:oasis:names:tc:opendocument:xmlns:container")
        rootfiles = etree.SubElement(container, "rootfiles")
        etree.SubElement(rootfiles, "rootfile", **{"full-path": expected_path, "media-type": "application/oebps-package+xml"})
        tree = etree.ElementTree(container)
        tree.write(container_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)


# ==============================================================================
# IN-MEMORY ASSET MINIFICATION & CSS CLASS PURGING PIPELINE
# ==============================================================================

def CollectUsedCSSClasses(source_dir):
    """
    Scans all XHTML, HTML, and SVG files in the container directory
    and returns a set of all CSS class names actually used in the markup.
    """
    used_classes = set()
    markup_exts = {".xhtml", ".html", ".svg"}

    for dirname, _, files in os.walk(source_dir):
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext in markup_exts:
                filepath = os.path.join(dirname, filename)
                try:
                    tree = etree.parse(filepath)
                    for class_attr in tree.xpath("//@class"):
                        for cls in class_attr.split():
                            used_classes.add(cls.strip())
                except Exception:
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            for match in re.findall(r'class\s*=\s*["\']([^"\']+)["\']', f.read()):
                                used_classes.update(match.split())
                    except Exception:
                        pass

    print(f"  -> Indexed {len(used_classes)} active CSS classes across markup files.")
    return used_classes


def PurgeUnusedCSS(css_text, used_classes):
    """
    Parses CSS rules (including nested @media / @supports blocks) and strips out
    any selector—or entire rule block—that references an unused CSS class.
    Preserves comments if removeCSSComments is false.
    """
    # Temporarily mask comments with placeholders so braces inside comments don't break parsing
    comments = []
    def save_comment(match):
        comments.append(match.group(0))
        return f"__COMMENT_{len(comments) - 1}__"

    masked_css = re.sub(r'/\*[\s\S]*?\*/', save_comment, css_text)

    def filter_selector_group(selector_group):
        kept_selectors = []
        for sel in selector_group.split(','):
            sel_clean = sel.strip()
            if not sel_clean:
                continue
            # Ignore comment placeholders when checking class names
            sel_no_comments = re.sub(r'__COMMENT_\d+__', '', sel_clean).strip()
            if not sel_no_comments:
                kept_selectors.append(sel_clean)
                continue

            classes_in_sel = re.findall(r'\.([a-zA-Z_][a-zA-Z0-9_-]*)', sel_no_comments)
            if all(c in used_classes for c in classes_in_sel):
                kept_selectors.append(sel_clean)
        return ", ".join(kept_selectors)

    def process_block(text):
        out = []
        i = 0
        n = len(text)
        while i < n:
            next_brace = text.find('{', i)
            next_semi = text.find(';', i)

            if next_semi != -1 and (next_brace == -1 or next_semi < next_brace):
                stmt = text[i:next_semi+1].strip()
                if stmt:
                    out.append(stmt)
                i = next_semi + 1
                continue

            if next_brace == -1:
                rem = text[i:].strip()
                if rem:
                    out.append(rem)
                break

            selector = text[i:next_brace].strip()

            depth = 1
            j = next_brace + 1
            while j < n and depth > 0:
                if text[j] == '{':
                    depth += 1
                elif text[j] == '}':
                    depth -= 1
                j += 1

            body = text[next_brace+1:j-1]

            # Check if selector (ignoring leading comment placeholders) is an @-rule
            sel_stripped = re.sub(r'^(?:__COMMENT_\d+__\s*)*', '', selector)
            if sel_stripped.startswith('@'):
                if any(sel_stripped.startswith(at) for at in ('@media', '@supports', '@layer', '@container')):
                    inner_purged = process_block(body).strip()
                    if inner_purged:
                        out.append(f"{selector} {{\n{inner_purged}\n}}")
                else:
                    out.append(f"{selector} {{{body}}}")
            else:
                filtered_sel = filter_selector_group(selector)
                if filtered_sel:
                    out.append(f"{filtered_sel} {{{body}}}")

            i = j

        return "\n".join(out)

    purged = process_block(masked_css)

    # Restore original comments
    for idx, comm in enumerate(comments):
        purged = purged.replace(f"__COMMENT_{idx}__", comm)

    return purged


def ProcessAndMinifyAsset(filepath, ext, data, used_classes=None):
    """
    Reads an EPUB text asset, applies the modular minification, comment removal,
    CSS class purging, and copyright injection rules from metadata.json, and returns bytes.
    """
    # Native boolean flags from metadata.json (defaults to False if omitted)
    xhtml_copyright  = bool(data.get("insertXHTMLCopyright", False))
    xhtml_whitespace = bool(data.get("minifyXHTMLWhitespace", False))
    xhtml_comments   = bool(data.get("removeXHTMLComments", False))

    css_copyright    = bool(data.get("injectCSSCopyright", False))
    css_whitespace   = bool(data.get("minifyCSSWhitespace", False))
    css_comments     = bool(data.get("removeCSSComments", False))
    css_classes      = bool(data.get("stripUnusedCSSClasses", False))

    js_copyright     = bool(data.get("insertJSCopyright", False))
    js_whitespace    = bool(data.get("minifyJSWhitespace", False))
    js_comments      = bool(data.get("removeJSComments", False))

    # Support both "copyrightNotice" and "copyrightNotice:"
    copyright_text = (data.get("copyrightNotice") or data.get("copyrightNotice:") or "").strip()

    xml_based_exts = {".xhtml", ".html", ".xml", ".opf", ".ncx", ".svg", ".smil", ".pls"}

    # --- 1. XHTML / XML ASSETS ---
    if ext in xml_based_exts:
        is_xhtml = ext in {".xhtml", ".html"}                      # <--- NEW: Check if file is XHTML/HTML
        epub_version = float(data.get("epubVersion", 3.3))         # <--- NEW: Read numeric epubVersion

        # Added 'is_xhtml' here so XHTML headers are still normalized even if all minification flags are false
        if not (is_xhtml or xhtml_copyright or xhtml_whitespace or xhtml_comments or css_classes):
            with open(filepath, "rb") as f:
                return f.read()

        try:
            parser = etree.XMLParser(
                remove_blank_text=xhtml_whitespace,
                remove_comments=xhtml_comments,
                resolve_entities=False
            )
            tree = etree.parse(filepath, parser)

            # <--- NEW: Normalize <html> namespaces, <head> meta tags, doctype, and XML declaration --->
            if is_xhtml:
                tree, profile = NormalizeXHTMLHeader(tree, epub_version)
                xml_decl = profile["xml_decl"]
                doctype = profile["doctype"]
            else:
                xml_decl = '<?xml version="1.0" encoding="UTF-8"?>'
                doctype = None
            # <---------------------------------------------------------------------------------------->

            for elem in tree.iter():
                tag_name = etree.QName(elem).localname if isinstance(elem.tag, str) else ""
                
                if xhtml_whitespace and tag_name not in ("pre", "code", "script", "style", "textarea"):
                    if elem.text and elem.text.strip():
                        elem.text = re.sub(r'\s+', ' ', elem.text)
                    if elem.tail and elem.tail.strip():
                        elem.tail = re.sub(r'\s+', ' ', elem.tail)
                
                # Apply CSS minification/purging rules to inline <style> blocks
                elif tag_name == "style" and elem.text:
                    style_css = elem.text
                    if css_classes and used_classes is not None:
                        style_css = PurgeUnusedCSS(style_css, used_classes)
                    if css_comments:
                        style_css = re.sub(r'/\*[\s\S]*?\*/', '', style_css)
                    if css_whitespace:
                        style_css = re.sub(r'\s+', ' ', style_css)
                        style_css = re.sub(r'\s*([\{\};:,>~+])\s*', r'\1', style_css)
                        style_css = re.sub(r';\}', '}', style_css).strip()
                    elem.text = style_css

            # (Removed the old hardcoded `doctype = ...` line from here since it's set above)
            
            body_bytes = etree.tostring(
                tree,
                encoding="UTF-8",
                xml_declaration=False,
                pretty_print=not xhtml_whitespace,
                doctype=doctype
            )

            header = f"{xml_decl}\n"                               # <--- NEW: Uses dynamic xml_decl (2.0.1 vs 3.2+)
            if xhtml_copyright and copyright_text:
                header += f'<!-- {copyright_text} -->\n'

            return header.encode("utf-8") + body_bytes

        except Exception as e:
            print(f"    [!] XML processing fallback for {filepath}: {e}")
            with open(filepath, "rb") as f:
                return f.read()

    # --- 2. CSS ASSETS ---
    if ext == ".css":
        if not (css_copyright or css_whitespace or css_classes or css_comments):
            with open(filepath, "rb") as f:
                return f.read()

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if css_classes and used_classes is not None:
            content = PurgeUnusedCSS(content, used_classes)

        if css_comments:
            content = re.sub(r'/\*[\s\S]*?\*/', '', content)

        if css_whitespace:
            content = re.sub(r'\s+', ' ', content)
            content = re.sub(r'\s*([\{\};:,>~+])\s*', r'\1', content)
            content = re.sub(r';\}', '}', content)
            content = content.strip()

        if css_copyright and copyright_text:
            content = f"/* {copyright_text} */\n{content}"

        return content.encode("utf-8")

    # --- 3. JAVASCRIPT ASSETS ---
    if ext == ".js":
        if not (js_copyright or js_whitespace or js_comments):
            with open(filepath, "rb") as f:
                return f.read()

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if js_comments:
            content = re.sub(r'/\*[\s\S]*?\*/', '', content)
            content = re.sub(r'(?<!:)//.*$', '', content, flags=re.MULTILINE)

        if js_whitespace:
            lines = [line.strip() for line in content.splitlines() if line.strip()]
            content = '\n'.join(lines)
            content = re.sub(r'[ \t]*([\{\};,=+\-*/<>!&|?:])[ \t]*', r'\1', content)

        if js_copyright and copyright_text:
            content = f"/* {copyright_text} */\n{content}"

        return content.encode("utf-8")

    with open(filepath, "rb") as f:
        return f.read()


def GenEpub(data):
    """Generate the EPUB file from the project contents."""
    print("\nPackaging EPUB file...")
    epub_filename = data["fileName"] + ".epub"
    source_dir = data["containerFolder"]
    compress_level = int(data.get("compressionLevel", 9))

    # Only scan markup for CSS classes if stripUnusedCSSClasses is enabled
    used_classes = None
    if bool(data.get("stripUnusedCSSClasses", False)):
        print("Scanning XHTML files for active CSS classes...")
        used_classes = CollectUsedCSSClasses(source_dir)

    processable_exts = {".xhtml", ".html", ".css", ".js", ".xml", ".opf", ".ncx", ".svg", ".smil", ".pls"}

    with zipfile.ZipFile(epub_filename, mode="w", compression=zipfile.ZIP_STORED) as zf:
        zf.write("mimetype", arcname="mimetype")
        
    with zipfile.ZipFile(epub_filename, mode="a", compression=zipfile.ZIP_DEFLATED, compresslevel=compress_level) as zf:
        if os.path.isdir("META-INF"):
            container_path = "META-INF/container.xml"
            zf.writestr(container_path, ProcessAndMinifyAsset(container_path, ".xml", data, used_classes))
        
        for dirname, _, files in os.walk(source_dir):
            for filename in sorted(files):
                full_path = os.path.join(dirname, filename)
                arcname = full_path.replace("\\", "/")
                ext = os.path.splitext(filename)[1].lower()
                
                if ext in processable_exts:
                    print(f"  - Zipping: {arcname}")
                    zf.writestr(arcname, ProcessAndMinifyAsset(full_path, ext, data, used_classes))
                else:
                    print(f"  - Zipping: {arcname}")
                    zf.write(full_path, arcname)
                
    if zipfile.is_zipfile(epub_filename):
        print(f"\nEPUB file '{epub_filename}' created successfully.")
    else:
        print(f"\nError: '{epub_filename}' is not a valid ZIP file.")


def GenChksum(data):
    """Generate checksums for the final EPUB file."""
    if not bool(data.get("enableChecksums")):
        print("\nChecksum generation disabled. Skipping.")
        return
        
    print("\nGenerating checksums...")
    epub_filename = data["fileName"] + ".epub"
    utctime = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(" ")
    md5, sha256, sha512 = hashlib.md5(), hashlib.sha256(), hashlib.sha512()
    
    with open(epub_filename, "rb") as afile:
        buffer = afile.read()
        md5.update(buffer)
        sha256.update(buffer)
        sha512.update(buffer)
        
    checksum_output = f"""-This output is saved to checksums.txt-

WARNING: MD5 is cryptographically weak. Use SHA-256 or SHA-512 instead.

Checksum values for {epub_filename} on {str(utctime)} UTC
=======================================================================

MD5: {md5.hexdigest()}
SHA-256: {sha256.hexdigest()}
SHA-512: {sha512.hexdigest()}
"""
    print(checksum_output)
    with open("checksums.txt", "w") as chksum:
        chksum.write(checksum_output)


def GenMetainf(data):
    """Runs the main build process for the e-book."""
    try:
        oebps_dir = data["containerFolder"]
        if not os.path.isdir(oebps_dir):
             raise FileNotFoundError(f"The container folder '{oebps_dir}' does not exist.")

        # 1. Check/create packaging metadata (mimetype, container.xml)
        GenPackagingFiles(data)

        # 2. Generate/overwrite files directly in the OEBPS folder
        GenOPF(oebps_dir, data)
        GenNav(oebps_dir, data)
        GenNCX(oebps_dir, data)

        # 3. Package the contents into the .epub file (with on-the-fly minification)
        GenEpub(data)
        
        # 4. Generate checksum for the final .epub file
        GenChksum(data)
        
        print("\nAll tasks completed successfully!")
    
    except FileNotFoundError as e:
        print("\n" + "="*70)
        print(">>> A FILE NOT FOUND ERROR OCCURRED! SCRIPT HALTED. <<<")
        print(f"DETAILS: {e}")
        print("="*70 + "\n")
    except Exception as e:
        print("\n" + "="*70)
        print(">>> AN UNEXPECTED ERROR OCCURRED! SCRIPT HALTED. <<<")
        print(f"ERROR TYPE: {type(e).__name__}")
        print(f"DETAILS: {e}")
        print("="*70 + "\n")
        
# Main execution block
if __name__ == "__main__":
    GenMetainf(data)