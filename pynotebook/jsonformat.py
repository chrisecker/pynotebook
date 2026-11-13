# -*- coding: utf-8 -*-

# Default file format: the object tree as JSON.
#
# Like cerealizer, objects are stored with their state (__getstate__ or
# __dict__) and restored with __new__ and __setstate__. It is just as
# safe: only registered classes can be created, and JSON cannot carry
# code. Styles are stored once in a table and referenced by index.
# Groups are written as flat arrays and rebalanced on load, weights are
# recomputed: both are internals of the texeltree.
#
#   # pynotebook2
#   {"styles": [{}, {"bold": true}],
#    "model": {"cls": "TextModel",
#              "texel": [{"cls": "Text", "text": "Hi", "style": {"style": 1}},
#                        ...],
#              "ENDMARK": {"cls": "NewLine", ...}}}
#
# JSON arrays are tuples, except in "childs" and in texel positions,
# where they are lists and groups; other lists are {"list": [...]}.
# Values of attributes "style" and "parstyle" that are dicts go to the
# style table.

from .textmodel.textmodel import TextModel
from .textmodel import texeltree
from .textmodel.texeltree import Group, Text, grouped, as_style
from . import nbtexels
from base64 import b64encode, b64decode
import json


magic = '# pynotebook2\n'
style_keys = ('style', 'parstyle')
derived_keys = ('weights',)

_missing = object()
_name2class = {}
_class2name = {}


def register(cls, classname=None):
    """Allows objects of *cls* to be saved and loaded. The first class
    registered under a name wins, as in cerealizer."""
    name = classname or cls.__name__
    if name in _name2class or cls in _class2name:
        return
    _name2class[name] = cls
    _class2name[cls] = name


def get_registered():
    return list(_name2class.items())


def _get_state(obj):
    getstate = getattr(type(obj), '__getstate__', None)
    if getstate is not None and getstate is not object.__getstate__:
        return obj.__getstate__()
    return obj.__dict__


def _flatten(group):
    r = []
    for child in group.childs:
        r.extend(_flatten(child) if child.is_group else [child])
    return r


class _Encoder:
    def __init__(self):
        self.styles = []
        self.style_index = {}

    def encode_style(self, style):
        key = json.dumps(style, sort_keys=True)
        if key not in self.style_index:
            self.style_index[key] = len(self.styles)
            self.styles.append(dict(style))
        return self.style_index[key]

    def encode(self, value, key=None):
        t = type(value)
        if value is None or t in (bool, int, float, str):
            return value
        if t is tuple:
            return [self.encode(x) for x in value]
        if t is list:
            l = [self.encode(x) for x in value]
            return l if key == 'childs' else dict(list=l)
        if t is bytes:
            return dict(bytes=b64encode(value).decode('ascii'))
        if isinstance(value, dict):
            if key in style_keys:
                return dict(style=self.encode_style(value))
            if not all(type(k) is str for k in value):
                raise TypeError('Cannot save dict with non-string keys: %r' % value)
            return dict(dict={k: self.encode(v) for k, v in value.items()})
        if isinstance(value, Group):
            return [self.encode(x) for x in _flatten(value)]
        return self.encode_object(value)

    def encode_object(self, obj):
        name = _class2name.get(type(obj))
        if name is None:
            raise TypeError('Cannot save object of unregistered class %s' %
                            type(obj).__name__)
        state = _get_state(obj)
        r = dict(cls=name)
        if type(state) is dict:
            for k, v in state.items():
                # derived values and class defaults are omitted
                if k not in derived_keys and getattr(type(obj), k, _missing) is not v:
                    r[k] = self.encode(v, k)
        else:
            r['state'] = self.encode(state)
        return r


