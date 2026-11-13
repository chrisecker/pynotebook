from runtests import test_file as do


import sys
sys.path.insert(0, '.')

### pynotebook
do("pynotebook/nbtexels.py")
do("pynotebook/graphics.py")
do("pynotebook/wxgraphics.py")
do("pynotebook/nbview.py")
do("pynotebook/pyclient.py")
do("pynotebook/jsonformat.py")
do("pynotebook/inspector.py")
do("pynotebook/cerealizerformat.py")


### textmodel
do("pynotebook/textmodel/texeltree.py")
do("pynotebook/textmodel/styles.py")
do("pynotebook/textmodel/textmodel.py")
do("pynotebook/textmodel/iterators.py")
do("pynotebook/textmodel/properties.py")


### wxtextview
do("pynotebook/wxtextview/textview.py")
do("pynotebook/wxtextview/wxtextview.py")
do("pynotebook/wxtextview/wxdevice.py")
do("pynotebook/wxtextview/simplelayout.py")
do("pynotebook/wxtextview/linewrap.py")
do("pynotebook/wxtextview/builder.py")
do("pynotebook/wxtextview/boxes.py")
