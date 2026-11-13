
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
dependencies: wxPython and pynotebook, the latter of which requires no
further external packages itself.


Features
--------

Most notable features are:

- syntax highlighting
- command completion (tab-key)
- object introspection (ctrl-h)
- built-in vector graphics
- plotting via matplotlib
- BSD-license



Installation
------------

Linux (Debian, Ubuntu, Fedora, ...): download the `.deb` or `.rpm`
from the [Releases page](https://github.com/chrisecker/pynotebook/releases)
and install it, e.g.:

    sudo apt install ./pnb_*_all.deb
    sudo dnf install ./pnb-*.noarch.rpm

The packages use the wxPython of the distribution and add pnb to the
application menu.

With pip (needs wxPython, which pip has to build from source on Linux):

    pip install pnb

From the source folder:

    pip install .

Desktop integration after a pip installation (pnb must be on the PATH):

    mkdir -p ~/.local/share/applications ~/.local/share/icons/hicolor/96x96/apps
    cp pnb.desktop ~/.local/share/applications/
    cp pnb.png ~/.local/share/icons/hicolor/96x96/apps/


Testing
-------

To start pnb without installing type:

    python runtests.py pnb


Links
-----
- [pynotebook module](https://pypi.org/project/pynotebook/)
- [source code](https://codeberg.org/chrisecker/pynotebook/src/branch/master/pnb)



