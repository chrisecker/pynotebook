
# pynotebook

![Screenshot](https://codeberg.org/chrisecker/pynotebook/raw/branch/master/screenshots/ball2.png)


[More screenshots](https://codeberg.org/chrisecker/pynotebook/src/branch/master/screenshots/)

## Introduction

Pynotebook is a library for creating notebook applications in wxPython.  
A notebook is a document that can contain program code, text, and graphics.  
Notebooks provide a pleasant way to develop and document code, as well as to store ideas.

Unlike other Python notebook interfaces such as Jupyter or Spyder, Pynotebook (pnb) is very lightweight and can be easily embedded in wxPython applications.

Although Python is the native language for Pynotebook, it is also possible to create notebooks for other scripting languages.

Applications using the Pynotebook library include:

- [pnb application](https://pypi.python.org/pypi/pnb) – a Python notebook application  
- [rnb](https://pypi.python.org/pypi/rnb) – an experimental notebook for the R programming language

## Run demo (no installation)

Running GUI:
>  cd demo
>  python plot_demo.py

## Testing

Most files have builtin tests. They can be started by:

>  python runtests.py pynotebook/nbtexels.py
  
Some files also builtin demos:

>  python runtests.py pynotebook/nbview.py demo_00


## Installation
pip install .

or if you do not have the pip executable installed:

python -m pip install .

## Links

- [Sources on codeberg](https://codeberg.org/chrisecker/pynotebook)


