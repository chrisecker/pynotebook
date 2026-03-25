
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

Installing the binary:

    pip install .


Desktop integration (on ubuntu):

    mkdir -p ~/.local/share/applications
    cp pnb.desktop ~/.local/share/applications/
    cp pnb.png  ~/.local/share/icons/


Testing
-------

To start pnb without installing type:

    python runtests.py pnb


Links
-----
- [pynotebook module](https://pypi.python.org/pypi/pynotebook)
- [source code](https://codeberg.org/chrisecker/textmodel/tree/master/pynotebook)



