
# pynotebook

![Screenshot](https://codeberg.org/chrisecker/pynotebook/raw/branch/master/screenshots/matplotlib.png)


[More screenshots](https://codeberg.org/chrisecker/pynotebook/src/branch/master/screenshots/)

## Introduction

Pynotebook is a library for building notebook interfaces within
wxPython. A notebook is an interactive document that integrates
program code, rich text, and graphics into a single file.

Unlike heavier environments such as Jupyter or Spyder, Pynotebook is
exceptionally lightweight and designed to be easily embedded into
existing wxPython applications. While Python is its native language,
the library is flexible enough to support other scripting languages as
well.

Applications using the Pynotebook library include:

- [pnb application](https://pypi.python.org/pypi/pnb) – a Python notebook application  

## Run demo (no installation)

    cd demo
    python plot_demo.py

## Testing

Most files have builtin tests. They can be started by:

    python runtests.py pynotebook/nbtexels.py
  
Some files also have builtin demos:

    python runtests.py pynotebook/nbview.py demo_00


## Installation
    pip install .

or if you do not have the pip executable installed:

    python -m pip install .

If you also want to install pnb:
    pip install pnb

## Links

- [Sources on codeberg](https://codeberg.org/chrisecker/pynotebook)


