import sys
from runtests import test_file

sys.path.insert(0, '.')

files = [
    # pynotebook
    "pynotebook/nbtexels.py",
    "pynotebook/graphics.py",
    "pynotebook/wxgraphics.py",
    "pynotebook/nbview.py",
    "pynotebook/pyclient.py",
    "pynotebook/jsonformat.py",
    "pynotebook/inspector.py",
    "pynotebook/cerealizerformat.py",
    "pynotebook/textformat.py",
    # textmodel
    "pynotebook/textmodel/texeltree.py",
    "pynotebook/textmodel/styles.py",
    "pynotebook/textmodel/textmodel.py",
    "pynotebook/textmodel/iterators.py",
    "pynotebook/textmodel/properties.py",
    "pynotebook/textmodel/utils.py",
    "pynotebook/textmodel/weights.py",
    # wxtextview
    "pynotebook/wxtextview/textview.py",
    "pynotebook/wxtextview/wxtextview.py",
    "pynotebook/wxtextview/wxdevice.py",
    "pynotebook/wxtextview/simplelayout.py",
    "pynotebook/wxtextview/linewrap.py",
    "pynotebook/wxtextview/builder.py",
    "pynotebook/wxtextview/boxes.py",
]

failed = sum(test_file(f) for f in files)
print("Total failed:\t%i" % failed)
sys.exit(1 if failed else 0)
