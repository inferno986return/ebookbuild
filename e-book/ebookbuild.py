#!/usr/bin/env python
# ebookbuild.py v1.5.0 - Generates an EPUB 3.3 / 2.0.1 file using metadata.json with lxml and orjson.
# Licensed under GNU GPLv3: https://www.gnu.org/licenses/gpl-3.0.en.html

import os, datetime, zipfile, hashlib, re
import orjson
from lxml import etree

print("""=================================================================
ebookbuild for EPUB 2.0.1 and 3.2+, v1.5.0 - Copyright (C) 2026 Hal Motley
https://www.github.com/inferno986return/ebookbuild/
==========================================================================

NOTE: This program creates both the legacy EPUB 2.0.1 files and the current EPUB 3.2+ files which are recommended by the W3C!

This script uses the lxml and orjson libraries to create fully-compliant
EPUB 3.3 files that pass epubcheck and can be read with most e-readers.

Not working? Try installing the dependencies:
    * lxml - 'pip install lxml'
    * orjson - 'pip install orjson'

This program comes with ABSOLUTELY NO WARRANTY; for details see the license.
This is free software, and you are welcome to redistribute it
under certain conditions. All trademarks belong to their respective owners.
""")

try:
    with open("metadata.json", "rb") as f:
        data = orjson.loads(f.read())
except FileNotFoundError:
    raise SystemExit("FATAL ERROR: metadata.json not found. The script cannot continue.")

# --- PRE-COMPILED REGEXES & CONSTANTS FOR PERFORMANCE ---
RE_WS = re.compile(r"\s+")
RE_CSS_COMMENTS = re.compile(r"/\*[\s\S]*?\*/")
RE_CSS_DELIMS = re.compile(r"\s*([\{\};:,>~+])\s*")
RE_CSS_CLASS = re.compile(r"\.([a-zA-Z_][a-zA-Z0-9_-]*)")
RE_JS_LINE_COMMENT = re.compile(r"(?<!:)//.*$", re.MULTILINE)
RE_JS_DELIMS = re.compile(r"[ \t]*([\{\};,=+\-*/<>!&|?:])[ \t]*")

DC_NS = "http://purl.org/dc/elements/1.1/"
OPF_NS = "http://www.idpf.org/2007/opf"
OPS_NS = "http://www.idpf.org/2007/ops"
XHTML_NS = "http://www.w3.org/1999/xhtml"

SUPPORTED_ASSETS = {
    ".xhtml": "application/xhtml+xml", ".html": "application/xhtml+xml",
    ".css": "text/css", ".js": "application/javascript",
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".gif": "image/gif", ".svg": "image/svg+xml", ".webp": "image/webp",
    ".ttf": "font/truetype", ".otf": "font/opentype", ".woff": "font/woff", ".woff2": "font/woff2",
    ".mp3": "audio/mpeg", ".mp4": "video/mp4", ".m4a": "audio/mp4", ".m4v": "video/mp4",
    ".opus": "audio/opus", ".pls": "application/pls+xml", ".smil": "application/smil+xml"
}

HEADER_PROFILES = {
    "epub2": {
        "xml_decl": '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>',
        "doctype": None,
        "nsmap": {None: XHTML_NS},
        "meta_attrs": {"content": "http://www.w3.org/1999/xhtml; charset=utf-8", "http-equiv": "Content-Type"}
    },
    "epub3": {
        "xml_decl": '<?xml version="1.0" encoding="UTF-8"?>',
        "doctype": "<!DOCTYPE html>",
        "nsmap": {None: XHTML_NS, "epub": OPS_NS},
        "meta_attrs": {"charset": "utf-8"}
    }
}