class _Decoder:
    def __init__(self, styles):
        self.styles = [as_style(s) for s in styles]

    def decode(self, obj, key=None, is_texel=False):
        t = type(obj)
        if t is list:
            if key == 'childs':
                return [self.decode(x, is_texel=True) for x in obj]
            if is_texel:
                return grouped([self.decode(x) for x in obj])
            return tuple(self.decode(x) for x in obj)
        if t is not dict:
            return obj
        if 'cls' in obj:
            return self.decode_object(obj)
        if 'list' in obj:
            return [self.decode(x) for x in obj['list']]
        if 'bytes' in obj:
            return b64decode(obj['bytes'])
        if 'style' in obj:
            return self.styles[obj['style']]
        if 'dict' in obj:
            return {k: self.decode(v) for k, v in obj['dict'].items()}
        raise ValueError('Unknown object: %r' % obj)

    def decode_object(self, obj):
        name = obj['cls']
        cls = _name2class.get(name)
        if cls is None:
            raise ValueError('Unknown class: %r' % name)
        if 'state' in obj:
            state = self.decode(obj['state'])
        else:
            state = {}
            for k, v in obj.items():
                if k == 'cls':
                    continue
                if k.startswith('__'):
                    raise ValueError('Invalid attribute: %r' % k)
                state[k] = self.decode(v, k, is_texel=(k == 'texel'))
        r = cls.__new__(cls)
        if hasattr(cls, '__setstate__'):
            r.__setstate__(state)
        else:
            r.__dict__.update(state)
        if 'childs' in r.__dict__ and hasattr(r, 'compute_weights'):
            r.compute_weights()
        elif isinstance(r, Text):
            r.weights = Text(r.text).weights
        return r


def dumps(model):
    encoder = _Encoder()
    data = encoder.encode(model)
    return magic+json.dumps(dict(styles=encoder.styles, model=data), indent=1)


def loads(s):
    if not s.startswith(magic):
        raise ValueError('Not a pynotebook file: %r' % s[:len(magic)])
    data = json.loads(s[len(magic):])
    return _Decoder(data['styles']).decode(data['model'])


register(texeltree.Group)
register(texeltree.Text)
register(texeltree.Container)
register(texeltree.NewLine)
register(texeltree.Tabulator)
register(TextModel)
register(nbtexels.TextCell)
register(nbtexels.ScriptingCell)
register(nbtexels.BitmapRGB)
register(nbtexels.BitmapRGBA)
register(nbtexels.Graphics)


def test_00():
    "round trip of cells and styles"
    from .textmodel.texeltree import NewLine, G
    bold = as_style(dict(bold=True))
    text = G([Text('Hello', bold), NewLine().set_parstyle(bold), Text('world')])
    model = TextModel()
    model.insert(0, nbtexels.mk_textmodel(nbtexels.TextCell(text)))
    cell = nbtexels.ScriptingCell(Text('print(1)'), Text('1'))
    model.insert(len(model), nbtexels.mk_textmodel(cell))
    s = dumps(model)
    assert s.startswith(magic)
    assert s.count('"bold"') == 1 # styles are stored once
    clone = loads(s)
    assert clone.get_text() == model.get_text()
    for i in range(len(model)):
        assert clone.get_style(i) is model.get_style(i)
        assert clone.get_parstyle(i) is model.get_parstyle(i)
    assert clone.texel.weights == model.texel.weights


def test_01():
    "only registered classes are loaded"
    class Evil: pass
    try:
        dumps(Evil())
        assert False
    except TypeError:
        pass
    for bad in ['{"cls": "os.system"}', '{"cls": "Text", "__class__": 1}']:
        try:
            loads(magic+'{"styles": [], "model": %s}' % bad)
            assert False
        except ValueError:
            pass


def test_02():
    "tuples, lists, bytes and dicts keep their type"
    from .graphics import LineDashes, Line
    enc = _Encoder()
    value = (1, [2, 3], b'\x00\xff', dict(a=(1.5, None)), LineDashes([1, 2]),
             Line((0, 0), (1, 1)))
    clone = _Decoder(enc.styles).decode(enc.encode(value))
    assert clone[:4] == value[:4]
    assert type(clone[1]) is list and type(clone[3]['a']) is tuple
    assert clone[4].__dict__ == value[4].__dict__
    assert clone[5].__dict__ == value[5].__dict__


def test_03():
    "all demo notebooks survive a round trip"
    import glob, wx
    app = wx.App()
    from . import cerealizerformat, graphics
    graphics.register_classes()
    names = glob.glob('pnb/demo/*.pnb')
    assert names
    for name in names:
        model = cerealizerformat.loads(open(name, 'rb').read())
        clone = loads(dumps(model))
        assert clone.get_text() == model.get_text(), name
        assert dumps(clone) == dumps(model), name
