# `ebookbuild`

This is the GitHub repository for `ebookbuild` which is a Python 3 script that can create compliant EPUB 2.0.1 files, with plans to support EPUB 3.3 in the future.

The sample file included is the free documentation as required by GNU GPLv3 to get you started and familiar with how `ebookbuild` works.

I have plans to write a premium how-to guide which goes into much more detail.

## Summary
You can use `ebookbuild` on Microsoft Windows, macOS and GNU/Linux. My approach to e-book development was designed to be as cross-platform as possible.

### 1. Setup Windows Subsystem for Linux (WSL)
Windows Subsystem for Linux (WSL) is available for Microsoft Windows 10 and 11. Skip this step if you are not using Microsoft Windows and instead using a Mac or GNU/Linux.

Try this guide from Microsoft: https://learn.microsoft.com/en-us/windows/wsl/install

You will also need a GNU/Linux distribution, I recommend using Ubuntu which can be installed from the Microsoft Store.

### 2. Download and install the following software
You will need a text editor and a web browser. You can use Microsoft Edge or Google Chrome, but I recommend the Brave Browser:

a. **Install a text editor** – Text editors are a matter of personal preference, though I recommend [Visual Studio Code](https://code.visualstudio.com/) as my go-to text editor of choice. However, the ideal text editor should be designed for programming and have built-in syntax highlighting for these file types: `.xhtml`, `.css`, `.json`, `.xml`, `.py`

b. **Install a Git client (optional)** – This is optional but I do recommend using [GitHub Desktop](https://desktop.github.com/) and a Git hosting provider such as GitHub, GitLab or Bitbucket to host the files, keep track of changes and easily revert changes if things go awry.

c. **Install the Brave Browser (optional)** – This is also optional, but [Brave](https://brave.com/) has similar functionality to Chrome along with additional features and an emphasis on privacy.

### 3. Download the following dependencies
These are required to make `ebookbuild` work though I do try to minimise external dependencies:

a. **Download and install Python 3.12** – on Microsoft Windows this can be done by downloading Python 3.12 from the [official Python website](https://www.python.org/). In WSL Ubuntu, use the following command `sudo apt update && sudo apt upgrade python3` to ensure the latest version.

b. **Install the OpenJDK** – this is to run epubcheck which is a Java application

c. **Download the latest epubcheck** – [epubcheck](https://www.w3.org/publishing/epubcheck/) is provided from the official W3C website and is used to ensure .epub file compliance with the standard. I recommend using the latest version as this GitHub repository may fall behind.

### 4. How to compile and test a .epub

a. **Open Terminal and change directory to the `e-book` folder** - the command should look like `cd e-book`

b. **Run ebookbuild and check the .epub file's compliance** - I use this command to build a new .epub and run epubcheck all at once `python3 ebookbuild.py && java -jar epubcheck.jar epubfile.epub` 

## Licencing

`ebookbuild` is designed to be always free. Both free as in freedom and free as in beer, so it is licenced under the strong copyleft GNU General Public License 3 (GPLv3).

epubcheck is included within this repository.