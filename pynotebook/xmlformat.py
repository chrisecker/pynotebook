from .textmodel import texeltree 
from . import nbtexels
from xml.sax.saxutils import escape


# Jupyter versucht es erst gar nicht mit xml: 
# http://nbformat.readthedocs.org/en/latest/format_description.html

# The xml:space Attribute !!!
# http://usingxml.com/Basics/XmlSpace


table = [] # IDEE: Liste von tupeln (Basisklasse, Handler)

def toxml(texel):
    if isinstance(texel, texeltree.Group):
        r = []
        for child in texel.childs:
            r.extend(toxml(child))
        return r
    if isinstance(texel, texeltree.Characters):
        return [escape(texel.get_text())]
    if isinstance(texel, nbtexels.ScriptingCell):
        return ["<Cell>\n", "<input>\n"] + \
            toxml(texel.input) + ["</input>\n", "<output>\n"] + \
            toxml(texel.output) + \
            ["</output>\n", "</Cell>\n"]
    if isinstance(texel, texeltree.NewLine):
        return ['\n']
    print(texel)
    return ["XX"] 
