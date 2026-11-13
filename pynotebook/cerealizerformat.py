# -*- coding: utf-8 -*-

# cerealizerformat.py
#
# The former file format, based on cerealizer (a secure form of
# pickling). Kept to load older files; jsonformat is the default. The
# classes are those registered in jsonformat.

from . import nbtexels, jsonformat
from .textmodel import textmodel
from .textmodel import texeltree, styles
from .nbtexels import mk_textmodel

import cerealizer
from io import BytesIO


magic = b'pynotebook0'
cmagic =b'cereal1'

def _register_classes():
    # Classes are registered by their short name (cerealizer's default
    # is module + name), because classes may move to other modules.
    for classname, Class in jsonformat.get_registered():
        try:
            cerealizer.register(Class, None, classname)
        except ValueError: # already registered
            pass


def dumps(obj):
    _register_classes()
    s = BytesIO()
    cerealizer.Dumper().dump(obj, s)
    c = s.getvalue()
    assert c.startswith(cmagic)
    return magic+c[len(cmagic):]


def _replace_styles(texel, table):
    if texel.is_group or texel.is_container:
        for child in texel.childs:
            _replace_styles(child, table)
    else:
        if 'style' in texel.__dict__:
            sid = id(texel.style)
            if not sid in table:
                table[sid] = styles.create_style(**texel.style)
            texel.style = table[sid]
        if isinstance(texel, texeltree.NewLine) and 'parstyle' in texel.__dict__:
            sid = id(texel.parstyle)
            if not sid in table:
                table[sid] = texel.parstyle = styles.create_style(**texel.parstyle)
            texel.parstyle = table[sid]

def loads(s):
    assert s.startswith(magic)
    _register_classes()
    s = cmagic+s[len(magic):]
    
    model =  cerealizer.Dumper().undump(BytesIO(s))
    _replace_styles(model.texel, {})
    return model



def test_00():
    model1 = textmodel.TextModel()
    tmp = textmodel.TextModel(u'for a in range(5):\n    print a')
    cell = nbtexels.ScriptingCell(tmp.texel, texeltree.NULL_TEXEL)
    model1.insert(len(model1), mk_textmodel(cell))

    s = dumps(model1)
    model2 = loads(s)
    assert str(model1.texel) == str(model2.texel)
    assert model1.get_style(5) is model2.get_style(5)
    assert model1.get_parstyle(5) is model2.get_parstyle(5)