def GenOPF(output_dir, data):
    """Generate the OPF package file."""
    opf_filename = data.get("opfName", "content.opf")
    print(f"Generating {opf_filename}...")
    utctime = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    package = etree.Element("package", attrib={"unique-identifier": "bookid", "version": "3.0"}, nsmap={"dc": DC_NS, None: OPF_NS})
    metadata = etree.SubElement(package, "metadata")

    # Core Dublin Core Metadata
    etree.SubElement(metadata, f"{{{DC_NS}}}identifier", id="bookid").text = data["ISBN"]
    etree.SubElement(metadata, "meta", refines="#bookid", property="identifier-type", scheme="xsd:string").text = "ISBN"
    etree.SubElement(metadata, f"{{{DC_NS}}}title").text = data["title"]

    # Unified Creator & Contributor Loop
    for role_type in ("creator", "contributor"):
        i = 1
        while f"{role_type}{i}" in data:
            el_id = f"{role_type}{i}"
            etree.SubElement(metadata, f"{{{DC_NS}}}{role_type}", id=el_id).text = data[el_id]
            if f"{el_id}Role" in data:
                etree.SubElement(metadata, "meta", refines=f"#{el_id}", property="role", scheme="marc:relators").text = data[f"{el_id}Role"]
            i += 1

    for tag in ("publisher", "language", "rights", "date", "description"):
        if data.get(tag):
            etree.SubElement(metadata, f"{{{DC_NS}}}{tag}").text = data[tag]

    if data.get("sourceUrn") and data.get("sourceISBN"):
        etree.SubElement(metadata, f"{{{DC_NS}}}source").text = f"urn:{data['sourceUrn'].lower()}:{data['sourceISBN']}"

    if bool(data.get("lastModified", True)):
        etree.SubElement(metadata, "meta", property="dcterms:modified").text = utctime

    col = data.get("collection", {})
    if bool(col.get("enableCollection")) and all(k in col for k in ("name", "type", "position")):
        etree.SubElement(metadata, "meta", property="belongs-to-collection", id="collection").text = col["name"]
        etree.SubElement(metadata, "meta", refines="#collection", property="collection-type").text = col["type"]
        etree.SubElement(metadata, "meta", refines="#collection", property="group-position").text = str(col["position"])
        if col.get("fileAs"):
            etree.SubElement(metadata, "meta", refines="#collection", property="file-as").text = col["fileAs"]
        if col.get("alternativeScript"):
            etree.SubElement(metadata, "meta", refines="#collection", property="alternate-script").text = col["alternativeScript"]

    etree.SubElement(metadata, "meta", name="cover", content="cover-image")

    # Manifest Registry
    manifest_registry = {data["navDocFile"]: "nav"}
    if bool(data.get("enableNcx")):
        manifest_registry["toc.ncx"] = "ncx"

    asset_counters = {}
    epub_cover = data.get("epubCover")

    for dirpath, _, filenames in os.walk(output_dir):
        for file in sorted(filenames):
            ext = os.path.splitext(file)[1].lower()
            if ext in SUPPORTED_ASSETS:
                href = os.path.relpath(os.path.join(dirpath, file), output_dir).replace(os.sep, "/")
                if href not in manifest_registry:
                    if epub_cover and file == epub_cover:
                        manifest_registry[href] = "cover-image"
                    else:
                        prefix = ext.lstrip(".")
                        idx = asset_counters.get(prefix, 0)
                        manifest_registry[href] = f"{prefix}{idx}"
                        asset_counters[prefix] = idx + 1

    manifest = etree.SubElement(package, "manifest")
    for href, item_id in manifest_registry.items():
        ext = os.path.splitext(href)[1].lower()
        media_type = "application/x-dtbncx+xml" if item_id == "ncx" else SUPPORTED_ASSETS.get(ext, "application/xhtml+xml")
        attrs = {"id": item_id, "href": href, "media-type": media_type}
        if item_id in ("nav", "cover-image"):
            attrs["properties"] = item_id
        etree.SubElement(manifest, "item", **attrs)

    # Spine Generation
    spine = etree.SubElement(package, "spine", **({"toc": "ncx"} if bool(data.get("enableNcx")) else {}))
    seen_spine = set()

    def process_spine(items):
        for item in items:
            base = item["fileName"].split("#")[0]
            if base not in seen_spine:
                if item_id := manifest_registry.get(base):
                    itemref = etree.SubElement(spine, "itemref", idref=item_id)
                    if item.get("type") == "cover":
                        itemref.set("linear", "no")
                else:
                    print(f"  -> WARNING: Spine item '{base}' missing from output folder.")
                seen_spine.add(base)
            if item.get("subheadings"):
                process_spine(item["subheadings"])

    process_spine(data["pages"])
    etree.ElementTree(package).write(os.path.join(output_dir, opf_filename), encoding="UTF-8", xml_declaration=True, pretty_print=True)


