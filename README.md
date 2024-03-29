# ebookbuild

*Get started with `ebookbuild` by reading the [wiki](https://github.com/inferno986return/ebookbuild/wiki).*

A very WIP cross-platform FOSS tool to create e-books properly, built entirely with FOSS technologies (so no vendor lock-in). Currently ebookbuild makes both reflowable and fixed-layout ePub 2.0.1 e-books.

Currently the code is found in individual repositories rather than centralised here in this repository. The latest e-book is *The Fall of Western Man*, the version of ebookbuild's main script `CreateE-book.py` is 0.8111 (needs to support nested pages and the rest of the legacy ePub 2.0.1 standard for v1.0).

ebookbuild is programmed in Python 3, although there are considerations to possibly switch language for speed improvements. I may use tkinter to develop a GUI.

I may develop several scripts related to e-book development under the ebookbuild name.

## Features
*NOTE: ebookbuild has a bug where it generates backslashes on Windows for the Content.opf. So I recommend compiling e-books using Windows Subsystem for Linux on Windows, or via the native macOS / GNU/Linux terminal.*

### v0.8114 Features (current)
* Fixed SHA-256 generation. I have tested the checksums with the Bash `sha256sum` and PowerShell `Get-FileHash` commands.
* Added timestamp for the checksums in UTC.

### v0.8113 Features
* Changed script name from `CreateE-book.py` to the simpler `ebookbuild.py`.
* Saves MD5, SHA-256 and SHA-512 checksums with a datestamps and timestamps.

### v0.8112 Features

### v0.8111 Features
* Added a GNU GPL-compliant (I hope) header to `ebookbuild` when run on the command-line.
* Changed SHA512 to SHA256 (apparently it requires less resources to generate and is a common standard anyway, I am happy to discuss this and might include all three if desired).

### v0.811 Features (and prior versions)
* Supports ePub 2.0.1.
* Supports reflowable and fixed-layout e-books.
* Supports 1 layer of anchor tags in the `toc.ncx`.
* Books generated convert nicely to .Mobi in Kindle Previewer (though images need to be centred with CSS `text-align: center;`).
* Runs on GNU Bash, IDLE and Thonny (for now).
* Shows MD5 and SHA512 hashes of the ePub file at the end output (the built-in datestamp and timestamp will ensure different hashes for each ePub generated) and saves them to `checksums.txt`.
* Fixed a bug so that any number of .otf/.ttf fonts can be added to an ePub.

### Planned features

* Support ePub 3.1 and any future ePub releases.
* Support nested pages in the `toc.ncx`. (for version 1.0)
* Support 3 layers of anchor tags in the `toc.ncx`. (for version 1.0)
* Support XHTML and CSS minification and obfuscation.
* Support compression (particularly desirable for image-heavy e-books).
* Support the ONIX 3 standard fully within the `metadata.json`.
* Maybe a better way to uniquely identify individual ePub builds (fingerprint) than just checksums?

## Examples
ebookbuild has been used to make the following e-books. Projects can be commercial or freely available to download.

### Commercial

|Title/Website | Author | Description |
|:------------:|:------:|:-----------:|
|              |        |             |


### Free and sample projects

| Title/Website | Author | Description |
|:-------------:|:--------------------:|:----------:|
|[The Cathedral and the Bazaar](https://github.com/inferno986return/cathedral-bazaar-ebook) | Eric S. Raymond | |
|[How We Are Entertained: The Consequences of the 1983 Video Game Crash](https://github.com/inferno986return/1983VideoGameCrash-Book) | Hal Motley | |
|[Soldering is Easy: Here's How to Do It (Extended Version)](https://github.com/inferno986return/FullSolderComic-ebook) | Mitch Altman, Andie Nordgren, Jeff Keyzer | |
|[Making Games with Python & Pygame (Unofficial 2018 Edition)](https://github.com/inferno986return/Pygame-ebook) | Al Sweigart, Hal Motley | |
|[Linux is Badass: Slightly More Badass Edition](https://github.com/inferno986return/LinuxIsBadass) | Bryan Lunduke | |
|[The Fall of Western Man](https://github.com/inferno986return/the-fall-of-western-man) | Mark Collett | |
|[Ligi's Survival Guide](https://github.com/inferno986return/SurvivalManual-ebook)] | Ligi | |
|Pirate Cinema | Cory Doctorow | | <!--Need to clone the repo across to GitHub-->
|Essential C | Nick Parlante | | <!--Need to clone the repo across to GitHub-->

### Templates

| Title/Website | Author | Description |
|:-------------:|:--------------------:|:----------:|
|[The Illustrated Book of Patience Games](https://github.com/inferno986return/Illustrated-Patience-Games-ebook) | Professor Hoffman | |

## Licensing

I have licenced ebookbuild under GNU GPLv3. See LICENSE.md for further information.

## And finally...

If ebookbuild has helped you and you want to give back, buy me a coffee (or two) via https://www.paypal.me/HalMotley.
