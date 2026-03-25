
pnb
====

![Screenshot](https://codeberg.org/chrisecker/pynotebook/raw/branch/master/screenshots/ball2.png)

[More screenshots](https://codeberg.org/chrisecker/pynotebook/src/branch/master/screenshots/)


Introduction
------------

Pnb is an interactive environment for python programming which
follows the notebook concept of mathematica and jupyter. Notebooks are
a pleasant way to develop and document python code and to store ideas.

Unlike other python notebook applications such as jupyter or spyder,
pnb is very lightweight and easy to install. It has only two
dependencies: wxpython and pynotebook.



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