def GenNav(output_dir, data):
    """Generate the nav.xhtml file required by EPUB 3."""
    print("Generating nav.xhtml...")
    nav_html = etree.Element("html", nsmap={None: XHTML_NS, "epub": OPS_NS})
    etree.SubElement(etree.SubElement(nav_html, "head"), "title").text = data["tocTitle"]
    body = etree.SubElement(nav_html, "body")

    nav = etree.SubElement(body, "nav", **{f"{{{OPS_NS}}}type": "toc", "id": "toc"})
    etree.SubElement(nav, "h1").text = data["tocTitle"]

    def build_ol(parent, items):
        ol = etree.SubElement(parent, "ol")
        for item in items:
            li = etree.SubElement(ol, "li")
            etree.SubElement(li, "a", href=item["fileName"]).text = item["pageName"]
            if item.get("subheadings"):
                build_ol(li, item["subheadings"])

    build_ol(nav, data["pages"])

    if bool(data.get("enableGuide")):
        landmarks = etree.SubElement(body, "nav", **{f"{{{OPS_NS}}}type": "landmarks", "id": "landmarks"})
        etree.SubElement(landmarks, "h1").text = "Landmarks"
        l_ol = etree.SubElement(landmarks, "ol")
        for l_type, f_key, p_key in (("cover", "frontCoverfile", "frontCoverpage"), ("toc", "tocFile", "tocPage"), ("bodymatter", "startReadingfile", "startReadingpage")):
            li = etree.SubElement(l_ol, "li")
            etree.SubElement(li, "a", **{f"{{{OPS_NS}}}type": l_type, "href": data[f_key]}).text = data[p_key]

    etree.ElementTree(nav_html).write(os.path.join(output_dir, data["navDocFile"]), encoding="UTF-8", xml_declaration=True, pretty_print=True, doctype="<!DOCTYPE html>")


def GenNCX(output_dir, data):
    """Generate toc.ncx for EPUB 2 backward compatibility."""
    if not bool(data.get("enableNcx")):
        return print("Skipping toc.ncx generation as 'enableNcx' is false.")

    print("Generating toc.ncx...")
    ncx = etree.Element("ncx", xmlns="http://www.daisy.org/z3986/2005/ncx/", version="2005-1")
    head = etree.SubElement(ncx, "head")
    for name, val in (("dtb:uid", data["ISBN"]), ("dtb:totalPageCount", "0"), ("dtb:maxPageNumber", "0")):
        etree.SubElement(head, "meta", name=name, content=val)

    etree.SubElement(etree.SubElement(ncx, "docTitle"), "text").text = data["titleShort"]
    nav_map = etree.SubElement(ncx, "navMap")

    play_order, max_depth = 1, 0
    def add_point(parent, item, depth):
        nonlocal play_order, max_depth
        np = etree.SubElement(parent, "navPoint", id=f"navpoint-{play_order}", playOrder=str(play_order))
        etree.SubElement(etree.SubElement(np, "navLabel"), "text").text = item["pageName"]
        etree.SubElement(np, "content", src=item["fileName"])
        play_order += 1
        max_depth = max(max_depth, depth)
        for sub in item.get("subheadings", ()):
            add_point(np, sub, depth + 1)

    for page in data["pages"]:
        add_point(nav_map, page, 1)

    etree.SubElement(head, "meta", name="dtb:depth", content=str(max_depth))
    etree.ElementTree(ncx).write(os.path.join(output_dir, "toc.ncx"), encoding="UTF-8", xml_declaration=True, pretty_print=True)


def GenPackagingFiles(data):
    """Ensure mimetype and META-INF/container.xml exist and are valid."""
    print("Checking container metadata...")
    mime_target = "application/epub+zip"
    if not (os.path.exists("mimetype") and open("mimetype", "r").read() == mime_target):
        print("  - Creating/updating mimetype file.")
        with open("mimetype", "w") as f:
            f.write(mime_target)

    os.makedirs("META-INF", exist_ok=True)
    container_path = os.path.join("META-INF", "container.xml")
    expected_opf = f"{data['containerFolder']}/{data.get('opfName', 'content.opf')}"

    valid_container = False
    if os.path.exists(container_path):
        try:
            rootfile = etree.parse(container_path).find("c:rootfiles/c:rootfile", namespaces={"c": "urn:oasis:names:tc:opendocument:xmlns:container"})
            valid_container = rootfile is not None and rootfile.get("full-path") == expected_opf
        except etree.XMLSyntaxError:
            pass

    if not valid_container:
        print("  - Creating/updating container.xml.")
        container = etree.Element("container", version="1.0", xmlns="urn:oasis:names:tc:opendocument:xmlns:container")
        etree.SubElement(etree.SubElement(container, "rootfiles"), "rootfile", **{"full-path": expected_opf, "media-type": "application/oebps-package+xml"})
        etree.ElementTree(container).write(container_path, encoding="UTF-8", xml_declaration=True, pretty_print=True)


