
# pynotebook

![Screenshot](https://codeberg.org/chrisecker/pynotebook/raw/branch/master/screenshots/polar.png)

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

## Features

- Code cells with syntax highlighting, completion and help; the output
  appears right below the cell
- Text cells with formatted text for notes and documentation
- Graphics in the document: matplotlib figures, bitmaps and built-in
  vector graphics (`pynotebook.graphics`)
- A notebook is a single wx widget, easy to embed
- Other languages can be plugged in as clients; `demo/rnotebook.py`
  shows R (needs rpy2)
- Safe, readable file format: notebooks are saved as JSON, and opening
  a file never runs code
- Few dependencies: wxPython (not installed automatically), and
  cerealizer to read files of older versions; BSD license

## Embedding

    import wx
    from pynotebook.nbview import NBView

    app = wx.App()
    frame = wx.Frame(None, title='My notebook', size=(800, 600))
    view = NBView(frame)   # or NBView(frame, filename='example.pnb')
    frame.Show()
    app.MainLoop()

`view.save(filename)` writes the notebook to a file.

Applications using the Pynotebook library include:

- [pnb](https://pypi.org/project/pnb/) – a Python notebook application

## Run demo (no installation, needs matplotlib)

    cd demo
    python plot_demo.py

## Installation

Pynotebook needs wxPython 4.2 or newer, which is not installed
automatically: usually your application or your Linux distribution
already provides it. From PyPI:

    pip install pynotebook

To install wxPython as well (on Linux, pip has to build it from source):

    pip install "pynotebook[wx]"

From the source folder:

    pip install .

If you also want to install pnb:

    pip install pnb

## Testing

Most files have builtin tests. All of them run with:

    python all_tests.py

The tests of a single file:

    python runtests.py pynotebook/nbtexels.py

Some files also have builtin demos:

    python runtests.py pynotebook/nbview.py demo_00

## Links

- [Sources on codeberg](https://codeberg.org/chrisecker/pynotebook)
