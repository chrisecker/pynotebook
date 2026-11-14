
pnb
====

![Screenshot](https://codeberg.org/chrisecker/pynotebook/raw/branch/master/screenshots/ball.png)

[More screenshots](https://codeberg.org/chrisecker/pynotebook/src/branch/master/screenshots/)


Introduction
------------

Pnb is an interactive environment for Python programming inspired by
the notebook concept of Mathematica and Jupyter. Notebooks offer a
nice way to develop and document Python code while organizing
ideas.

Unlike heavier applications like Jupyter or Spyder, pnb is
exceptionally lightweight and easy to install. It has only two
dependencies: wxPython and pynotebook, which itself only needs the
small pure-Python package cerealizer to read files of older versions.


Features
--------

- Code cells: run with Shift+Return, the output appears right below
- Syntax highlighting, completion (Tab) and help on the word at the
  cursor (Ctrl-H)
- Text cells with formatted text for notes and documentation
- Plots via matplotlib and built-in vector graphics, right in the
  document
- Safe, readable file format: notebooks are saved as JSON, and opening
  a file never runs code
- BSD license


Quick start
-----------

Start `pnb`, type some Python code and press Shift+Return:

| Key | Action |
|---|---|
| Shift+Return | Execute the cell |
| Tab | Complete |
| Ctrl-H | Help on the word at the cursor |
| Ctrl-T | Insert a text cell |
| Ctrl-B | Split the cell at the cursor |
| Ctrl-I / Ctrl-U | Indent / dedent |

Examples: `demo/*.pnb` in the sources; the Linux packages install them
to `/usr/share/doc/pnb/examples/`.


Installation
------------

Linux (Debian, Ubuntu, Fedora, ...): download the `.deb` or `.rpm`
from the [Releases page](https://github.com/chrisecker/pynotebook/releases)
and install it, e.g.:

    sudo apt install ./pnb_*_all.deb
    sudo dnf install ./pnb-*.noarch.rpm

The packages use the wxPython of the distribution and add pnb to the
application menu.

With pip and the wxPython of your Linux distribution (4.2 or newer):

    sudo apt install python3-wxgtk4.0      # or: sudo dnf install python3-wxpython4
    python3 -m venv --system-site-packages ~/pnb-env
    ~/pnb-env/bin/pip install pnb

With pip including wxPython (Windows, macOS; on Linux, pip has to build
wxPython from source):

    pip install "pnb[wx]"

From the source folder:

    pip install .

Desktop integration after a pip installation (pnb must be on the PATH):

    mkdir -p ~/.local/share/applications ~/.local/share/icons/hicolor/96x96/apps
    cp pnb.desktop ~/.local/share/applications/
    cp pnb.png ~/.local/share/icons/hicolor/96x96/apps/


Run without installing
----------------------

In this folder:

    python runtests.py pnb


Links
-----
- [pynotebook module](https://pypi.org/project/pynotebook/)
- [source code](https://codeberg.org/chrisecker/pynotebook/src/branch/master/pnb)