# ==============================================================================
# IN-MEMORY HEADER NORMALIZATION, CSS PURGING & MINIFICATION PIPELINE
# ==============================================================================

def NormalizeXHTMLHeader(tree, epub_version):
    """Rewrites <html> namespaces and <head> charset meta tags to match EPUB 2.0.1 vs 3.2+."""
    is_epub2 = float(epub_version) < 3.0
    profile = HEADER_PROFILES["epub2" if is_epub2 else "epub3"]
    old_root = tree.getroot()

    if old_root.nsmap != profile["nsmap"]:
        new_root = etree.Element(f"{{{XHTML_NS}}}html", nsmap=profile["nsmap"])
        for k, v in old_root.attrib.items():
            if not (is_epub2 and OPS_NS in k):
                new_root.set(k, v)
        new_root.text = old_root.text
        new_root.extend(old_root)
        tree._setroot(new_root)
        root = new_root
    else:
        root = old_root

    head = root.find(f"{{{XHTML_NS}}}head")
    if head is None:
        head = root.find("head")
    if head is not None:
        for meta in list(head.findall(f"{{{XHTML_NS}}}meta")) + list(head.findall("meta")):
            if "charset" in meta.attrib or (meta.get("http-equiv") or "").lower() == "content-type":
                head.remove(meta)
        new_meta = etree.Element(f"{{{XHTML_NS}}}meta", attrib=profile["meta_attrs"])
        head.insert(0, new_meta) if is_epub2 else head.append(new_meta)

    return tree, profile


def CollectUsedCSSClasses(source_dir):
    """Scans all XHTML/HTML/SVG files and returns a set of active CSS class names."""
    used_classes = set()
    for dirname, _, files in os.walk(source_dir):
        for file in files:
            if os.path.splitext(file)[1].lower() in {".xhtml", ".html", ".svg"}:
                path = os.path.join(dirname, file)
                try:
                    for attr in etree.parse(path).xpath("//@class"):
                        used_classes.update(attr.split())
                except Exception:
                    pass
    print(f"  -> Indexed {len(used_classes)} active CSS classes across markup files.")
    return used_classes


def PurgeUnusedCSS(css_text, used_classes):
    """Removes CSS selectors and rule blocks referencing classes absent from used_classes."""
    comments = []
    masked_css = RE_CSS_COMMENTS.sub(lambda m: (comments.append(m.group(0)), f"__C_{len(comments)-1}__")[1], css_text)

    def filter_selectors(group):
        kept = []
        for sel in group.split(","):
            if not (s := sel.strip()):
                continue
            clean = re.sub(r"__C_\d+__", "", s).strip()
            if not clean or all(c in used_classes for c in RE_CSS_CLASS.findall(clean)):
                kept.append(s)
        return ", ".join(kept)

    def parse_block(text):
        out, i, n = [], 0, len(text)
        while i < n:
            b, s = text.find("{", i), text.find(";", i)
            if s != -1 and (b == -1 or s < b):
                if stmt := text[i:s+1].strip():
                    out.append(stmt)
                i = s + 1
                continue
            if b == -1:
                if rem := text[i:].strip():
                    out.append(rem)
                break

            selector, depth, j = text[i:b].strip(), 1, b + 1
            while j < n and depth > 0:
                depth += (text[j] == "{") - (text[j] == "}")
                j += 1
            body = text[b+1:j-1]

            sel_clean = re.sub(r"^(?:__C_\d+__\s*)*", "", selector)
            if sel_clean.startswith("@"):
                if any(sel_clean.startswith(at) for at in ("@media", "@supports", "@layer", "@container")):
                    if inner := parse_block(body).strip():
                        out.append(f"{selector} {{\n{inner}\n}}")
                else:
                    out.append(f"{selector} {{{body}}}")
            elif kept_sel := filter_selectors(selector):
                out.append(f"{kept_sel} {{{body}}}")
            i = j
        return "\n".join(out)

    purged = parse_block(masked_css)
    for idx, comm in enumerate(comments):
        purged = purged.replace(f"__C_{idx}__", comm)
    return purged


