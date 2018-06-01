# ebookbuild

A very WIP cross-platform FOSS tool to create e-books properly, built entirely with FOSS technologies (so no vendor lock-in). Currently ebookbuild makes both reflowable and fixed-layout ePub 2.0.1 e-books.

Currently the code is found in individual repositories rather than centralised here in this repository. The latest e-book is *The Cathedral and the Bazaar*, the version of ebookbuild's main script `CreateE-book.py` is 0.8 (needs to support nested pages, compression and the ePub 3.0+ standard for 1.0).

ebookbuild is programmed in Python 3, although there are considerations to possibly switch language for speed improvements. I may use tkinter to develop a GUI.

## Features

### Current features (v0.8)
* Supports ePub 2.0.1.
* Supports reflowable and fixed-layout e-books.
* Supports anchor tags in the `toc.ncx`.
* Books generated convert nicely to .Mobi in Kindle Previewer.

### Planned features
* Get the script to run in IDLE and Thonny again (a strange bug means it won't run in those IDEs, yet runs in GNU Bash perfectly).
* Support ePub 3.1 and any future ePub releases.
* Support nested pages in the `toc.ncx`.
* Support compression (particularly desirable for image-heavy e-books)
* Support the ONIX 3 standard fully within the `metadata.json`.

## Examples
ebookbuild has been used to make the following e-books. Projects can be commercial or freely available to download.

### Commercial

|Title/Website | Author | Description |
|:------------:|:------:|:-----------:|
| A Treatise on MonoCulture: The Salvation of Society (2nd Edition) | Sander Laanemaa, Wesley Messamore |
| Karl Marx Never Bathed: The Staggeringly Messed Up Life of The World’s First Social Justice Warrior (2nd Edition) | Sander Laanemaa, Wesley Messamore |

### Free

| Title/Website | Author | Description |
|:-------------:|:--------------------:|:----------:|
|[The Cathedral and the Bazaar](https://github.com/inferno986return/cathedral-bazaar-ebook) | Eric S. Raymond | |
|[How we are Entertained: The Consequences of the 1983 Video Game Crash](https://github.com/inferno986return/1983VideoGameCrash-Book) | Hal Motley | |
|[Soldering is Easy: Here's How to Do It (Extended Version)](https://github.com/inferno986return/FullSolderComic-ebook) | Mitch Altman, Andie Nordgren, Jeff Keyzer | |
|[Making Games with Python & Pygame (Unofficial 2018 Edition)](https://github.com/inferno986return/Pygame-ebook) | Al Sweigart, Hal Motley | |
|[Linux is Badass: Slightly More Badass Edition](https://github.com/inferno986return/LinuxIsBadass) | Bryan Lunduke | |
|[The Illustrated Book of Patience Games](https://github.com/inferno986return/Illustrated-Patience-Games-ebook) | Professor Hoffman | 

## Licensing

ebookbuild is currently licensed under GNU GPLv3. See LICENSE.md for further information.

## And finally...

If ebookbuild has helped you and you want to give back, buy me a coffee (or two) via https://www.paypal.me/HalMotley.