def minify_css_string(css, purge_classes, rm_comments, min_ws, used_classes):
    """Shared helper to purge and minify both standalone .css files and inline <style> blocks."""
    if purge_classes and used_classes is not None:
        css = PurgeUnusedCSS(css, used_classes)
    if rm_comments:
        css = RE_CSS_COMMENTS.sub("", css)
    if min_ws:
        css = RE_CSS_DELIMS.sub(r"\1", RE_WS.sub(" ", css)).replace(";}", "}").strip()
    return css


def ProcessAndMinifyAsset(filepath, ext, data, used_classes=None):
    """Applies header normalization, CSS class purging, comment stripping, and minification in-memory."""
    xhtml_copy = bool(data.get("insertXHTMLCopyright", False))
    xhtml_ws   = bool(data.get("minifyXHTMLWhitespace", False))
    xhtml_comm = bool(data.get("removeXHTMLComments", False))

    css_copy   = bool(data.get("injectCSSCopyright", False))
    css_ws     = bool(data.get("minifyCSSWhitespace", False))
    css_comm   = bool(data.get("removeCSSComments", False))
    css_purge  = bool(data.get("stripUnusedCSSClasses", False))

    js_copy    = bool(data.get("insertJSCopyright", False))
    js_ws      = bool(data.get("minifyJSWhitespace", False))
    js_comm    = bool(data.get("removeJSComments", False))

    notice = (data.get("copyrightNotice") or data.get("copyrightNotice:") or "").strip()

    # 1. XML / XHTML Assets
    if ext in {".xhtml", ".html", ".xml", ".opf", ".ncx", ".svg", ".smil", ".pls"}:
        is_xhtml = ext in {".xhtml", ".html"}
        if not (is_xhtml or xhtml_copy or xhtml_ws or xhtml_comm or css_purge):
            return open(filepath, "rb").read()
        try:
            parser = etree.XMLParser(remove_blank_text=xhtml_ws, remove_comments=xhtml_comm, resolve_entities=False)
            tree = etree.parse(filepath, parser)

            if is_xhtml:
                tree, profile = NormalizeXHTMLHeader(tree, data.get("epubVersion", 3.3))
                xml_decl, doctype = profile["xml_decl"], profile["doctype"]
            else:
                xml_decl, doctype = '<?xml version="1.0" encoding="UTF-8"?>', None

            for elem in tree.iter():
                tag = etree.QName(elem).localname if isinstance(elem.tag, str) else ""
                if xhtml_ws and tag not in ("pre", "code", "script", "style", "textarea"):
                    if elem.text and elem.text.strip():
                        elem.text = RE_WS.sub(" ", elem.text)
                    if elem.tail and elem.tail.strip():
                        elem.tail = RE_WS.sub(" ", elem.tail)
                elif tag == "style" and elem.text:
                    elem.text = minify_css_string(elem.text, css_purge, css_comm, css_ws, used_classes)

            body = etree.tostring(tree, encoding="UTF-8", xml_declaration=False, pretty_print=not xhtml_ws, doctype=doctype)
            header = f"{xml_decl}\n" + (f"<!-- {notice} -->\n" if xhtml_copy and notice else "")
            return header.encode("utf-8") + body
        except Exception as e:
            print(f"    [!] XML fallback for {filepath}: {e}")
            return open(filepath, "rb").read()

    # 2. CSS Assets
    if ext == ".css":
        if not (css_copy or css_ws or css_purge or css_comm):
            return open(filepath, "rb").read()
        content = minify_css_string(open(filepath, "r", encoding="utf-8").read(), css_purge, css_comm, css_ws, used_classes)
        return (f"/* {notice} */\n{content}" if css_copy and notice else content).encode("utf-8")

    # 3. JS Assets
    if ext == ".js":
        if not (js_copy or js_ws or js_comm):
            return open(filepath, "rb").read()
        content = open(filepath, "r", encoding="utf-8").read()
        if js_comm:
            content = RE_JS_LINE_COMMENT.sub("", RE_CSS_COMMENTS.sub("", content))
        if js_ws:
            content = RE_JS_DELIMS.sub(r"\1", "\n".join(line.strip() for line in content.splitlines() if line.strip()))
        return (f"/* {notice} */\n{content}" if js_copy and notice else content).encode("utf-8")

    return open(filepath, "rb").read()


def TouchFiles(source_dir):
    """Updates file timestamps on disk to prevent zipfile pre-1980 ValueError."""
    print("Touching files to normalize timestamps...")
    for target in ("mimetype", os.path.join("META-INF", "container.xml")):
        if os.path.exists(target):
            os.utime(target, None)
    for dirname, _, files in os.walk(source_dir):
        for file in files:
            try:
                os.utime(os.path.join(dirname, file), None)
            except OSError:
                pass


def GenEpub(data):
    """Package and compress the EPUB archive."""
    print("\nPackaging EPUB file...")
    epub_filename = data["fileName"] + ".epub"
    source_dir = data["containerFolder"]
    compress_level = int(data.get("compressionLevel", 9))

    TouchFiles(source_dir)
    now_tuple = datetime.datetime.now(datetime.timezone.utc).timetuple()[:6]

    used_classes = CollectUsedCSSClasses(source_dir) if bool(data.get("stripUnusedCSSClasses", False)) else None
    processable_exts = {".xhtml", ".html", ".css", ".js", ".xml", ".opf", ".ncx", ".svg", ".smil", ".pls"}

    def write_zip_bytes(zf, arcname, raw_bytes):
        zinfo = zipfile.ZipInfo(filename=arcname, date_time=now_tuple)
        zinfo.compress_type = zipfile.ZIP_DEFLATED
        zinfo.external_attr = 0o644 << 16
        zf.writestr(zinfo, raw_bytes)

    with zipfile.ZipFile(epub_filename, mode="w", compression=zipfile.ZIP_STORED) as zf:
        zf.write("mimetype", arcname="mimetype")

    with zipfile.ZipFile(epub_filename, mode="a", compression=zipfile.ZIP_DEFLATED, compresslevel=compress_level) as zf:
        if os.path.exists("META-INF/container.xml"):
            write_zip_bytes(zf, "META-INF/container.xml", ProcessAndMinifyAsset("META-INF/container.xml", ".xml", data, used_classes))

        for dirname, _, files in os.walk(source_dir):
            for filename in sorted(files):
                full_path = os.path.join(dirname, filename)
                arcname = full_path.replace("\\", "/")
                ext = os.path.splitext(filename)[1].lower()
                print(f"  - Zipping: {arcname}")
                if ext in processable_exts:
                    write_zip_bytes(zf, arcname, ProcessAndMinifyAsset(full_path, ext, data, used_classes))
                else:
                    zf.write(full_path, arcname)

    print(f"\nEPUB file '{epub_filename}' created successfully." if zipfile.is_zipfile(epub_filename) else f"\nError: '{epub_filename}' is invalid.")


def GenChksum(data):
    """Generate selected checksums (md5, sha256, sha512) for the final EPUB file."""
    if not bool(data.get("enableChecksums")):
        return print("\nChecksum generation disabled. Skipping.")

    print("\nGenerating checksums...")
    epub_filename = data["fileName"] + ".epub"
    utctime = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(" ")
    buf = open(epub_filename, "rb").read()

    lines = [
        "-This output is saved to checksums.txt-\n",
        "WARNING: MD5 is cryptographically weak. Use SHA-256 or SHA-512 instead.\n",
        f"Checksum values for {epub_filename} on {utctime} UTC",
        "=" * 71 + "\n"
    ]
    if bool(data.get("md5", True)):
        lines.append(f"MD5: {hashlib.md5(buf).hexdigest()}")
    if bool(data.get("sha256", True)):
        lines.append(f"SHA-256: {hashlib.sha256(buf).hexdigest()}")
    if bool(data.get("sha512", True)):
        lines.append(f"SHA-512: {hashlib.sha512(buf).hexdigest()}")

    output = "\n".join(lines) + "\n"
    print(output)
    with open("checksums.txt", "w") as f:
        f.write(output)


def GenMetainf(data):
    """Runs the main build process for the e-book."""
    try:
        oebps_dir = data["containerFolder"]
        if not os.path.isdir(oebps_dir):
            raise FileNotFoundError(f"The container folder '{oebps_dir}' does not exist.")

        GenPackagingFiles(data)
        GenOPF(oebps_dir, data)
        GenNav(oebps_dir, data)
        GenNCX(oebps_dir, data)
        GenEpub(data)
        GenChksum(data)
        print("\nAll tasks completed successfully!")

    except Exception as e:
        print(f"\n{'='*70}\n>>> ERROR OCCURRED! SCRIPT HALTED. ({type(e).__name__}) <<<\nDETAILS: {e}\n{'='*70}\n")

if __name__ == "__main__":
    GenMetainf(data)